import { APIGatewayProxyHandler } from 'aws-lambda';
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, QueryCommand } from '@aws-sdk/lib-dynamodb';

const dynamoClient = new DynamoDBClient({});
const docClient = DynamoDBDocumentClient.from(dynamoClient);

export const handler: APIGatewayProxyHandler = async (event) => {
  try {
    const farmId = event.pathParameters?.farmId || '2BH';
    const limit = parseInt(event.queryStringParameters?.limit || '50');

    // Query ops events for the farm
    const result = await docClient.send(new QueryCommand({
      TableName: 'ops_events',
      KeyConditionExpression: 'pk >= :pk',
      ExpressionAttributeValues: {
        ':pk': `${farmId}#`
      },
      ScanIndexForward: false, // Sort by newest first
      Limit: limit
    }));

    const events = result.Items?.map(item => ({
      event_id: item.event_id,
      type: item.type,
      note: item.note,
      media_urls: item.media_urls || [],
      created_at: item.created_at,
      created_by: item.created_by
    })) || [];

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: JSON.stringify({
        farm_id: farmId,
        events,
        count: events.length,
        has_more: !!result.LastEvaluatedKey
      })
    };

  } catch (error) {
    console.error('Error fetching ops events:', error);
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