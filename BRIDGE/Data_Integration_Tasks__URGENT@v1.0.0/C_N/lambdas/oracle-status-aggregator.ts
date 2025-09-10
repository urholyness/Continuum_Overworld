// File: C_N/lambdas/oracle-status-aggregator.ts
// Task 2: Lambda function for Oracle Status Aggregation

import { DynamoDBClient, QueryCommand } from '@aws-sdk/client-dynamodb';
import { APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';

const ddb = new DynamoDBClient({
  region: process.env.AWS_REGION || 'eu-central-1'
});

interface OracleStatus {
  satellite: {
    lastHourCount: number;
    estimatedCost: number;
    status: 'online' | 'offline' | 'degraded';
    lastUpdate?: string;
  };
  weather: {
    last24HourCount: number;
    estimatedCost: number;
    status: 'online' | 'offline' | 'degraded';
    lastUpdate?: string;
  };
  blockchain: {
    lastHourCount: number;
    gasUsed: number;
    estimatedCost: number;
    status: 'online' | 'offline' | 'degraded';
  };
  totalDailyCost: number;
  timestamp: string;
}

export const handler = async (
  event: APIGatewayProxyEvent
): Promise<APIGatewayProxyResult> => {
  try {
    const now = Date.now();
    const hourAgo = now - 3600000;
    const dayAgo = now - 86400000;
    
    // Query satellite oracle data
    const satelliteQuery = await ddb.send(new QueryCommand({
      TableName: 'C_N-Oracle-SatelliteData',
      IndexName: 'TimestampIndex',
      KeyConditionExpression: 'GSI1PK = :pk AND #ts > :hourAgo',
      ExpressionAttributeNames: { 
        '#ts': 'timestamp' 
      },
      ExpressionAttributeValues: {
        ':pk': { S: 'SATELLITE' },
        ':hourAgo': { N: String(hourAgo) }
      },
      Select: 'COUNT',
      ScanIndexForward: false,
      Limit: 100
    }));
    
    // Query weather oracle data
    const weatherQuery = await ddb.send(new QueryCommand({
      TableName: 'C_N-Oracle-WeatherData',
      IndexName: 'TimestampIndex',
      KeyConditionExpression: 'GSI1PK = :pk AND #ts > :dayAgo',
      ExpressionAttributeNames: { 
        '#ts': 'timestamp' 
      },
      ExpressionAttributeValues: {
        ':pk': { S: 'WEATHER' },
        ':dayAgo': { N: String(dayAgo) }
      },
      Select: 'COUNT',
      ScanIndexForward: false,
      Limit: 500
    }));
    
    // Query blockchain transactions
    const blockchainQuery = await ddb.send(new QueryCommand({
      TableName: 'C_N-Events-Trace',
      IndexName: 'TypeIndex',
      KeyConditionExpression: '#type = :type AND #ts > :hourAgo',
      ExpressionAttributeNames: { 
        '#type': 'type',
        '#ts': 'timestamp' 
      },
      ExpressionAttributeValues: {
        ':type': { S: 'blockchain_tx' },
        ':hourAgo': { N: String(hourAgo) }
      },
      Select: 'COUNT'
    }));
    
    // Calculate costs based on actual usage
    const satelliteCost = (satelliteQuery.Count || 0) * 0.15; // $0.15 per satellite image
    const weatherCost = (weatherQuery.Count || 0) * 0.01; // $0.01 per weather API call
    const blockchainCost = (blockchainQuery.Count || 0) * 0.05; // $0.05 per blockchain tx
    
    // Determine service status based on activity
    const getStatus = (count: number, threshold: number = 1): 'online' | 'offline' | 'degraded' => {
      if (count === 0) return 'offline';
      if (count < threshold) return 'degraded';
      return 'online';
    };
    
    const response: OracleStatus = {
      satellite: {
        lastHourCount: satelliteQuery.Count || 0,
        estimatedCost: satelliteCost,
        status: getStatus(satelliteQuery.Count || 0),
        lastUpdate: satelliteQuery.LastEvaluatedKey ? 
          new Date(parseInt(satelliteQuery.LastEvaluatedKey.timestamp.N!)).toISOString() : 
          undefined
      },
      weather: {
        last24HourCount: weatherQuery.Count || 0,
        estimatedCost: weatherCost,
        status: getStatus(weatherQuery.Count || 0, 10),
        lastUpdate: weatherQuery.LastEvaluatedKey ? 
          new Date(parseInt(weatherQuery.LastEvaluatedKey.timestamp.N!)).toISOString() : 
          undefined
      },
      blockchain: {
        lastHourCount: blockchainQuery.Count || 0,
        gasUsed: (blockchainQuery.Count || 0) * 21000, // Estimated gas per tx
        estimatedCost: blockchainCost,
        status: getStatus(blockchainQuery.Count || 0)
      },
      totalDailyCost: (satelliteCost + weatherCost + blockchainCost) * 24,
      timestamp: new Date().toISOString()
    };
    
    // Log metrics for CloudWatch
    console.log(JSON.stringify({
      metricType: 'OracleStatus',
      satellite: response.satellite,
      weather: response.weather,
      blockchain: response.blockchain,
      totalCost: response.totalDailyCost
    }));
    
    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'max-age=60'
      },
      body: JSON.stringify(response)
    };
  } catch (error) {
    console.error('Oracle status aggregation failed:', error);
    
    return {
      statusCode: 500,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        error: 'Failed to aggregate oracle status',
        message: error instanceof Error ? error.message : 'Unknown error'
      })
    };
  }
};
