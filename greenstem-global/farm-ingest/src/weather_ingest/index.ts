import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, PutCommand } from '@aws-sdk/lib-dynamodb';
import { SSMClient, GetParameterCommand, PutParameterCommand } from '@aws-sdk/client-ssm';
import { EventBridgeClient, PutEventsCommand } from '@aws-sdk/client-eventbridge';
import axios from 'axios';

const dynamoClient = new DynamoDBClient({});
const docClient = DynamoDBDocumentClient.from(dynamoClient);
const ssmClient = new SSMClient({});
const eventBridgeClient = new EventBridgeClient({});

interface AccuWeatherCurrentConditions {
  Temperature: {
    Metric: { Value: number; Unit: string };
  };
  RelativeHumidity: number;
  PrecipitationSummary?: {
    Past24Hours?: {
      Metric?: { Value: number; Unit: string };
    };
  };
}

async function getOrResolveLocationKey(apiKey: string, lat: string, lon: string): Promise<string> {
  const paramName = 'ACCU_LOCKEY_2BH';
  
  try {
    const result = await ssmClient.send(new GetParameterCommand({ Name: paramName }));
    return result.Parameter!.Value!;
  } catch (error: any) {
    if (error.name === 'ParameterNotFound') {
      console.log('Location key not cached, resolving from AccuWeather...');
      
      const response = await axios.get(
        `http://dataservice.accuweather.com/locations/v1/cities/geoposition/search`,
        {
          params: {
            q: `${lat},${lon}`,
            apikey: apiKey
          }
        }
      );
      
      const locationKey = response.data.Key;
      
      await ssmClient.send(new PutParameterCommand({
        Name: paramName,
        Value: locationKey,
        Type: 'String',
        Description: 'AccuWeather location key for 2BH farm'
      }));
      
      return locationKey;
    }
    throw error;
  }
}

async function fetchCurrentConditions(apiKey: string, locationKey: string): Promise<AccuWeatherCurrentConditions> {
  const response = await axios.get(
    `http://dataservice.accuweather.com/currentconditions/v1/${locationKey}`,
    {
      params: {
        details: true,
        apikey: apiKey
      }
    }
  );
  
  return response.data[0];
}

async function putReading(farmId: string, ts: string, sensor: string, value: number): Promise<void> {
  await docClient.send(new PutCommand({
    TableName: 'readings',
    Item: {
      pk: `${farmId}#${ts}`,
      sk: sensor,
      farm_id: farmId,
      timestamp: ts,
      sensor,
      value,
      unit: sensor === 'weather.temp' ? '°C' : sensor === 'weather.humidity' ? '%' : 'mm',
      created_at: new Date().toISOString()
    }
  }));
}

async function putEventBridge(eventType: string, detail: any): Promise<void> {
  await eventBridgeClient.send(new PutEventsCommand({
    Entries: [
      {
        Source: 'farm-ingest.weather',
        DetailType: eventType,
        Detail: JSON.stringify(detail),
        EventBusName: 'default'
      }
    ]
  }));
}

export const handler = async (): Promise<void> => {
  const { ACCUWEATHER_API_KEY, FARM_LAT, FARM_LON, FARM_ID = '2BH' } = process.env;
  
  if (!ACCUWEATHER_API_KEY || !FARM_LAT || !FARM_LON) {
    throw new Error('Missing required environment variables');
  }
  
  try {
    const locationKey = await getOrResolveLocationKey(ACCUWEATHER_API_KEY, FARM_LAT, FARM_LON);
    const conditions = await fetchCurrentConditions(ACCUWEATHER_API_KEY, locationKey);
    const ts = new Date().toISOString();
    
    await Promise.all([
      putReading(FARM_ID, ts, 'weather.temp', conditions.Temperature.Metric.Value),
      putReading(FARM_ID, ts, 'weather.humidity', conditions.RelativeHumidity),
      putReading(FARM_ID, ts, 'weather.precip24h', 
        conditions.PrecipitationSummary?.Past24Hours?.Metric?.Value ?? 0)
    ]);
    
    await putEventBridge('weather_ingest_complete', { 
      farm_id: FARM_ID, 
      ts,
      metrics: {
        temp: conditions.Temperature.Metric.Value,
        humidity: conditions.RelativeHumidity,
        precip24h: conditions.PrecipitationSummary?.Past24Hours?.Metric?.Value ?? 0
      }
    });
    
    console.log(`Weather data ingested successfully for ${FARM_ID} at ${ts}`);
  } catch (error) {
    console.error('Error ingesting weather data:', error);
    throw error;
  }
};