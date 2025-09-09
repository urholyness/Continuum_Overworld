#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { CNFarmDataStack } from '../lib/cn-farm-data-stack';
import { CNFarmStorageStack } from '../lib/cn-farm-storage-stack';
import { CNFarmApiStack } from '../lib/cn-farm-api-stack';
import { CNFarmObservabilityStack } from '../lib/cn-farm-observability-stack';
import { CNFarmSchemasConstruct } from '../lib/cn-farm-schemas';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as kms from 'aws-cdk-lib/aws-kms';
import * as events from 'aws-cdk-lib/aws-events';

const app = new cdk.App();

// Get environment and account from context or environment variables
const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT || app.node.tryGetContext('account'),
  region: process.env.CDK_DEFAULT_REGION || app.node.tryGetContext('region') || 'us-east-1'
};

const environment = process.env.ENVIRONMENT || 'PROD';

// Create KMS key for encryption (shared across stacks)
class CNFarmFoundationStack extends cdk.Stack {
  public readonly kmsKey: kms.Key;
  public readonly eventBus: events.EventBus;

  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create KMS key for encryption
    this.kmsKey = new kms.Key(this, 'AegisKMSKey', {
      alias: 'Aegis_KMS__PROD',
      description: 'Enterprise KMS key for C_N Farm Infrastructure',
      enableKeyRotation: true,
      removalPolicy: cdk.RemovalPolicy.RETAIN
    });

    // Create EventBridge bus
    this.eventBus = new events.EventBus(this, 'FarmEventBus', {
      eventBusName: 'C_N-EventBus-Core',
      description: 'Core event bus for farm management and Oracle events'
    });

    // Outputs
    new cdk.CfnOutput(this, 'KMSKeyId', {
      value: this.kmsKey.keyId,
      exportName: 'CN-AegisKMS-KeyId'
    });

    new cdk.CfnOutput(this, 'KMSKeyArn', {
      value: this.kmsKey.keyArn,
      exportName: 'CN-AegisKMS-KeyArn'
    });

    new cdk.CfnOutput(this, 'EventBusName', {
      value: this.eventBus.eventBusName,
      exportName: 'CN-EventBus-Name'
    });
  }
}

// Create farm compute stack with Lambda functions
class CNFarmComputeStack extends cdk.Stack {
  public readonly farmValidatorFunction: lambda.Function;
  public readonly satelliteFunction: lambda.Function;

  constructor(scope: cdk.App, id: string, kmsKey: kms.IKey, props?: cdk.StackProps) {
    super(scope, id, props);

    // Farm Validator Lambda Function
    this.farmValidatorFunction = new lambda.Function(this, 'FarmValidator', {
      functionName: 'C_N-Farm-Validator',
      runtime: lambda.Runtime.NODEJS_18_X,
      handler: 'index.handler',
      code: lambda.Code.fromAsset('lib/lambda/farm-validator'),
      timeout: cdk.Duration.seconds(30),
      memorySize: 512,
      environment: {
        AEGIS_KMS_KEY: kmsKey.keyArn,
        NODE_OPTIONS: '--enable-source-maps'
      },
      tracing: lambda.Tracing.ACTIVE,
      reservedConcurrentExecutions: 5,
      description: 'Enterprise farm geometry validator with polygon validation'
    });

    // Enhanced Satellite Oracle Lambda Function
    this.satelliteFunction = new lambda.Function(this, 'SatelliteOracle', {
      functionName: 'C_N-Oracle-Satellite-Enhanced',
      runtime: lambda.Runtime.NODEJS_18_X,
      handler: 'index.handler',
      code: lambda.Code.fromAsset('lib/lambda/oracle-satellite-enhanced'),
      timeout: cdk.Duration.minutes(2),
      memorySize: 1024,
      environment: {
        AEGIS_KMS_KEY: kmsKey.keyArn,
        NODE_OPTIONS: '--enable-source-maps'
      },
      tracing: lambda.Tracing.ACTIVE,
      reservedConcurrentExecutions: 10,
      description: 'Enhanced satellite data processing with polygon clipping and quality assessment'
    });

    // Grant permissions
    kmsKey.grantEncryptDecrypt(this.farmValidatorFunction);
    kmsKey.grantEncryptDecrypt(this.satelliteFunction);

    // Outputs
    new cdk.CfnOutput(this, 'FarmValidatorArn', {
      value: this.farmValidatorFunction.functionArn,
      exportName: 'CN-FarmValidator-Arn'
    });

    new cdk.CfnOutput(this, 'SatelliteFunctionArn', {
      value: this.satelliteFunction.functionArn,
      exportName: 'CN-SatelliteFunction-Arn'
    });
  }
}

