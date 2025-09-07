import { EventBridgeEvent } from 'aws-lambda';
import { SNSClient, PublishCommand } from '@aws-sdk/client-sns';
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, QueryCommand } from '@aws-sdk/lib-dynamodb';

const snsClient = new SNSClient({});
const dynamoClient = new DynamoDBClient({});
const docClient = DynamoDBDocumentClient.from(dynamoClient);

const SNS_TOPIC_ARN = process.env.SNS_TOPIC_ARN || '';
const FARM_ID = process.env.FARM_ID || '2BH';

interface WeatherIngestEvent {
  farm_id: string;
  ts: string;
  metrics: {
    temp: number;
    humidity: number;
    precip24h: number;
  };
}

interface SatIngestEvent {
  farm_id: string;
  timestamp: string;
  metrics: {
    mean: number;
    p10: number;
    p90: number;
  };
}

async function getLastNDVI(farmId: string): Promise<number | null> {
  const twoDaysAgo = new Date();
  twoDaysAgo.setDate(twoDaysAgo.getDate() - 2);
  
  const result = await docClient.send(new QueryCommand({
    TableName: 'readings',
    KeyConditionExpression: 'pk >= :pk AND sk = :sk',
    ExpressionAttributeValues: {
      ':pk': `${farmId}#${twoDaysAgo.toISOString()}`,
      ':sk': 'sat.ndvi.mean'
    },
    ScanIndexForward: false,
    Limit: 1
  }));

  if (result.Items && result.Items.length > 0) {
    return result.Items[0].value;
  }
  return null;
}

async function checkIngestHealth(farmId: string): Promise<boolean> {
  const oneDayAgo = new Date();
  oneDayAgo.setDate(oneDayAgo.getDate() - 1);
  
  const result = await docClient.send(new QueryCommand({
    TableName: 'readings',
    KeyConditionExpression: 'pk >= :pk AND sk = :sk',
    ExpressionAttributeValues: {
      ':pk': `${farmId}#${oneDayAgo.toISOString()}`,
      ':sk': 'weather.temp'
    },
    Limit: 1
  }));

  return result.Items && result.Items.length > 0;
}

async function sendAlert(subject: string, message: string): Promise<void> {
  await snsClient.send(new PublishCommand({
    TopicArn: SNS_TOPIC_ARN,
    Subject: subject,
    Message: message,
    MessageAttributes: {
      farm_id: {
        DataType: 'String',
        StringValue: FARM_ID
      },
      alert_type: {
        DataType: 'String',
        StringValue: 'automated'
      }
    }
  }));
}

export const handler = async (event: EventBridgeEvent<string, any>): Promise<void> => {
  console.log('Processing event:', JSON.stringify(event));

  try {
    switch (event['detail-type']) {
      case 'weather_ingest_complete': {
        const detail: WeatherIngestEvent = event.detail;
        
        // Check for heavy rain alert
        if (detail.metrics.precip24h > 10) {
          await sendAlert(
            `Heavy Rainfall Alert - ${FARM_ID}`,
            `Farm ${FARM_ID} has received ${detail.metrics.precip24h}mm of rain in the last 24 hours.\n\n` +
            `Temperature: ${detail.metrics.temp}°C\n` +
            `Humidity: ${detail.metrics.humidity}%\n\n` +
            `Consider checking for waterlogging and adjusting irrigation schedules.`
          );
        }
        
        // Check for extreme temperatures
        if (detail.metrics.temp > 35) {
          await sendAlert(
            `High Temperature Alert - ${FARM_ID}`,
            `Farm ${FARM_ID} is experiencing high temperatures of ${detail.metrics.temp}°C.\n\n` +
            `Consider increasing irrigation and providing shade for sensitive crops.`
          );
        }
        
        if (detail.metrics.temp < 10) {
          await sendAlert(
            `Low Temperature Alert - ${FARM_ID}`,
            `Farm ${FARM_ID} is experiencing low temperatures of ${detail.metrics.temp}°C.\n\n` +
            `Consider frost protection measures for sensitive crops.`
          );
        }
        break;
      }

      case 'sat_ingest_complete': {
        const detail: SatIngestEvent = event.detail;
        
        // Check for NDVI drop
        const previousNDVI = await getLastNDVI(detail.farm_id);
        if (previousNDVI !== null) {
          const dropPercentage = ((previousNDVI - detail.metrics.mean) / previousNDVI) * 100;
          
          if (dropPercentage > 15) {
            await sendAlert(
              `NDVI Drop Alert - ${FARM_ID}`,
              `Farm ${FARM_ID} has experienced a ${dropPercentage.toFixed(1)}% drop in NDVI.\n\n` +
              `Current NDVI: ${detail.metrics.mean.toFixed(3)}\n` +
              `Previous NDVI: ${previousNDVI.toFixed(3)}\n\n` +
              `This may indicate vegetation stress. Please investigate potential causes.`
            );
          }
        }
        break;
      }

      case 'ingest_health_check': {
        // Scheduled health check
        const isHealthy = await checkIngestHealth(FARM_ID);
        
        if (!isHealthy) {
          await sendAlert(
            `Ingest Health Alert - ${FARM_ID}`,
            `No weather data has been received for farm ${FARM_ID} in the last 24 hours.\n\n` +
            `Please check the weather ingest service and AccuWeather API connectivity.`
          );
        }
        break;
      }

      case 'rain_forecast': {
        // Future enhancement: rain forecast alerts
        const forecast = event.detail;
        if (forecast.expected_precipitation > 10) {
          await sendAlert(
            `Rain Forecast Alert - ${FARM_ID}`,
            `Heavy rain (${forecast.expected_precipitation}mm) is forecast for farm ${FARM_ID} in the next 24 hours.\n\n` +
            `Consider postponing any planned harvesting or fertilizer applications.`
          );
        }
        break;
      }

      default:
        console.log(`Unhandled event type: ${event['detail-type']}`);
    }
  } catch (error) {
    console.error('Error processing alert:', error);
    throw error;
  }
};