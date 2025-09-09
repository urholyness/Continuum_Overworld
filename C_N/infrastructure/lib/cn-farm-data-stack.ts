import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as kms from 'aws-cdk-lib/aws-kms';

export interface FarmDataStackProps extends cdk.StackProps {
  kmsKey: kms.IKey;
  environment: string;
}

export class CNFarmDataStack extends cdk.Stack {
  public readonly farmRegistryTable: dynamodb.Table;
  public readonly farmPlotsTable: dynamodb.Table;
  public readonly satelliteDataTable: dynamodb.Table;
  public readonly weatherDataTable: dynamodb.Table;
  public readonly productTraceTable: dynamodb.Table;
  public readonly fundsTraceTable: dynamodb.Table;

  constructor(scope: Construct, id: string, props: FarmDataStackProps) {
    super(scope, id, props);

    // Enterprise security settings for all tables
    const tableDefaults = {
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      encryption: dynamodb.TableEncryption.CUSTOMER_MANAGED,
      encryptionKey: props.kmsKey,
      pointInTimeRecovery: true,
      deletionProtection: true,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    };

    // 1. Farm Registry Table
    this.farmRegistryTable = new dynamodb.Table(this, 'FarmRegistry', {
      tableName: 'C_N-FarmRegistry',
      partitionKey: { name: 'farmId', type: dynamodb.AttributeType.STRING },
      stream: dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
      ...tableDefaults
    });

    // Add Global Secondary Indexes for Farm Registry
    this.farmRegistryTable.addGlobalSecondaryIndex({
      indexName: 'CountryIndex',
      partitionKey: { name: 'country', type: dynamodb.AttributeType.STRING }
    });

    this.farmRegistryTable.addGlobalSecondaryIndex({
      indexName: 'GeohashIndex',
      partitionKey: { name: 'geohash5', type: dynamodb.AttributeType.STRING }
    });

    // 2. Farm Plots Table
    this.farmPlotsTable = new dynamodb.Table(this, 'FarmPlots', {
      tableName: 'C_N-Oracle-FarmPlots',
      partitionKey: { name: 'plotId', type: dynamodb.AttributeType.STRING },
      ...tableDefaults
    });

    // Add Global Secondary Indexes for Farm Plots
    this.farmPlotsTable.addGlobalSecondaryIndex({
      indexName: 'FarmIndex',
      partitionKey: { name: 'farmId', type: dynamodb.AttributeType.STRING }
    });

    this.farmPlotsTable.addGlobalSecondaryIndex({
      indexName: 'GeohashIndex',
      partitionKey: { name: 'geohash7', type: dynamodb.AttributeType.STRING }
    });

    // 3. Satellite Data Table (with TTL)
    this.satelliteDataTable = new dynamodb.Table(this, 'SatelliteData', {
      tableName: 'C_N-Oracle-SatelliteData',
      partitionKey: { name: 'plotId', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'timestamp', type: dynamodb.AttributeType.NUMBER },
      timeToLiveAttribute: 'ttl',
      ...tableDefaults
    });

    // Add Global Secondary Index for Satellite Data
    this.satelliteDataTable.addGlobalSecondaryIndex({
      indexName: 'GeohashIndex',
      partitionKey: { name: 'geohash', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'timestamp', type: dynamodb.AttributeType.NUMBER }
    });

    // 4. Weather Data Table (with TTL)
    this.weatherDataTable = new dynamodb.Table(this, 'WeatherData', {
      tableName: 'C_N-Oracle-WeatherData',
      partitionKey: { name: 'plotId', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'timestamp', type: dynamodb.AttributeType.NUMBER },
      timeToLiveAttribute: 'ttl',
      ...tableDefaults
    });

    // Add Global Secondary Index for Weather Data
    this.weatherDataTable.addGlobalSecondaryIndex({
      indexName: 'GeohashIndex',
      partitionKey: { name: 'geohash', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'timestamp', type: dynamodb.AttributeType.NUMBER }
    });

    // 5. Product Trace Read Model (Immutable)
    this.productTraceTable = new dynamodb.Table(this, 'ProductTraceReadModel', {
      tableName: 'C_N-ReadModel-ProductTrace',
      partitionKey: { name: 'batchId', type: dynamodb.AttributeType.STRING },
      stream: dynamodb.StreamViewType.NEW_IMAGE,
      ...tableDefaults
    });

    // 6. Funds Trace Read Model (Immutable)
    this.fundsTraceTable = new dynamodb.Table(this, 'FundsTraceReadModel', {
      tableName: 'C_N-ReadModel-FundsTrace',
      partitionKey: { name: 'contributionId', type: dynamodb.AttributeType.STRING },
      stream: dynamodb.StreamViewType.NEW_IMAGE,
      ...tableDefaults
    });

    // Output table ARNs for use in other stacks
    new cdk.CfnOutput(this, 'FarmRegistryTableArn', {
      value: this.farmRegistryTable.tableArn,
      description: 'Farm Registry Table ARN',
      exportName: 'CN-FarmRegistry-TableArn'
    });

    new cdk.CfnOutput(this, 'FarmPlotsTableArn', {
      value: this.farmPlotsTable.tableArn,
      description: 'Farm Plots Table ARN',
      exportName: 'CN-FarmPlots-TableArn'
    });

    new cdk.CfnOutput(this, 'SatelliteDataTableArn', {
      value: this.satelliteDataTable.tableArn,
      description: 'Satellite Data Table ARN',
      exportName: 'CN-SatelliteData-TableArn'
    });

    new cdk.CfnOutput(this, 'WeatherDataTableArn', {
      value: this.weatherDataTable.tableArn,
      description: 'Weather Data Table ARN',
      exportName: 'CN-WeatherData-TableArn'
    });

    // Apply comprehensive tags
    cdk.Tags.of(this).add('WORLD', 'Continuum_Overworld');
    cdk.Tags.of(this).add('ORCHESTRATOR', 'C_N');
    cdk.Tags.of(this).add('ENV', props.environment);
    cdk.Tags.of(this).add('CAPABILITY', 'FarmData');
    cdk.Tags.of(this).add('SECURITY', 'Enterprise');
    cdk.Tags.of(this).add('COMPLIANCE', 'PITR-KMS-Enabled');
  }
}