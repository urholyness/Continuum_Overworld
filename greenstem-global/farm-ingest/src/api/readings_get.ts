import { APIGatewayProxyHandler } from 'aws-lambda';
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, QueryCommand } from '@aws-sdk/lib-dynamodb';

const dynamoClient = new DynamoDBClient({});
const docClient = DynamoDBDocumentClient.from(dynamoClient);

export const handler: APIGatewayProxyHandler = async (event) => {
  try {
    const farmId = event.pathParameters?.farmId || '2BH';
    const since = event.queryStringParameters?.since;
    const limit = parseInt(event.queryStringParameters?.limit || '100');
    const sensor = event.queryStringParameters?.sensor;

    let queryParams: any = {
      TableName: 'readings',
      Limit: limit,
      ScanIndexForward: false // Most recent first
    };

    if (since) {
      // Query readings since a specific timestamp
      queryParams.KeyConditionExpression = 'pk >= :pk';
      queryParams.ExpressionAttributeValues = {
        ':pk': `${farmId}#${since}`
      };
    } else {
      // Query all readings for the farm
      queryParams.KeyConditionExpression = 'pk >= :pk';
      queryParams.ExpressionAttributeValues = {
        ':pk': `${farmId}#`
      };
    }

    // Add sensor filter if specified
    if (sensor) {
      queryParams.KeyConditionExpression += ' AND sk = :sk';
      queryParams.ExpressionAttributeValues[':sk'] = sensor;
    }

    const result = await docClient.send(new QueryCommand(queryParams));

    const readings = result.Items?.map(item => ({
      timestamp: item.timestamp,
      sensor: item.sensor,
      value: item.value,
      unit: item.unit
    })) || [];

    // Group readings by timestamp for easier consumption
    const groupedReadings = readings.reduce((acc: any, reading) => {
      if (!acc[reading.timestamp]) {
        acc[reading.timestamp] = {
          timestamp: reading.timestamp,
          sensors: {}
        };
      }
      acc[reading.timestamp].sensors[reading.sensor] = {
        value: reading.value,
        unit: reading.unit
      };
      return acc;
    }, {});

    const response = {
      farm_id: farmId,
      readings: Object.values(groupedReadings),
      count: readings.length,
      has_more: !!result.LastEvaluatedKey
    };

    if (result.LastEvaluatedKey) {
      response['next_key'] = Buffer.from(JSON.stringify(result.LastEvaluatedKey)).toString('base64');
    }

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Cache-Control': 'max-age=30'
      },
      body: JSON.stringify(response)
    };

  } catch (error) {
    console.error('Error fetching readings:', error);
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