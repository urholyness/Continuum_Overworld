import { APIGatewayProxyHandler } from 'aws-lambda';
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, PutCommand } from '@aws-sdk/lib-dynamodb';
import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3';
import { randomUUID } from 'crypto';

const dynamoClient = new DynamoDBClient({});
const docClient = DynamoDBDocumentClient.from(dynamoClient);
const s3Client = new S3Client({});

const S3_BUCKET = process.env.S3_BUCKET || 'gsg-web-assets';
const FARM_ID = process.env.FARM_ID || '2BH';

interface OpsEventRequest {
  type: string;
  note: string;
  media_base64?: string[];
}

export const handler: APIGatewayProxyHandler = async (event) => {
  try {
    // Check authentication
    const authHeader = event.headers.Authorization || event.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return {
        statusCode: 401,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        },
        body: JSON.stringify({ error: 'Unauthorized' })
      };
    }

    // Parse request body
    const body: OpsEventRequest = JSON.parse(event.body || '{}');
    
    if (!body.type || !body.note) {
      return {
        statusCode: 400,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        },
        body: JSON.stringify({ error: 'Missing required fields: type, note' })
      };
    }

    const timestamp = new Date().toISOString();
    const eventId = randomUUID();
    const mediaUrls: string[] = [];

    // Upload media files if provided
    if (body.media_base64 && body.media_base64.length > 0) {
      for (let i = 0; i < body.media_base64.length; i++) {
        const mediaData = body.media_base64[i];
        const matches = mediaData.match(/^data:([A-Za-z-+\/]+);base64,(.+)$/);
        
        if (!matches || matches.length !== 3) {
          continue;
        }

        const contentType = matches[1];
        const base64Data = matches[2];
        const buffer = Buffer.from(base64Data, 'base64');
        
        const extension = contentType.split('/')[1] || 'jpg';
        const fileName = `${timestamp.replace(/[:.]/g, '-')}-${randomUUID()}.${extension}`;
        const key = `ops/${FARM_ID}/${fileName}`;

        await s3Client.send(new PutObjectCommand({
          Bucket: S3_BUCKET,
          Key: key,
          Body: buffer,
          ContentType: contentType,
          Metadata: {
            farm_id: FARM_ID,
            event_id: eventId,
            uploaded_at: timestamp
          }
        }));

        mediaUrls.push(`https://${S3_BUCKET}.s3.amazonaws.com/${key}`);
      }
    }

    // Save to DynamoDB
    await docClient.send(new PutCommand({
      TableName: 'ops_events',
      Item: {
        pk: `${FARM_ID}#${timestamp}`,
        sk: eventId,
        farm_id: FARM_ID,
        event_id: eventId,
        type: body.type,
        note: body.note,
        media_urls: mediaUrls,
        created_at: timestamp,
        created_by: 'admin' // Would normally extract from JWT
      }
    }));

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: JSON.stringify({
        ok: true,
        event_id: eventId,
        timestamp,
        media_urls: mediaUrls
      })
    };

  } catch (error) {
    console.error('Error creating ops event:', error);
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