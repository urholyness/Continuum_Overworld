import { CloudWatchClient, PutMetricDataCommand } from '@aws-sdk/client-cloudwatch';
import AWSXRay from 'aws-xray-sdk-core';

const cw = AWSXRay.captureAWSv3Client(new CloudWatchClient());

// In-memory cache (per container)
const cache = new Map();
let cacheHits = 0;
let cacheMisses = 0;
let startTime = Date.now();

const ALLOWED_PROVIDERS = ['openai', 'anthropic', 'cohere', 'together'];
const COST_CAPS = { 
  'gpt-4': 100, 
  'gpt-4o': 120,
  'claude-3-5-sonnet': 80,
  'claude-3-haiku': 40, 
  'command': 50,
  'llama-2-70b': 30
};

export const handler = async (event) => {
  const correlationId = event.headers?.['X-Correlation-Id'] || crypto.randomUUID();
  const causationId = event.headers?.['X-Causation-Id'] || correlationId;
  
  console.log(JSON.stringify({
    level: 'INFO',
    correlationId,
    causationId,
    event: 'mcp_request',
    httpMethod: event.httpMethod,
    path: event.path
  }));
  
  try {
    // Handle health check
    if (event.httpMethod === 'GET' && event.path === '/health') {
      const uptime = Math.floor((Date.now() - startTime) / 1000);
      return {
        statusCode: 200,
        body: JSON.stringify({
          status: 'healthy',
          uptime,
          cacheStats: {
            size: cache.size,
            hits: cacheHits,
            misses: cacheMisses,
            hitRate: cacheHits / (cacheHits + cacheMisses) || 0
          },
          timestamp: new Date().toISOString()
        }),
        headers: {
          'Content-Type': 'application/json',
          'X-Correlation-Id': correlationId
        }
      };
    }
    
    // Parse request
    const { provider, model, prompt, temperature, maxTokens } = JSON.parse(event.body || '{}');
    
    if (!provider || !model || !prompt) {
      return {
        statusCode: 400,
        body: JSON.stringify({
          error: 'Missing required parameters: provider, model, prompt'
        }),
        headers: {
          'Content-Type': 'application/json',
          'X-Correlation-Id': correlationId
        }
      };
    }
    
    // Check allowlist
    if (!ALLOWED_PROVIDERS.includes(provider)) {
      console.log(JSON.stringify({
        level: 'WARN',
        correlationId,
        event: 'provider_blocked',
        provider,
        allowedProviders: ALLOWED_PROVIDERS
      }));
      
      return { 
        statusCode: 403, 
        body: JSON.stringify({
          error: `Provider '${provider}' not allowed`,
          allowedProviders: ALLOWED_PROVIDERS
        }),
        headers: {
          'Content-Type': 'application/json',
          'X-Correlation-Id': correlationId
        }
      };
    }
    
    // Check cost cap
    const costCap = COST_CAPS[model];
    if (costCap && maxTokens > costCap * 1000) {  // Rough token limit
      return {
        statusCode: 429,
        body: JSON.stringify({
          error: `Token limit exceeded for model '${model}'. Max: ${costCap * 1000}`
        }),
        headers: {
          'Content-Type': 'application/json',
          'X-Correlation-Id': correlationId
        }
      };
    }
    
    // Check cache
    const cacheKey = `${provider}:${model}:${hashString(prompt)}:${temperature}:${maxTokens}`;
    if (cache.has(cacheKey)) {
      cacheHits++;
      const cachedResponse = cache.get(cacheKey);
      
      console.log(JSON.stringify({
        level: 'INFO',
        correlationId,
        event: 'cache_hit',
        cacheKey: cacheKey.substring(0, 50) + '...'
      }));
      
      await emitCacheMetrics();
      
      return {
        statusCode: 200,
        body: JSON.stringify({
          ...cachedResponse,
          cached: true,
          timestamp: new Date().toISOString()
        }),
        headers: { 
          'Content-Type': 'application/json',
          'X-Cache': 'HIT',
          'X-Correlation-Id': correlationId 
        }
      };
    }
    
    cacheMisses++;
    
    console.log(JSON.stringify({
      level: 'INFO',
      correlationId,
      event: 'cache_miss',
      provider,
      model,
      promptLength: prompt.length
    }));
    
    // Route to provider (MVP implementation with mock response)
    const response = await routeToProvider(provider, model, prompt, temperature, maxTokens, correlationId);
    
    // Cache the response (TTL: 1 hour)
    cache.set(cacheKey, response);
    if (cache.size > 1000) {  // LRU eviction
      const firstKey = cache.keys().next().value;
      cache.delete(firstKey);
    }
    
    await emitCacheMetrics();
    
    return {
      statusCode: 200,
      body: JSON.stringify({
        ...response,
        cached: false,
        timestamp: new Date().toISOString()
      }),
      headers: { 
        'Content-Type': 'application/json',
        'X-Cache': 'MISS',
        'X-Correlation-Id': correlationId,
        'X-Causation-Id': causationId
      }
    };
    
  } catch (error) {
    console.log(JSON.stringify({
      level: 'ERROR',
      correlationId,
      causationId,
      error: error.message,
      stack: error.stack?.split('\n')[0]
    }));
    
    return {
      statusCode: 500,
      body: JSON.stringify({ 
        error: 'Internal server error',
        correlationId 
      }),
      headers: {
        'Content-Type': 'application/json',
        'X-Correlation-Id': correlationId
      }
    };
  }
};

