import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, ScanCommand } from "@aws-sdk/lib-dynamodb";

export const runtime = 'nodejs';

const client = new DynamoDBClient({ 
  region: process.env.AWS_REGION || 'eu-central-1' 
});
const ddb = DynamoDBDocumentClient.from(client);

export async function GET() {
  try {
    // Use environment variable with fallback to deployed table
    const tableName = process.env.DDB_METRICS_TABLE || 'C_N-FarmMetrics-Live-PROD';
    const command = new ScanCommand({
      TableName: tableName,
      FilterExpression: 'attribute_exists(farmId)',
      Limit: 20
    });

    const result = await ddb.send(command);
    
    // Transform DynamoDB data to lots format
    const lots = (result.Items || []).map(item => ({
      id: item.farmId,
      name: item.name || item.farmId,
      location: item.location || 'Kenya',
      coordinates: {
        lat: item.latitude || 0,
        lng: item.longitude || 0
      },
      crop: item.cropType || 'Unknown',
      variety: item.variety || 'Unknown',
      grade: item.grade || 'Standard',
      metrics: {
        temperature: item.temperature || null,
        humidity: item.humidity || null,
        ndvi: item.ndvi || null,
        soilMoisture: item.soilMoisture || null
      },
      lastUpdate: new Date(item.timestamp || Date.now()).toISOString(),
      status: 'active'
    }));

    return Response.json({
      success: true,
      data: lots,
      count: lots.length,
      source: 'DynamoDB'
    });

  } catch (error) {
    console.error('DynamoDB error:', error);
    
    // Fallback to mock data if DynamoDB fails
    const sample = await import("@/../mocks/lots_sample.json");
    return Response.json({
      success: false,
      data: sample.default,
      error: 'Using fallback data',
      source: 'Mock'
    });
  }
}