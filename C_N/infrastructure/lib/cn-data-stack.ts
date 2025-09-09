import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as kms from 'aws-cdk-lib/aws-kms';
import * as iam from 'aws-cdk-lib/aws-iam';

export class CNDataStack extends cdk.Stack {
  public readonly productTraceTable: dynamodb.Table;
  public readonly fundsTraceTable: dynamodb.Table;
  public readonly aegisKey: kms.Key;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Import Aegis KMS key from foundation stack
    this.aegisKey = kms.Key.fromLookup(this, 'AegisKMS', {
      aliasName: 'alias/Aegis_KMS__PROD'
    });

    // ProductTrace Read Model
    this.productTraceTable = new dynamodb.Table(this, 'ProductTraceReadModel', {
      tableName: 'C_N-ReadModel-ProductTrace',
      partitionKey: { name: 'batchId', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      encryption: dynamodb.TableEncryption.CUSTOMER_MANAGED,
      encryptionKey: this.aegisKey,
      pointInTimeRecovery: true,
      timeToLiveAttribute: 'ttl', // 7 years retention
      stream: dynamodb.StreamViewType.NEW_AND_OLD_IMAGES
    });

    // GSI for farm-based queries
    this.productTraceTable.addGlobalSecondaryIndex({
      indexName: 'FarmIndex',
      partitionKey: { name: 'farmId', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'harvestDate', type: dynamodb.AttributeType.STRING },
      projectionType: dynamodb.ProjectionType.ALL
    });

    // GSI for date range queries
    this.productTraceTable.addGlobalSecondaryIndex({
      indexName: 'DateRangeIndex',
      partitionKey: { name: 'schemaVer', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'harvestDate', type: dynamodb.AttributeType.STRING },
      projectionType: dynamodb.ProjectionType.ALL
    });

    // FundsTrace Read Model
    this.fundsTraceTable = new dynamodb.Table(this, 'FundsTraceReadModel', {
      tableName: 'C_N-ReadModel-FundsTrace',
      partitionKey: { name: 'contributionId', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      encryption: dynamodb.TableEncryption.CUSTOMER_MANAGED,
      encryptionKey: this.aegisKey,
      pointInTimeRecovery: true,
      timeToLiveAttribute: 'ttl',
      stream: dynamodb.StreamViewType.NEW_AND_OLD_IMAGES
    });

    // GSI for investor queries
    this.fundsTraceTable.addGlobalSecondaryIndex({
      indexName: 'InvestorIndex',
      partitionKey: { name: 'investorId', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'contributionDate', type: dynamodb.AttributeType.STRING },
      projectionType: dynamodb.ProjectionType.ALL
    });

    // GSI for batch allocation queries
    this.fundsTraceTable.addGlobalSecondaryIndex({
      indexName: 'BatchAllocationIndex',
      partitionKey: { name: 'allocatedBatchId', type: dynamodb.AttributeType.STRING },
      projectionType: dynamodb.ProjectionType.ALL
    });

    // Satellite Tiles Storage (Hot data with S3 integration)
    const satelliteTilesTable = new dynamodb.Table(this, 'SatelliteTilesIndex', {
      tableName: 'C_N-SatelliteTiles-Index',
      partitionKey: { name: 'tileKey', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'captureDate', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      encryption: dynamodb.TableEncryption.CUSTOMER_MANAGED,
      encryptionKey: this.aegisKey,
      timeToLiveAttribute: 'ttl' // 90 days retention in DDB, then S3 Glacier
    });

    satelliteTilesTable.addGlobalSecondaryIndex({
      indexName: 'PlotDateIndex',
      partitionKey: { name: 'plotId', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'captureDate', type: dynamodb.AttributeType.STRING },
      projectionType: dynamodb.ProjectionType.ALL
    });

    // Create IAM policy for read model access
    const readModelPolicy = new iam.ManagedPolicy(this, 'ReadModelAccess', {
      managedPolicyName: 'C_N-ReadModel-Access',
      statements: [
        new iam.PolicyStatement({
          effect: iam.Effect.ALLOW,
          actions: [
            'dynamodb:GetItem',
            'dynamodb:Query',
            'dynamodb:BatchGetItem'
          ],
          resources: [
            this.productTraceTable.tableArn,
            this.fundsTraceTable.tableArn,
            `${this.productTraceTable.tableArn}/index/*`,
            `${this.fundsTraceTable.tableArn}/index/*`
          ]
        }),
        new iam.PolicyStatement({
          effect: iam.Effect.ALLOW,
          actions: ['kms:Decrypt'],
          resources: [this.aegisKey.keyArn]
        })
      ]
    });

    // Create IAM policy for materializer write access
    const materializerPolicy = new iam.ManagedPolicy(this, 'MaterializerAccess', {
      managedPolicyName: 'C_N-Materializer-Access',
      statements: [
        new iam.PolicyStatement({
          effect: iam.Effect.ALLOW,
          actions: [
            'dynamodb:PutItem',
            'dynamodb:UpdateItem',
            'dynamodb:GetItem'
          ],
          resources: [
            this.productTraceTable.tableArn,
            this.fundsTraceTable.tableArn,
            satelliteTilesTable.tableArn
          ]
        }),
        new iam.PolicyStatement({
          effect: iam.Effect.ALLOW,
          actions: ['kms:Encrypt', 'kms:Decrypt', 'kms:GenerateDataKey'],
          resources: [this.aegisKey.keyArn]
        })
      ]
    });

    // Apply standard tags
    cdk.Tags.of(this).add('WORLD', 'Continuum_Overworld');
    cdk.Tags.of(this).add('ORCHESTRATOR', 'C_N');
    cdk.Tags.of(this).add('ENV', 'PROD');
    cdk.Tags.of(this).add('DIVISION', 'Data');
    cdk.Tags.of(this).add('CAPABILITY', 'ReadModels');

    // Outputs
    new cdk.CfnOutput(this, 'ProductTraceTableName', {
      value: this.productTraceTable.tableName,
      description: 'ProductTrace read model table name'
    });

    new cdk.CfnOutput(this, 'FundsTraceTableName', {
      value: this.fundsTraceTable.tableName,
      description: 'FundsTrace read model table name'
    });

    new cdk.CfnOutput(this, 'SatelliteTilesIndexName', {
      value: satelliteTilesTable.tableName,
      description: 'Satellite tiles index table name'
    });

    new cdk.CfnOutput(this, 'ReadModelPolicyArn', {
      value: readModelPolicy.managedPolicyArn,
      description: 'IAM policy ARN for read model access'
    });

    new cdk.CfnOutput(this, 'MaterializerPolicyArn', {
      value: materializerPolicy.managedPolicyArn,
      description: 'IAM policy ARN for materializer access'
    });
  }
}