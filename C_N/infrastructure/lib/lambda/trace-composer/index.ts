import { DynamoDBClient, GetItemCommand } from '@aws-sdk/client-dynamodb';
import { unmarshall } from '@aws-sdk/util-dynamodb';
import { CloudWatchClient, PutMetricDataCommand } from '@aws-sdk/client-cloudwatch';
import { APIGatewayProxyHandler, APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';
import * as jwt from 'jsonwebtoken';
import AWSXRay from 'aws-xray-sdk-core';

const ddb = AWSXRay.captureAWSv3Client(new DynamoDBClient());
const cw = AWSXRay.captureAWSv3Client(new CloudWatchClient());

interface ProductTrace {
  batchId: string;
  farm: {
    id: string;
    plotId: string;
    name: string;
    location?: {
      lat: number;
      lon: number;
    };
  };
  timeline: Array<{
    t: string; // ISO date
    event: string;
    ndvi?: {
      mean: number;
      tileKey: string;
      cloudPct?: number;
    };
    weather?: {
      temp: number;
      humidity: number;
      precipitation: number;
    };
    anchor?: {
      txHash: string;
      blockNumber: number;
      confirmations: number;
    };
  }>;
  harvest?: {
    date: string;
    weight: number;
    grade: string;
  };
  schemaVer: string;
}

interface FundsTrace {
  contributionId: string;
  investor: {
    id: string;
    type: 'individual' | 'institution';
  };
  contribution: {
    amount: number;
    currency: string;
    date: string;
  };
  allocation: {
    batchId: string;
    percentage: number;
    estimatedYield: number;
  };
  returns?: {
    projected: number;
    actual?: number;
    paidDate?: string;
  };
  schemaVer: string;
}

export const handler: APIGatewayProxyHandler = async (event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> => {
  const correlationId = event.headers['X-Correlation-Id'] || event.requestContext.requestId;
  const startTime = Date.now();
  
  console.log(JSON.stringify({
    level: 'INFO',
    correlationId,
    event: 'trace_composer_request',
    httpMethod: event.httpMethod,
    path: event.path,
    queryParams: event.queryStringParameters
  }));
  
  try {
    // Validate JWT token (simplified for MVP)
    const authHeader = event.headers['Authorization'] || event.headers['authorization'];
    if (!authHeader) {
      return createResponse(401, { error: 'Missing Authorization header' }, correlationId);
    }
    
    const token = authHeader.replace('Bearer ', '');
    
    // For MVP: Simple token validation
    // In production: Full JWT verification with Cognito
    const validTokens = [
      process.env.C_N_VIEWER_TOKEN,
      process.env.C_N_PUBLIC_TOKEN,
      process.env.C_N_API_TOKEN
    ];
    
    if (!validTokens.includes(token)) {
      await emitMetric('UnauthorizedAccess', 1, correlationId);
      return createResponse(401, { error: 'Invalid token' }, correlationId);
    }
    
    // Extract query parameters
    const { batchId, contributionId, format } = event.queryStringParameters || {};
    
    if (!batchId && !contributionId) {
      return createResponse(400, { 
        error: 'Missing required parameter: batchId or contributionId',
        usage: {
          productTrace: '/public/trace/product?batchId=24-0901-FB',
          fundsTrace: '/public/trace/funds?contributionId=INV-2024-001'
        }
      }, correlationId);
    }
    
    let result: any;
    let cacheKey: string;
    
    if (batchId) {
      // Fetch ProductTrace read model
      console.log(JSON.stringify({
        level: 'INFO',
        correlationId,
        event: 'fetching_product_trace',
        batchId
      }));
      
      const productResult = await ddb.send(new GetItemCommand({
        TableName: 'C_N-ReadModel-ProductTrace',
        Key: { batchId: { S: batchId } },
        ConsistentRead: false // Eventual consistency OK for public API
      }));
      
      if (!productResult.Item) {
        await emitMetric('ProductTraceNotFound', 1, correlationId);
        return createResponse(404, { 
          error: 'Product trace not found',
          batchId 
        }, correlationId);
      }
      
      const productTrace = unmarshall(productResult.Item) as ProductTrace;
      
      // Transform for public consumption
      result = {
        type: 'ProductTrace',
        batchId: productTrace.batchId,
        farm: {
          name: productTrace.farm.name,
          plot: productTrace.farm.plotId,
          location: productTrace.farm.location
        },
        journey: productTrace.timeline.map(event => ({
          date: event.t,
          milestone: event.event,
          data: {
            ...(event.ndvi && { 
              vegetation: {
                healthIndex: parseFloat((event.ndvi.mean * 100).toFixed(1)),
                cloudCoverage: event.ndvi.cloudPct,
                satelliteImage: `https://tiles.greenstemglobal.com/${event.ndvi.tileKey}.png`
              }
            }),
            ...(event.weather && {
              conditions: {
                temperature: event.weather.temp,
                humidity: event.weather.humidity,
                rainfall: event.weather.precipitation
              }
            }),
            ...(event.anchor && {
              blockchain: {
                txHash: event.anchor.txHash,
                etherscan: `https://sepolia.etherscan.io/tx/${event.anchor.txHash}`,
                blockNumber: event.anchor.blockNumber,
                confirmations: event.anchor.confirmations
              }
            })
          }
        })),
        harvest: productTrace.harvest,
        metadata: {
          schema: productTrace.schemaVer,
          lastUpdated: new Date().toISOString(),
          traceabilityScore: calculateTraceabilityScore(productTrace)
        }
      };
      
      cacheKey = `product:${batchId}`;
      
    } else if (contributionId) {
      // Fetch FundsTrace read model
      console.log(JSON.stringify({
        level: 'INFO',
        correlationId,
        event: 'fetching_funds_trace',
        contributionId
      }));
      
      const fundsResult = await ddb.send(new GetItemCommand({
        TableName: 'C_N-ReadModel-FundsTrace',
        Key: { contributionId: { S: contributionId } },
        ConsistentRead: false
      }));
      
      if (!fundsResult.Item) {
        await emitMetric('FundsTraceNotFound', 1, correlationId);
        return createResponse(404, { 
          error: 'Contribution trace not found',
          contributionId 
        }, correlationId);
      }
      
      const fundsTrace = unmarshall(fundsResult.Item) as FundsTrace;
      
      // Transform for public consumption (anonymized)
      result = {
        type: 'FundsTrace',
        contributionId: fundsTrace.contributionId,
        investor: {
          type: fundsTrace.investor.type,
          // ID is anonymized in public view
          anonymousId: hashString(fundsTrace.investor.id).substring(0, 8)
        },
        investment: {
          amount: fundsTrace.contribution.amount,
          currency: fundsTrace.contribution.currency,
          date: fundsTrace.contribution.date
        },
        allocation: {
          batchId: fundsTrace.allocation.batchId,
          percentage: fundsTrace.allocation.percentage,
          projectedReturn: fundsTrace.allocation.estimatedYield
        },
        performance: fundsTrace.returns && {
          projected: fundsTrace.returns.projected,
          actual: fundsTrace.returns.actual,
          status: fundsTrace.returns.actual ? 'Completed' : 'In Progress'
        },
        metadata: {
          schema: fundsTrace.schemaVer,
          lastUpdated: new Date().toISOString()
        }
      };
      
      cacheKey = `funds:${contributionId}`;
    }
    
    // Emit success metrics
    const duration = Date.now() - startTime;
    await Promise.all([
      emitMetric('TraceComposerSuccess', 1, correlationId),
      emitMetric('ResponseTime', duration, correlationId, 'Milliseconds'),
      emitMetric('CacheAccess', 1, correlationId, 'Count', cacheKey)
    ]);
    
    console.log(JSON.stringify({
      level: 'INFO',
      correlationId,
      event: 'trace_composer_success',
      traceType: result.type,
      duration,
      cacheKey
    }));
    
    return createResponse(200, result, correlationId, {
      'Cache-Control': 'public, max-age=300', // 5 minute cache
      'X-Trace-Type': result.type,
      'X-Cache-Key': cacheKey
    });
    
  } catch (error) {
    const duration = Date.now() - startTime;
    
    console.log(JSON.stringify({
      level: 'ERROR',
      correlationId,
      event: 'trace_composer_error',
      error: error.message,
      duration
    }));
    
    await Promise.all([
      emitMetric('TraceComposerError', 1, correlationId),
      emitMetric('ErrorResponseTime', duration, correlationId, 'Milliseconds')
    ]);
    
    return createResponse(500, { 
      error: 'Internal server error',
      correlationId,
      timestamp: new Date().toISOString()
    }, correlationId);
  }
};

function createResponse(
  statusCode: number, 
  body: any, 
  correlationId: string, 
  additionalHeaders: Record<string, string> = {}
): APIGatewayProxyResult {
  return {
    statusCode,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
      'X-Correlation-Id': correlationId,
      'X-Powered-By': 'C_N-Trace-Composer',
      ...additionalHeaders
    },
    body: JSON.stringify(body, null, 2)
  };
}

function calculateTraceabilityScore(trace: ProductTrace): number {
  let score = 0;
  
  // Base score for having a trace
  score += 20;
  
  // Score for each timeline event
  score += Math.min(trace.timeline.length * 10, 50);
  
  // Bonus for satellite data
  if (trace.timeline.some(e => e.ndvi)) score += 15;
  
  // Bonus for weather data
  if (trace.timeline.some(e => e.weather)) score += 10;
  
  // Bonus for blockchain anchor
  if (trace.timeline.some(e => e.anchor)) score += 15;
  
  // Bonus for harvest data
  if (trace.harvest) score += 10;
  
  return Math.min(score, 100);
}

function hashString(str: string): string {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32bit integer
  }
  return Math.abs(hash).toString(16);
}

async function emitMetric(
  metricName: string, 
  value: number, 
  correlationId: string, 
  unit: string = 'Count',
  dimension?: string
): Promise<void> {
  try {
    const dimensions = [
      { Name: 'Service', Value: 'TraceComposer' },
      { Name: 'Environment', Value: 'PROD' }
    ];
    
    if (dimension) {
      dimensions.push({ Name: 'CacheKey', Value: dimension });
    }
    
    await cw.send(new PutMetricDataCommand({
      Namespace: 'C_N/PublicAPI',
      MetricData: [{
        MetricName: metricName,
        Value: value,
        Unit: unit,
        Dimensions: dimensions,
        Timestamp: new Date()
      }]
    }));
  } catch (error) {
    console.log(JSON.stringify({
      level: 'WARN',
      correlationId,
      event: 'metric_emit_failed',
      metric: metricName,
      error: error.message
    }));
  }
}