async function routeToProvider(provider, model, prompt, temperature, maxTokens, correlationId) {
  // MVP: Mock implementation
  // In production, this would call actual LLM APIs
  
  console.log(JSON.stringify({
    level: 'INFO',
    correlationId,
    event: 'provider_request',
    provider,
    model,
    promptLength: prompt.length,
    temperature,
    maxTokens
  }));
  
  // Simulate processing time
  await new Promise(resolve => setTimeout(resolve, Math.random() * 1000 + 500));
  
  const mockResponses = {
    openai: `OpenAI ${model} response to: "${prompt.substring(0, 50)}..."`,
    anthropic: `Claude ${model} thoughtful response to: "${prompt.substring(0, 50)}..."`,
    cohere: `Cohere ${model} generated: "${prompt.substring(0, 50)}..."`,
    together: `Together ${model} completion: "${prompt.substring(0, 50)}..."`
  };
  
  return {
    provider,
    model,
    response: mockResponses[provider] || `Mock response from ${provider}`,
    usage: {
      promptTokens: Math.floor(prompt.length / 4),
      completionTokens: Math.floor(Math.random() * 200 + 50),
      totalTokens: Math.floor(prompt.length / 4) + Math.floor(Math.random() * 200 + 50)
    },
    finishReason: 'stop'
  };
}

async function emitCacheMetrics() {
  const hitRate = cacheHits / (cacheHits + cacheMisses) || 0;
  
  await cw.send(new PutMetricDataCommand({
    Namespace: 'C_N/MCP',
    MetricData: [
      {
        MetricName: 'CacheHitRate',
        Value: hitRate * 100,
        Unit: 'Percent',
        Dimensions: [{ Name: 'Environment', Value: 'PROD' }]
      },
      {
        MetricName: 'CacheSize',
        Value: cache.size,
        Unit: 'Count',
        Dimensions: [{ Name: 'Environment', Value: 'PROD' }]
      },
      {
        MetricName: 'RequestCount',
        Value: 1,
        Unit: 'Count',
        Dimensions: [{ Name: 'Environment', Value: 'PROD' }]
      }
    ]
  }));
  
  // Log for Phase 2 decision making
  if (hitRate >= 0.3) {
    console.log(JSON.stringify({
      level: 'INFO',
      event: 'cache_promotion_threshold',
      hitRate,
      cacheSize: cache.size,
      recommendation: 'Consider DynamoDB cache upgrade'
    }));
  }
}

function hashString(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  return Math.abs(hash).toString(36);
}