// Deploy stacks in dependency order
const foundationStack = new CNFarmFoundationStack(app, 'CNFarmFoundationStack', {
  env,
  description: 'C_N Farm Infrastructure - Foundation (KMS, EventBridge)',
  stackName: 'C-N-Farm-Foundation'
});

const dataStack = new CNFarmDataStack(app, 'CNFarmDataStack', {
  env,
  kmsKey: foundationStack.kmsKey,
  environment,
  description: 'C_N Farm Infrastructure - Data Layer (DynamoDB)',
  stackName: 'C-N-Farm-Data'
});
dataStack.addDependency(foundationStack);

const storageStack = new CNFarmStorageStack(app, 'CNFarmStorageStack', {
  env,
  kmsKey: foundationStack.kmsKey,
  environment,
  description: 'C_N Farm Infrastructure - Storage (S3)',
  stackName: 'C-N-Farm-Storage'
});
storageStack.addDependency(foundationStack);

const computeStack = new CNFarmComputeStack(app, 'CNFarmComputeStack', foundationStack.kmsKey, {
  env,
  description: 'C_N Farm Infrastructure - Compute (Lambda)',
  stackName: 'C-N-Farm-Compute'
});
computeStack.addDependency(foundationStack);
computeStack.addDependency(dataStack);
computeStack.addDependency(storageStack);

const apiStack = new CNFarmApiStack(app, 'CNFarmApiStack', {
  env,
  farmValidatorFunction: computeStack.farmValidatorFunction,
  satelliteFunction: computeStack.satelliteFunction,
  kmsKey: foundationStack.kmsKey,
  environment,
  description: 'C_N Farm Infrastructure - API Gateway with WAF',
  stackName: 'C-N-Farm-API'
});
apiStack.addDependency(computeStack);

// Add schemas construct to foundation stack
new CNFarmSchemasConstruct(foundationStack, 'FarmSchemas', {
  eventBus: foundationStack.eventBus,
  environment
});

const observabilityStack = new CNFarmObservabilityStack(app, 'CNFarmObservabilityStack', {
  env,
  farmValidatorFunction: computeStack.farmValidatorFunction,
  satelliteFunction: computeStack.satelliteFunction,
  api: apiStack.api,
  environment,
  description: 'C_N Farm Infrastructure - Observability and Monitoring',
  stackName: 'C-N-Farm-Observability'
});
observabilityStack.addDependency(apiStack);

// Apply tags to all stacks
const tags = {
  'WORLD': 'Continuum_Overworld',
  'ORCHESTRATOR': 'C_N',
  'PROJECT': 'FarmInfrastructure',
  'ENV': environment,
  'DEPLOYMENT': 'Enterprise',
  'COMPLIANCE': 'KMS-PITR-WAF',
  'COST_CENTER': 'Agricultural_Operations'
};

Object.entries(tags).forEach(([key, value]) => {
  cdk.Tags.of(app).add(key, value);
});

// Add stack-specific tags
cdk.Tags.of(foundationStack).add('LAYER', 'Foundation');
cdk.Tags.of(dataStack).add('LAYER', 'Data');
cdk.Tags.of(storageStack).add('LAYER', 'Storage');
cdk.Tags.of(computeStack).add('LAYER', 'Compute');
cdk.Tags.of(apiStack).add('LAYER', 'API');
cdk.Tags.of(observabilityStack).add('LAYER', 'Observability');

// Output deployment summary
new cdk.CfnOutput(foundationStack, 'DeploymentSummary', {
  value: JSON.stringify({
    project: 'C_N Enterprise Farm Infrastructure',
    version: 'v1.1.0',
    stacks: 6,
    capabilities: [
      'Real coordinate validation',
      'Polygon geometry validation',
      'Enhanced satellite processing',
      'Enterprise security (KMS, WAF, PITR)',
      'Step Functions orchestration',
      'Comprehensive monitoring'
    ],
    compliance: 'Enterprise-grade with audit trails',
    estimatedMonthlyCost: '$15-25'
  }),
  description: 'Enterprise Farm Infrastructure Deployment Summary'
});