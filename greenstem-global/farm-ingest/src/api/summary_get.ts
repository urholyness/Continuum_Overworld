import { APIGatewayProxyHandler } from 'aws-lambda';
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, QueryCommand } from '@aws-sdk/lib-dynamodb';

const dynamoClient = new DynamoDBClient({});
const docClient = DynamoDBDocumentClient.from(dynamoClient);

const FARM_POLYGON_GEOJSON = process.env.FARM_POLYGON_GEOJSON || JSON.stringify({
  "type": "Feature",
  "properties": {"farm_id":"2BH","name":"Two Butterflies Homestead"},
  "geometry": {
    "type": "Polygon",
    "coordinates": [[
      [35.2648,-0.5193],[35.2748,-0.5193],
      [35.2748,-0.5093],[35.2648,-0.5093],
      [35.2648,-0.5193]
    ]]
  }
});

async function getLastReading(farmId: string, sensor: string): Promise<any> {
  const result = await docClient.send(new QueryCommand({
    TableName: 'readings',
    KeyConditionExpression: 'pk >= :pk AND sk = :sk',
    ExpressionAttributeValues: {
      ':pk': `${farmId}#`,
      ':sk': sensor
    },
    ScanIndexForward: false,
    Limit: 1
  }));

  if (result.Items && result.Items.length > 0) {
    return {
      value: result.Items[0].value,
      timestamp: result.Items[0].timestamp,
      unit: result.Items[0].unit
    };
  }
  return null;
}

async function getLastOpsEvent(farmId: string): Promise<any> {
  const result = await docClient.send(new QueryCommand({
    TableName: 'ops_events',
    KeyConditionExpression: 'pk >= :pk',
    ExpressionAttributeValues: {
      ':pk': `${farmId}#`
    },
    ScanIndexForward: false,
    Limit: 1
  }));

  if (result.Items && result.Items.length > 0) {
    return {
      event_id: result.Items[0].event_id,
      type: result.Items[0].type,
      note: result.Items[0].note,
      timestamp: result.Items[0].created_at
    };
  }
  return null;
}

function estimateHarvestEta(): string {
  // Simple calculation: next harvest in 90 days from now
  const harvestDate = new Date();
  harvestDate.setDate(harvestDate.getDate() + 90);
  return harvestDate.toISOString().split('T')[0];
}

export const handler: APIGatewayProxyHandler = async (event) => {
  try {
    const farmId = event.pathParameters?.farmId || '2BH';

    // Fetch latest data in parallel
    const [lastNdvi, lastWeather, lastOps] = await Promise.all([
      getLastReading(farmId, 'sat.ndvi.mean'),
      getLastReading(farmId, 'weather.temp'),
      getLastOpsEvent(farmId)
    ]);

    const summary = {
      id: farmId,
      name: 'Two Butterflies Homestead',
      location: 'Eldoret, Kenya',
      coords: JSON.parse(FARM_POLYGON_GEOJSON),
      last_ndvi: lastNdvi,
      last_weather: {
        temperature: lastWeather
      },
      next_harvest_eta: estimateHarvestEta(),
      last_ops_event: lastOps,
      freshness: {
        weather_ts: lastWeather?.timestamp,
        sat_ts: lastNdvi?.timestamp,
        ops_ts: lastOps?.timestamp
      }
    };

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Cache-Control': 'max-age=60'
      },
      body: JSON.stringify(summary)
    };

  } catch (error) {
    console.error('Error fetching farm summary:', error);
    return {
      statusCode: 500,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: JSON.stringify({ error: 'Internal server error' })
    };
  }
};