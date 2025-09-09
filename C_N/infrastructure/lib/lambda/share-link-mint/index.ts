import { APIGatewayProxyHandler, APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';
import { CloudWatchClient, PutMetricDataCommand } from '@aws-sdk/client-cloudwatch';
import * as jwt from 'jsonwebtoken';
import * as crypto from 'crypto';
import AWSXRay from 'aws-xray-sdk-core';

const cw = AWSXRay.captureAWSv3Client(new CloudWatchClient());

interface ShareLinkRequest {
  resource: 'product' | 'funds';
  id: string;
  ttlHours?: number;
  description?: string;
}

interface ShareLinkResponse {
  shareLink: string;
  qrCode: string;
  expiresAt: string;
  expiresIn: string;
  metadata: {
    resource: string;
    id: string;
    created: string;
    tokenId: string;
  };
}

export const handler: APIGatewayProxyHandler = async (event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> => {
  const correlationId = event.headers['X-Correlation-Id'] || event.requestContext.requestId;
  
  console.log(JSON.stringify({
    level: 'INFO',
    correlationId,
    event: 'share_link_mint_request',
    httpMethod: event.httpMethod,
    userAgent: event.headers['User-Agent']
  }));
  
  try {
    if (event.httpMethod !== 'POST') {
      return createResponse(405, { error: 'Method not allowed' }, correlationId);
    }
    
    if (!event.body) {
      return createResponse(400, { 
        error: 'Missing request body',
        expectedFormat: {
          resource: 'product | funds',
          id: 'string',
          ttlHours: 24,
          description: 'optional'
        }
      }, correlationId);
    }
    
    const request: ShareLinkRequest = JSON.parse(event.body);
    
    // Validate request
    if (!request.resource || !request.id) {
      return createResponse(400, { 
        error: 'Missing required fields: resource, id' 
      }, correlationId);
    }
    
    if (!['product', 'funds'].includes(request.resource)) {
      return createResponse(400, { 
        error: 'Invalid resource type. Must be "product" or "funds"' 
      }, correlationId);
    }
    
    const ttlHours = Math.min(request.ttlHours || 24, 168); // Max 7 days
    const expiresAt = new Date(Date.now() + (ttlHours * 60 * 60 * 1000));
    const tokenId = crypto.randomBytes(8).toString('hex');
    
    // Create JWT token with share permissions
    const jwtSecret = process.env.JWT_SECRET;
    if (!jwtSecret) {
      throw new Error('JWT_SECRET not configured');
    }
    
    const tokenPayload = {
      iss: 'C_N-Share-Link-Mint',
      aud: 'greenstemglobal.com',
      sub: `${request.resource}:${request.id}`,
      scope: `public:read:${request.resource}`,
      resource: request.resource,
      id: request.id,
      tokenId,
      description: request.description,
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(expiresAt.getTime() / 1000)
    };
    
    const shareToken = jwt.sign(tokenPayload, jwtSecret, { 
      algorithm: 'HS256',
      header: { typ: 'JWT', alg: 'HS256' }
    });
    
    // Generate share link
    const baseUrl = process.env.SHARE_BASE_URL || 'https://greenstemglobal.com';
    const shareLink = `${baseUrl}/trace?token=${shareToken}`;
    
    // Generate QR code URL
    const qrCode = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(shareLink)}`;
    
    const response: ShareLinkResponse = {
      shareLink,
      qrCode,
      expiresAt: expiresAt.toISOString(),
      expiresIn: `${ttlHours}h`,
      metadata: {
        resource: request.resource,
        id: request.id,
        created: new Date().toISOString(),
        tokenId
      }
    };
    
    // Emit metrics
    await Promise.all([
      emitMetric('ShareLinkCreated', 1, correlationId, 'Count', request.resource),
      emitMetric('ShareLinkTTL', ttlHours, correlationId, 'Count', request.resource)
    ]);
    
    console.log(JSON.stringify({
      level: 'INFO',
      correlationId,
      event: 'share_link_mint_success',
      resource: request.resource,
      id: request.id,
      tokenId,
      ttlHours,
      expiresAt: expiresAt.toISOString()
    }));
    
    return createResponse(201, response, correlationId, {
      'Cache-Control': 'no-store, no-cache, must-revalidate',
      'X-Token-ID': tokenId
    });
    
  } catch (error) {
    console.log(JSON.stringify({
      level: 'ERROR',
      correlationId,
      event: 'share_link_mint_error',
      error: error.message,
      stack: error.stack?.split('\n')[0]
    }));
    
    await emitMetric('ShareLinkMintError', 1, correlationId, 'Count', 'ERROR');
    
    return createResponse(500, {
      error: 'Internal server error',
      correlationId
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
      'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Correlation-Id',
      'X-Correlation-Id': correlationId,
      'X-Service': 'C_N-Share-Link-Mint',
      ...additionalHeaders
    },
    body: JSON.stringify(body, null, 2)
  };
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
      { Name: 'Service', Value: 'ShareLinkMint' },
      { Name: 'Environment', Value: 'PROD' }
    ];
    
    if (dimension) {
      dimensions.push({ Name: 'ResourceType', Value: dimension });
    }
    
    await cw.send(new PutMetricDataCommand({
      Namespace: 'C_N/PublicAPI',
      MetricData: [{
        MetricName: metricName,
        Value: value,
        Unit: unit,
        Dimensions: dimensions
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