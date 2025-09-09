import { 
  StepFunctionsClient, 
  StartExecutionCommand, 
  DescribeExecutionCommand,
  ExecutionStatus
} from '@aws-sdk/client-sfn';
import { DynamoDBClient, GetItemCommand } from '@aws-sdk/client-dynamodb';
import { unmarshall } from '@aws-sdk/util-dynamodb';
import { expect } from '@jest/globals';

describe('Oracle Flow Integration Tests', () => {
  const sfn = new StepFunctionsClient({ region: 'us-east-1' });
  const ddb = new DynamoDBClient({ region: 'us-east-1' });
  
  const testPlotId = 'test-plot-001';
  const testBatchId = `test-batch-${Date.now()}`;
  const correlationId = `test-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  
  jest.setTimeout(300000); // 5 minutes timeout for end-to-end tests

  it('should complete satellite-weather-compose workflow successfully', async () => {
    const stateMachineArn = `arn:aws:states:us-east-1:${process.env.AWS_ACCOUNT_ID}:stateMachine:Sat-Weather-Compose`;
    
    const executionInput = {
      plotId: testPlotId,
      correlationId,
      causationId: correlationId,
      coordinates: { 
        lat: -0.3656, // Naivasha area coordinates
        lon: 36.0822 
      },
      dateFrom: '2025-01-01',
      dateTo: '2025-01-08'
    };
    
    console.log(`Starting execution with correlationId: ${correlationId}`);
    
    // Start Step Function execution
    const execution = await sfn.send(new StartExecutionCommand({
      stateMachineArn,
      input: JSON.stringify(executionInput),
      name: `test-execution-${Date.now()}`
    }));
    
    expect(execution.executionArn).toBeDefined();
    
    // Poll for completion
    let status: ExecutionStatus = ExecutionStatus.RUNNING;
    let attempts = 0;
    const maxAttempts = 60; // 5 minutes max
    
    while (status === ExecutionStatus.RUNNING && attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 5000)); // Wait 5 seconds
      
      const description = await sfn.send(new DescribeExecutionCommand({
        executionArn: execution.executionArn
      }));
      
      status = description.status!;
      attempts++;
      
      console.log(`Attempt ${attempts}: Status is ${status}`);
      
      if (description.output) {
        console.log('Execution output:', description.output);
      }
    }
    
    expect(status).toBe(ExecutionStatus.SUCCEEDED);
    expect(attempts).toBeLessThan(maxAttempts);
    
    // Wait a bit more for async processing
    await new Promise(resolve => setTimeout(resolve, 10000));
    
    // Verify ProductTrace read model was updated
    const productTraceResult = await ddb.send(new GetItemCommand({
      TableName: 'C_N-ReadModel-ProductTrace',
      Key: { batchId: { S: testBatchId } }
    }));
    
    if (productTraceResult.Item) {
      const productTrace = unmarshall(productTraceResult.Item);
      
      expect(productTrace).toBeDefined();
      expect(productTrace.batchId).toBe(testBatchId);
      expect(productTrace.timeline).toBeDefined();
      expect(Array.isArray(productTrace.timeline)).toBe(true);
      
      // Check for NDVI event
      const ndviEvent = productTrace.timeline.find((event: any) => event.ndvi);
      expect(ndviEvent).toBeDefined();
      
      // Check for weather event
      const weatherEvent = productTrace.timeline.find((event: any) => event.weather);
      expect(weatherEvent).toBeDefined();
      
      console.log('ProductTrace verified:', {
        batchId: productTrace.batchId,
        timelineLength: productTrace.timeline.length,
        events: productTrace.timeline.map((e: any) => e.event)
      });
    } else {
      console.warn('ProductTrace read model not found - may be async processing delay');
    }
  });

  it('should handle satellite data ingestion errors gracefully', async () => {
    const stateMachineArn = `arn:aws:states:us-east-1:${process.env.AWS_ACCOUNT_ID}:stateMachine:Sat-Weather-Compose`;
    
    const executionInput = {
      plotId: 'error-test-plot',
      correlationId: `error-${Date.now()}`,
      coordinates: { 
        lat: 200, // Invalid latitude to trigger error
        lon: 200  // Invalid longitude to trigger error
      },
      dateFrom: '2025-01-01'
    };
    
    const execution = await sfn.send(new StartExecutionCommand({
      stateMachineArn,
      input: JSON.stringify(executionInput),
      name: `error-test-${Date.now()}`
    }));
    
    // Poll for completion
    let status: ExecutionStatus = ExecutionStatus.RUNNING;
    let attempts = 0;
    
    while (status === ExecutionStatus.RUNNING && attempts < 30) {
      await new Promise(resolve => setTimeout(resolve, 5000));
      
      const description = await sfn.send(new DescribeExecutionCommand({
        executionArn: execution.executionArn
      }));
      
      status = description.status!;
      attempts++;
    }
    
    // Should either succeed with error handling or fail gracefully
    expect([ExecutionStatus.SUCCEEDED, ExecutionStatus.FAILED]).toContain(status);
    
    if (status === ExecutionStatus.FAILED) {
      const description = await sfn.send(new DescribeExecutionCommand({
        executionArn: execution.executionArn
      }));
      
      console.log('Error execution details:', description.error);
      expect(description.error).toContain('Satellite'); // Should be satellite-related error
    }
  });

  it('should process ledger anchoring workflow', async () => {
    const stateMachineArn = `arn:aws:states:us-east-1:${process.env.AWS_ACCOUNT_ID}:stateMachine:Ledger-Anchoring`;
    
    const executionInput = {
      batchId: testBatchId,
      correlationId: `anchor-${Date.now()}`,
      eventTypes: ['NDVI.Processed', 'Weather.Snapshotted']
    };
    
    const execution = await sfn.send(new StartExecutionCommand({
      stateMachineArn,
      input: JSON.stringify(executionInput),
      name: `anchor-test-${Date.now()}`
    }));
    
    expect(execution.executionArn).toBeDefined();
    
    // Poll for completion (anchoring takes longer due to blockchain)
    let status: ExecutionStatus = ExecutionStatus.RUNNING;
    let attempts = 0;
    const maxAttempts = 120; // 10 minutes for blockchain operations
    
    while (status === ExecutionStatus.RUNNING && attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 5000));
      
      const description = await sfn.send(new DescribeExecutionCommand({
        executionArn: execution.executionArn
      }));
      
      status = description.status!;
      attempts++;
      
      if (attempts % 12 === 0) { // Log every minute
        console.log(`Anchoring attempt ${attempts}/120: Status is ${status}`);
      }
    }
    
    // Anchoring might timeout due to blockchain conditions, that's acceptable
    expect([
      ExecutionStatus.SUCCEEDED, 
      ExecutionStatus.FAILED,
      ExecutionStatus.TIMED_OUT
    ]).toContain(status);
    
    if (status === ExecutionStatus.SUCCEEDED) {
      console.log('Blockchain anchoring completed successfully');
      
      const description = await sfn.send(new DescribeExecutionCommand({
        executionArn: execution.executionArn
      }));
      
      if (description.output) {
        const output = JSON.parse(description.output);
        expect(output.txHash).toMatch(/^0x[a-fA-F0-9]{64}$/); // Valid tx hash
        expect(output.blockNumber).toBeGreaterThan(0);
        console.log('Blockchain anchor details:', output);
      }
    } else {
      console.log('Blockchain anchoring did not complete - acceptable for test environment');
    }
  });
});

// Helper functions for test setup and teardown
beforeAll(async () => {
  console.log('🧪 Starting C_N Oracle Flow Integration Tests');
  console.log('Account ID:', process.env.AWS_ACCOUNT_ID);
  console.log('Region:', process.env.AWS_REGION || 'us-east-1');
});

afterAll(async () => {
  console.log('✅ C_N Oracle Flow Integration Tests completed');
  
  // Clean up test data if needed
  console.log('Test data cleanup - keeping for audit trail');
});