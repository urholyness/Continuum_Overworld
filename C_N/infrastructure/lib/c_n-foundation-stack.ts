import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as kms from 'aws-cdk-lib/aws-kms';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as cloudwatch from 'aws-cdk-lib/aws-cloudwatch';
import * as budgets from 'aws-cdk-lib/aws-budgets';
import * as ce from 'aws-cdk-lib/aws-ce';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as schemas from 'aws-cdk-lib/aws-eventschemas';

export class CNFoundationStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);
    
    // Aegis KMS Key with proper alias
    const aegisKey = new kms.Key(this, 'AegisKMS', {
      enableKeyRotation: true,
      description: 'C_N master encryption key'
    });
    aegisKey.addAlias('alias/Aegis_KMS__PROD');
    
    // Meridian Alerts SNS Topic
    const meridianAlerts = new sns.Topic(this, 'MeridianAlerts', {
      topicName: 'C_N-Meridian-Alerts',
      masterKey: aegisKey
    });
    
    // EventBridge with DLQ
    const eventBusDLQ = new sqs.Queue(this, 'EventBusDLQ', {
      queueName: 'C_N-EventBus-DLQ',
      encryption: sqs.QueueEncryption.KMS,
      encryptionMasterKey: aegisKey,
      retentionPeriod: cdk.Duration.days(14)
    });
    
    const eventBus = new events.EventBus(this, 'CNEventBus', {
      eventBusName: 'C_N-EventBus-Core'
    });
    
    // Schema Registry
    const schemaRegistry = new schemas.CfnRegistry(this, 'CNSchemaRegistry', {
      registryName: 'C_N-Core',
      description: 'Event schemas for C_N agents'
    });
    
    // NDVI.Processed@v1 Schema
    new schemas.CfnSchema(this, 'NDVIProcessedSchema', {
      registryName: schemaRegistry.registryName,
      schemaName: 'NDVI.Processed@v1',
      type: 'JSONSchemaDraft4',
      content: JSON.stringify({
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type": "object",
        "required": ["source", "detail-type", "time", "detail"],
        "properties": {
          "detail": {
            "type": "object",
            "required": ["correlationId", "causationId", "plotId", "index", "tileUri"],
            "properties": {
              "correlationId": { "type": "string", "format": "uuid" },
              "causationId": { "type": "string", "format": "uuid" },
              "plotId": { "type": "string" },
              "index": { "type": "number" },
              "tileUri": { "type": "string", "format": "uri" }
            }
          }
        }
      })
    });
    
    // Pantheon Registry with optimizations
    const pantheonTable = new dynamodb.Table(this, 'PantheonRegistry', {
      tableName: 'C_N-Pantheon-Registry',
      partitionKey: { name: 'agentId', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      encryption: dynamodb.TableEncryption.CUSTOMER_MANAGED,
      encryptionKey: aegisKey,
      pointInTimeRecovery: true,
      timeToLiveAttribute: 'ttl'
    });
    
    pantheonTable.addGlobalSecondaryIndex({
      indexName: 'DivisionIndex',
      partitionKey: { name: 'division', type: dynamodb.AttributeType.STRING },
      projectionType: dynamodb.ProjectionType.ALL
    });
    
    // Farm Plots Table
    const farmPlotsTable = new dynamodb.Table(this, 'FarmPlots', {
      tableName: 'C_N-Oracle-FarmPlots',
      partitionKey: { name: 'plotId', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      encryption: dynamodb.TableEncryption.CUSTOMER_MANAGED,
      encryptionKey: aegisKey,
      pointInTimeRecovery: true,
      timeToLiveAttribute: 'ttl'
    });
    
    farmPlotsTable.addGlobalSecondaryIndex({
      indexName: 'FarmIndex',
      partitionKey: { name: 'farmId', type: dynamodb.AttributeType.STRING },
      projectionType: dynamodb.ProjectionType.ALL
    });
    
    // Daily Budget
    new budgets.CfnBudget(this, 'DailyBudget', {
      budget: {
        budgetName: 'C_N-Daily-Budget',
        budgetType: 'COST',
        timeUnit: 'DAILY',
        budgetLimit: { amount: 20, unit: 'USD' }
      },
      notificationsWithSubscribers: [{
        notification: {
          notificationType: 'ACTUAL',
          comparisonOperator: 'GREATER_THAN',
          threshold: 80
        },
        subscribers: [{
          subscriptionType: 'SNS',
          address: meridianAlerts.topicArn
        }]
      }]
    });
    
    // Cost Anomaly Detection
    const anomalyMonitor = new ce.CfnAnomalyMonitor(this, 'CostAnomalyMonitor', {
      monitorName: 'C_N-All-Services',
      monitorType: 'DIMENSIONAL',
      monitorSpecification: JSON.stringify({
        "Dimension": "SERVICE"
      })
    });
    
    new ce.CfnAnomalySubscription(this, 'CostAnomalySubscription', {
      subscriptionName: 'C_N-Anomaly-Alerts',
      frequency: 'IMMEDIATE',
      monitorArnList: [anomalyMonitor.attrMonitorArn],
      subscribers: [{
        type: 'SNS',
        address: meridianAlerts.topicArn
      }],
      threshold: 10
    });
    
    // CloudWatch Dashboard with cost metrics from us-east-1
    new cloudwatch.Dashboard(this, 'CNDashboard', {
      dashboardName: 'C_N-Fleet-Health',
      widgets: [
        [
          new cloudwatch.GraphWidget({
            title: 'Agent Health',
            left: [
              pantheonTable.metricUserErrors(),
              new cloudwatch.Metric({
                namespace: 'AWS/Events',
                metricName: 'FailedInvocations',
                dimensionsMap: { EventBusName: 'C_N-EventBus-Core' }
              })
            ]
          }),
          new cloudwatch.GraphWidget({
            title: 'Cost per Day (USD)',
            left: [
              new cloudwatch.Metric({
                namespace: 'AWS/Billing',
                metricName: 'EstimatedCharges',
                dimensionsMap: { Currency: 'USD' },
                region: 'us-east-1' // Billing metrics only in us-east-1
              })
            ]
          })
        ]
      ]
    });
    
    // Apply standard tags
    cdk.Tags.of(this).add('WORLD', 'Continuum_Overworld');
    cdk.Tags.of(this).add('ORCHESTRATOR', 'C_N');
    cdk.Tags.of(this).add('ENV', 'PROD');
    cdk.Tags.of(this).add('DIVISION', 'Core');
    cdk.Tags.of(this).add('CAPABILITY', 'Foundation');
    
    // Outputs
    new cdk.CfnOutput(this, 'EventBusName', {
      value: eventBus.eventBusName,
      description: 'C_N EventBus Name'
    });
    
    new cdk.CfnOutput(this, 'PantheonRegistryName', {
      value: pantheonTable.tableName,
      description: 'Pantheon Registry Table Name'
    });
    
    new cdk.CfnOutput(this, 'FarmPlotsTableName', {
      value: farmPlotsTable.tableName,
      description: 'Farm Plots Table Name'
    });
    
    new cdk.CfnOutput(this, 'AegisKMSKeyId', {
      value: aegisKey.keyId,
      description: 'Aegis KMS Key ID'
    });
    
    new cdk.CfnOutput(this, 'MeridianAlertsTopicArn', {
      value: meridianAlerts.topicArn,
      description: 'Meridian Alerts SNS Topic ARN'
    });
  }
}