import { ethers } from 'ethers';
import { SecretsManagerClient, GetSecretValueCommand } from '@aws-sdk/client-secrets-manager';
import { CloudWatchClient, PutMetricDataCommand } from '@aws-sdk/client-cloudwatch';
import AWSXRay from 'aws-xray-sdk-core';

const sm = AWSXRay.captureAWSv3Client(new SecretsManagerClient());
const cw = AWSXRay.captureAWSv3Client(new CloudWatchClient());

export const handler = async (event) => {
  const correlationId = event.headers?.['X-Correlation-Id'] || crypto.randomUUID();
  const causationId = event.headers?.['X-Causation-Id'] || correlationId;
  
  console.log(JSON.stringify({ 
    level: 'INFO', 
    correlationId, 
    causationId,
    event: 'request_received',
    httpMethod: event.httpMethod,
    path: event.path
  }));
  
  try {
    // Handle health check
    if (event.httpMethod === 'GET' && event.path === '/health') {
      return { 
        statusCode: 200, 
        body: JSON.stringify({ 
          status: 'healthy', 
          timestamp: new Date().toISOString(),
          correlationId 
        }),
        headers: {
          'Content-Type': 'application/json',
          'X-Correlation-Id': correlationId
        }
      };
    }
    
    // Parse request body
    const { action, params } = JSON.parse(event.body || '{}');
    
    if (!action) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: 'Missing action parameter' }),
        headers: { 'X-Correlation-Id': correlationId }
      };
    }
    
    // Get signer key from Secrets Manager
    const secret = await sm.send(new GetSecretValueCommand({
      SecretId: '/C_N/PROD/Ledger/SignerKey'
    }));
    const { privateKey } = JSON.parse(secret.SecretString);
    
    // Connect to blockchain
    const provider = new ethers.JsonRpcProvider(process.env.CHAIN_RPC_URL_TESTNET);
    const signer = new ethers.Wallet(privateKey, provider);
    
    // Execute action
    let result;
    if (action === 'emitCheckpoint') {
      const contract = new ethers.Contract(
        process.env.LEDGER_CONTRACT_TRACE,
        ['function emitCheckpoint(string calldata ref, uint256 amount, string calldata currency) external'],
        signer
      );
      
      const tx = await contract.emitCheckpoint(
        params.batch || `batch-${Date.now()}`,
        params.amount || Date.now(),
        params.currency || JSON.stringify(params.metadata || {})
      );
      
      await tx.wait(1); // Single confirmation for testnet
      
      result = {
        txHash: tx.hash,
        blockNumber: tx.blockNumber,
        explorer: `${process.env.LEDGER_EXPLORER_BASE}/tx/${tx.hash}`,
        timestamp: new Date().toISOString()
      };
    } else if (action === 'getBalance') {
      const balance = await provider.getBalance(signer.address);
      result = {
        address: signer.address,
        balance: ethers.formatEther(balance),
        currency: 'ETH'
      };
    } else {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: `Unknown action: ${action}` }),
        headers: { 'X-Correlation-Id': correlationId }
      };
    }
    
    // Emit success metrics
    await cw.send(new PutMetricDataCommand({
      Namespace: 'C_N/Ledger',
      MetricData: [{
        MetricName: 'TransactionSuccess',
        Value: 1,
        Unit: 'Count',
        Dimensions: [
          { Name: 'Action', Value: action },
          { Name: 'Environment', Value: 'PROD' }
        ]
      }]
    }));
    
    console.log(JSON.stringify({
      level: 'INFO',
      correlationId,
      causationId,
      event: 'transaction_complete',
      action,
      txHash: result?.txHash,
      duration: Date.now() - parseInt(correlationId.split('-')[0] || '0', 16)
    }));
    
    return {
      statusCode: 200,
      body: JSON.stringify(result),
      headers: {
        'Content-Type': 'application/json',
        'X-Correlation-Id': correlationId,
        'X-Causation-Id': causationId
      }
    };
  } catch (error) {
    console.log(JSON.stringify({
      level: 'ERROR',
      correlationId,
      causationId,
      event: 'transaction_error',
      error: error.message,
      stack: error.stack?.split('\n')[0]
    }));
    
    // Emit error metrics
    await cw.send(new PutMetricDataCommand({
      Namespace: 'C_N/Ledger',
      MetricData: [{
        MetricName: 'TransactionError',
        Value: 1,
        Unit: 'Count',
        Dimensions: [
          { Name: 'ErrorType', Value: error.name || 'UnknownError' },
          { Name: 'Environment', Value: 'PROD' }
        ]
      }]
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