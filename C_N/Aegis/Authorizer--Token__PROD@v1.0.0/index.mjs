import { CloudWatchClient, PutMetricDataCommand } from '@aws-sdk/client-cloudwatch';
import AWSXRay from 'aws-xray-sdk-core';

const cw = AWSXRay.captureAWSv3Client(new CloudWatchClient());

// Cache for authorization decisions (per container)
const authCache = new Map();
const CACHE_TTL = 300000; // 5 minutes

export const handler = async (event) => {
  const token = event.authorizationToken;
  const methodArn = event.methodArn;
  
  console.log(JSON.stringify({
    level: 'INFO',
    event: 'authorization_request',
    methodArn,
    hasToken: !!token,
    timestamp: new Date().toISOString()
  }));
  
  try {
    // Check cache first
    const cacheKey = `${token}:${methodArn}`;
    const cached = authCache.get(cacheKey);
    if (cached && (Date.now() - cached.timestamp) < CACHE_TTL) {
      console.log(JSON.stringify({
        level: 'INFO',
        event: 'auth_cache_hit',
        principalId: cached.policy.principalId
      }));
      
      await emitMetric('AuthCacheHit', 1);
      return cached.policy;
    }
    
    // Validate token
    const authResult = await validateToken(token, methodArn);
    
    // Cache the result
    authCache.set(cacheKey, {
      policy: authResult,
      timestamp: Date.now()
    });
    
    // Clean old cache entries
    if (authCache.size > 1000) {
      const cutoff = Date.now() - CACHE_TTL;
      for (const [key, value] of authCache.entries()) {
        if (value.timestamp < cutoff) {
          authCache.delete(key);
        }
      }
    }
    
    await emitMetric('AuthCacheMiss', 1);
    await emitMetric('AuthSuccess', 1);
    
    console.log(JSON.stringify({
      level: 'INFO',
      event: 'authorization_success',
      principalId: authResult.principalId,
      division: authResult.context?.division
    }));
    
    return authResult;
    
  } catch (error) {
    console.log(JSON.stringify({
      level: 'ERROR',
      event: 'authorization_error',
      error: error.message,
      methodArn
    }));
    
    await emitMetric('AuthFailure', 1);
    
    throw new Error('Unauthorized'); // This triggers 401 response
  }
};

async function validateToken(token, methodArn) {
  // MVP: Simple token validation
  // Phase 2: Upgrade to JWT/Cognito
  
  if (!token) {
    throw new Error('No token provided');
  }
  
  // Remove "Bearer " prefix if present
  const cleanToken = token.replace(/^Bearer\s+/, '');
  
  // Validate against environment variable
  const validTokens = {
    [process.env.C_N_API_TOKEN]: {
      division: 'Core',
      permissions: ['*']
    },
    [process.env.C_N_ORACLE_TOKEN]: {
      division: 'Oracle',
      permissions: ['oracle:*', 'ledger:read']
    },
    [process.env.C_N_HELIOS_TOKEN]: {
      division: 'Helios',
      permissions: ['dashboard:*', 'metrics:read']
    }
  };
  
  const tokenData = validTokens[cleanToken];
  if (!tokenData) {
    throw new Error('Invalid token');
  }
  
  // Generate policy based on token type
  const policy = generatePolicy(tokenData, methodArn);
  
  return policy;
}

function generatePolicy(tokenData, methodArn) {
  // Extract region, account, API ID from methodArn
  // arn:aws:execute-api:region:account:apiId/stage/method/resource
  const arnParts = methodArn.split(':');
  const region = arnParts[3];
  const account = arnParts[4];
  const [apiId, stage] = arnParts[5].split('/');
  
  // Build resource ARN for all methods
  const resourceArn = `arn:aws:execute-api:${region}:${account}:${apiId}/${stage}/*/*`;
  
  return {
    principalId: `user-${tokenData.division.toLowerCase()}`,
    policyDocument: {
      Version: '2012-10-17',
      Statement: [{
        Action: 'execute-api:Invoke',
        Effect: 'Allow',
        Resource: resourceArn
      }]
    },
    context: {
      division: tokenData.division,
      permissions: tokenData.permissions.join(','),
      tokenType: 'static', // Will be 'jwt' in Phase 2
      timestamp: new Date().toISOString()
    }
  };
}

async function emitMetric(metricName, value) {
  try {
    await cw.send(new PutMetricDataCommand({
      Namespace: 'C_N/Aegis',
      MetricData: [{
        MetricName: metricName,
        Value: value,
        Unit: 'Count',
        Dimensions: [
          { Name: 'Environment', Value: 'PROD' },
          { Name: 'AuthorizerType', Value: 'Token' }
        ]
      }]
    }));
  } catch (error) {
    console.log(JSON.stringify({
      level: 'WARN',
      event: 'metric_emit_failed',
      metric: metricName,
      error: error.message
    }));
  }
}