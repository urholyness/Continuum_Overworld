import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigatewayv2';
import * as apigatewayIntegrations from 'aws-cdk-lib/aws-apigatewayv2-integrations';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as cognito from 'aws-cdk-lib/aws-cognito';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as snsSubscriptions from 'aws-cdk-lib/aws-sns-subscriptions';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as cloudfrontOrigins from 'aws-cdk-lib/aws-cloudfront-origins';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as waf from 'aws-cdk-lib/aws-wafv2';
import * as budgets from 'aws-cdk-lib/aws-budgets';

export class FarmIngestStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const env = this.node.tryGetContext('env') || 'sbx';
    const prefix = `gsg-${env}`;

    // DynamoDB Tables
    const farmsTable = new dynamodb.Table(this, 'FarmsTable', {
      tableName: `${prefix}-farms`,
      partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: env === 'prod' ? cdk.RemovalPolicy.RETAIN : cdk.RemovalPolicy.DESTROY,
    });

    const readingsTable = new dynamodb.Table(this, 'ReadingsTable', {
      tableName: `${prefix}-readings`,
      partitionKey: { name: 'pk', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'sk', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: env === 'prod' ? cdk.RemovalPolicy.RETAIN : cdk.RemovalPolicy.DESTROY,
    });

    const opsEventsTable = new dynamodb.Table(this, 'OpsEventsTable', {
      tableName: `${prefix}-ops_events`,
      partitionKey: { name: 'pk', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'sk', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: env === 'prod' ? cdk.RemovalPolicy.RETAIN : cdk.RemovalPolicy.DESTROY,
    });

    // S3 Buckets
    const dataBucket = new s3.Bucket(this, 'DataBucket', {
      bucketName: `${prefix}-data-curated`,
      versioned: env === 'prod',
      publicReadAccess: false,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: env === 'prod' ? cdk.RemovalPolicy.RETAIN : cdk.RemovalPolicy.DESTROY,
      lifecycleRules: [{
        id: 'delete-old-sat-images',
        enabled: true,
        expiration: cdk.Duration.days(90),
        prefix: 'sat/'
      }]
    });

    const webAssetsBucket = new s3.Bucket(this, 'WebAssetsBucket', {
      bucketName: `${prefix}-web-assets`,
      versioned: false,
      publicReadAccess: false,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: env === 'prod' ? cdk.RemovalPolicy.RETAIN : cdk.RemovalPolicy.DESTROY,
      cors: [{
        allowedOrigins: ['*'],
        allowedMethods: [s3.HttpMethods.GET, s3.HttpMethods.PUT],
        allowedHeaders: ['*'],
      }]
    });

    // Cognito User Pool
    const userPool = new cognito.UserPool(this, 'UserPool', {
      userPoolName: `${prefix}-farm-users`,
      selfSignUpEnabled: false,
      signInAliases: { email: true },
      autoVerify: { email: true },
      passwordPolicy: {
        minLength: 8,
        requireLowercase: true,
        requireUppercase: true,
        requireDigits: true,
        requireSymbols: false,
      },
      removalPolicy: env === 'prod' ? cdk.RemovalPolicy.RETAIN : cdk.RemovalPolicy.DESTROY,
    });

    const buyersGroup = new cognito.CfnUserPoolGroup(this, 'BuyersGroup', {
      userPoolId: userPool.userPoolId,
      groupName: 'buyers',
      description: 'Buyers with access to detailed farm data',
    });

    const adminsGroup = new cognito.CfnUserPoolGroup(this, 'AdminsGroup', {
      userPoolId: userPool.userPoolId,
      groupName: 'admins',
      description: 'Admins with full access',
    });

    const userPoolClient = new cognito.UserPoolClient(this, 'UserPoolClient', {
      userPool,
      authFlows: {
        userPassword: true,
        userSrp: true,
      },
      generateSecret: false,
    });

    // Lambda Functions
    const weatherIngestLambda = new lambda.Function(this, 'WeatherIngestLambda', {
      functionName: `${prefix}-weather-ingest`,
      runtime: lambda.Runtime.NODEJS_18_X,
      handler: 'weather_ingest/index.handler',
      code: lambda.Code.fromAsset('../dist'),
      timeout: cdk.Duration.seconds(30),
      environment: {
        ACCUWEATHER_API_KEY: process.env.ACCUWEATHER_API_KEY || '',
        FARM_ID: '2BH',
        FARM_LAT: '-0.5143',
        FARM_LON: '35.2698',
      },
    });

    const satAgentLambda = new lambda.Function(this, 'SatAgentLambda', {
      functionName: `${prefix}-sat-agent`,
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: 'sat_agent/index.handler',
      code: lambda.Code.fromAsset('../../sat-agent/src'),
      timeout: cdk.Duration.minutes(5),
      memorySize: 1024,
      environment: {
        SENTINELHUB_CLIENT_ID: process.env.SENTINELHUB_CLIENT_ID || '',
        SENTINELHUB_CLIENT_SECRET: process.env.SENTINELHUB_CLIENT_SECRET || '',
        FARM_ID: '2BH',
        FARM_POLYGON_GEOJSON: JSON.stringify({
          "type": "Feature",
          "properties": {"farm_id":"2BH","name":"Two Butterflies Homestead"},
          "geometry": {
            "type": "Polygon",
            "coordinates": [[
              [35.2648,-0.5193],[35.2748,-0.5193],
              [35.2748,-0.5093],[35.2648,-0.5093],
              [35.2648,-0.5193]
            ]]
          }
        }),
        S3_BUCKET: dataBucket.bucketName,
      },
    });

    const opsPostLambda = new lambda.Function(this, 'OpsPostLambda', {
      functionName: `${prefix}-ops-post`,
      runtime: lambda.Runtime.NODEJS_18_X,
      handler: 'api/ops_post.handler',
      code: lambda.Code.fromAsset('../dist'),
      timeout: cdk.Duration.seconds(30),
      environment: {
        S3_BUCKET: webAssetsBucket.bucketName,
        FARM_ID: '2BH',
      },
    });

    const opsGetLambda = new lambda.Function(this, 'OpsGetLambda', {
      functionName: `${prefix}-ops-get`,
      runtime: lambda.Runtime.NODEJS_18_X,
      handler: 'api/ops_get.handler',
      code: lambda.Code.fromAsset('../dist'),
      timeout: cdk.Duration.seconds(30),
    });

    const summaryGetLambda = new lambda.Function(this, 'SummaryGetLambda', {
      functionName: `${prefix}-summary-get`,
      runtime: lambda.Runtime.NODEJS_18_X,
      handler: 'api/summary_get.handler',
      code: lambda.Code.fromAsset('../dist'),
      timeout: cdk.Duration.seconds(30),
      environment: {
        FARM_POLYGON_GEOJSON: JSON.stringify({
          "type": "Feature",
          "properties": {"farm_id":"2BH","name":"Two Butterflies Homestead"},
          "geometry": {
            "type": "Polygon",
            "coordinates": [[
              [35.2648,-0.5193],[35.2748,-0.5193],
              [35.2748,-0.5093],[35.2648,-0.5093],
              [35.2648,-0.5193]
            ]]
          }
        }),
      },
    });

    const readingsGetLambda = new lambda.Function(this, 'ReadingsGetLambda', {
      functionName: `${prefix}-readings-get`,
      runtime: lambda.Runtime.NODEJS_18_X,
      handler: 'api/readings_get.handler',
      code: lambda.Code.fromAsset('../dist'),
      timeout: cdk.Duration.seconds(30),
    });

    const alertsLambda = new lambda.Function(this, 'AlertsLambda', {
      functionName: `${prefix}-alerts`,
      runtime: lambda.Runtime.NODEJS_18_X,
      handler: 'alerts/index.handler',
      code: lambda.Code.fromAsset('../dist'),
      timeout: cdk.Duration.seconds(30),
      environment: {
        FARM_ID: '2BH',
      },
    });

    // Grant permissions
    readingsTable.grantReadWriteData(weatherIngestLambda);
    readingsTable.grantReadWriteData(satAgentLambda);
    readingsTable.grantReadData(summaryGetLambda);
    readingsTable.grantReadData(readingsGetLambda);
    readingsTable.grantReadData(alertsLambda);
    
    opsEventsTable.grantReadWriteData(opsPostLambda);
    opsEventsTable.grantReadData(opsGetLambda);
    opsEventsTable.grantReadData(summaryGetLambda);
    
    dataBucket.grantReadWrite(satAgentLambda);
    webAssetsBucket.grantReadWrite(opsPostLambda);

    // API Gateway
    const api = new apigateway.HttpApi(this, 'FarmApi', {
      apiName: `${prefix}-farm-api`,
      corsPreflight: {
        allowOrigins: ['*'],
        allowMethods: [apigateway.CorsHttpMethod.ANY],
        allowHeaders: ['*'],
      },
    });

    // API Routes
    api.addRoutes({
      path: '/farms/{farmId}/summary',
      methods: [apigateway.HttpMethod.GET],
      integration: new apigatewayIntegrations.HttpLambdaIntegration('SummaryIntegration', summaryGetLambda),
    });

    api.addRoutes({
      path: '/farms/{farmId}/readings',
      methods: [apigateway.HttpMethod.GET],
      integration: new apigatewayIntegrations.HttpLambdaIntegration('ReadingsIntegration', readingsGetLambda),
    });

    api.addRoutes({
      path: '/farms/{farmId}/ops',
      methods: [apigateway.HttpMethod.GET],
      integration: new apigatewayIntegrations.HttpLambdaIntegration('OpsGetIntegration', opsGetLambda),
    });

    api.addRoutes({
      path: '/ops',
      methods: [apigateway.HttpMethod.POST],
      integration: new apigatewayIntegrations.HttpLambdaIntegration('OpsPostIntegration', opsPostLambda),
    });

    // EventBridge Schedules
    new events.Rule(this, 'WeatherIngestSchedule', {
      ruleName: `${prefix}-weather-ingest-schedule`,
      schedule: events.Schedule.rate(cdk.Duration.hours(1)),
      targets: [new targets.LambdaFunction(weatherIngestLambda)],
    });

    new events.Rule(this, 'SatIngestSchedule', {
      ruleName: `${prefix}-sat-ingest-schedule`,
      schedule: events.Schedule.cron({ hour: '7', minute: '0' }), // Daily at 07:00 UTC
      targets: [new targets.LambdaFunction(satAgentLambda)],
    });

    // EventBridge Rules for Alerts
    const opsAlertsTopic = new sns.Topic(this, 'OpsAlertsTopic', {
      topicName: `${prefix}-ops-alerts`,
      displayName: 'Farm Operations Alerts',
    });

    alertsLambda.addEnvironment('SNS_TOPIC_ARN', opsAlertsTopic.topicArn);
    opsAlertsTopic.grantPublish(alertsLambda);

    new events.Rule(this, 'WeatherAlertRule', {
      ruleName: `${prefix}-weather-alert-rule`,
      eventPattern: {
        source: ['farm-ingest.weather'],
        detailType: ['weather_ingest_complete'],
      },
      targets: [new targets.LambdaFunction(alertsLambda)],
    });

    new events.Rule(this, 'SatAlertRule', {
      ruleName: `${prefix}-sat-alert-rule`,
      eventPattern: {
        source: ['farm-ingest.satellite'],
        detailType: ['sat_ingest_complete'],
      },
      targets: [new targets.LambdaFunction(alertsLambda)],
    });

    new events.Rule(this, 'HealthCheckSchedule', {
      ruleName: `${prefix}-health-check-schedule`,
      schedule: events.Schedule.rate(cdk.Duration.hours(24)),
      targets: [new targets.LambdaFunction(alertsLambda, {
        event: events.RuleTargetInput.fromObject({
          'detail-type': 'ingest_health_check',
        }),
      })],
    });

    // CloudFront for UI
    const uiBucket = new s3.Bucket(this, 'UIBucket', {
      bucketName: `${prefix}-bridge-ui`,
      websiteIndexDocument: 'index.html',
      websiteErrorDocument: 'error.html',
      publicReadAccess: false,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: env === 'prod' ? cdk.RemovalPolicy.RETAIN : cdk.RemovalPolicy.DESTROY,
    });

    const originAccessIdentity = new cloudfront.OriginAccessIdentity(this, 'OAI');
    uiBucket.grantRead(originAccessIdentity);

    const distribution = new cloudfront.Distribution(this, 'UIDistribution', {
      defaultBehavior: {
        origin: new cloudfrontOrigins.S3Origin(uiBucket, {
          originAccessIdentity,
        }),
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
      },
      defaultRootObject: 'index.html',
      errorResponses: [{
        httpStatus: 404,
        responseHttpStatus: 200,
        responsePagePath: '/index.html',
      }],
    });

    // WAF ACL
    const webAcl = new waf.CfnWebACL(this, 'ApiWebAcl', {
      scope: 'REGIONAL',
      defaultAction: { allow: {} },
      rules: [{
        name: 'RateLimitRule',
        priority: 1,
        statement: {
          rateBasedStatement: {
            limit: 2000,
            aggregateKeyType: 'IP',
          },
        },
        action: { block: {} },
        visibilityConfig: {
          sampledRequestsEnabled: true,
          cloudWatchMetricsEnabled: true,
          metricName: 'RateLimitRule',
        },
      }],
      visibilityConfig: {
        sampledRequestsEnabled: true,
        cloudWatchMetricsEnabled: true,
        metricName: `${prefix}-web-acl`,
      },
    });

    // Budget Alarms
    new budgets.CfnBudget(this, 'MonthlyBudget', {
      budget: {
        budgetName: `${prefix}-monthly-budget`,
        budgetType: 'COST',
        timeUnit: 'MONTHLY',
        budgetLimit: {
          amount: env === 'prod' ? 150 : 50,
          unit: 'USD',
        },
      },
      notificationsWithSubscribers: [{
        notification: {
          notificationType: 'ACTUAL',
          comparisonOperator: 'GREATER_THAN',
          threshold: 80,
          thresholdType: 'PERCENTAGE',
        },
        subscribers: [{
          subscriptionType: 'EMAIL',
          address: 'ops@greenstem.global',
        }],
      }],
    });

    // Outputs
    new cdk.CfnOutput(this, 'ApiUrl', {
      value: api.url!,
      description: 'API Gateway URL',
    });

    new cdk.CfnOutput(this, 'UIUrl', {
      value: `https://${distribution.distributionDomainName}`,
      description: 'CloudFront UI URL',
    });

    new cdk.CfnOutput(this, 'UserPoolId', {
      value: userPool.userPoolId,
      description: 'Cognito User Pool ID',
    });

    new cdk.CfnOutput(this, 'UserPoolClientId', {
      value: userPoolClient.userPoolClientId,
      description: 'Cognito User Pool Client ID',
    });
  }
}