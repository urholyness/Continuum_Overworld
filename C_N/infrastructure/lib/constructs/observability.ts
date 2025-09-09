import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as cloudwatch from 'aws-cdk-lib/aws-cloudwatch';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as cloudwatch_actions from 'aws-cdk-lib/aws-cloudwatch-actions';

export interface ObservabilityProps {
  alertTopic: sns.Topic;
  apiName: string;
  environment: string;
}

export class ObservabilityConstruct extends Construct {
  public readonly dashboard: cloudwatch.Dashboard;
  public readonly alarms: cloudwatch.Alarm[];

  constructor(scope: Construct, id: string, props: ObservabilityProps) {
    super(scope, id);

    this.alarms = [];

    // Create comprehensive dashboard
    this.dashboard = new cloudwatch.Dashboard(this, 'CNFleetHealthDashboard', {
      dashboardName: 'C_N-Fleet-Health-Production',
      widgets: [
        // Row 1: Step Functions Health
        [
          new cloudwatch.GraphWidget({
            title: 'Step Function Execution Status',
            width: 12,
            height: 6,
            left: [
              new cloudwatch.Metric({
                namespace: 'AWS/States',
                metricName: 'ExecutionsSucceeded',
                statistic: 'Sum',
                period: cdk.Duration.minutes(5)
              }),
              new cloudwatch.Metric({
                namespace: 'AWS/States',
                metricName: 'ExecutionsFailed',
                statistic: 'Sum',
                period: cdk.Duration.minutes(5)
              }),
              new cloudwatch.Metric({
                namespace: 'AWS/States',
                metricName: 'ExecutionsTimedOut',
                statistic: 'Sum',
                period: cdk.Duration.minutes(5)
              })
            ]
          }),
          new cloudwatch.GraphWidget({
            title: 'Step Function Duration (avg)',
            width: 12,
            height: 6,
            left: [
              new cloudwatch.Metric({
                namespace: 'AWS/States',
                metricName: 'ExecutionTime',
                statistic: 'Average',
                period: cdk.Duration.minutes(5)
              })
            ]
          })
        ],
        
        // Row 2: API Gateway Performance
        [
          new cloudwatch.GraphWidget({
            title: 'API Gateway Request Volume',
            width: 8,
            height: 6,
            left: [
              new cloudwatch.Metric({
                namespace: 'AWS/ApiGateway',
                metricName: 'Count',
                dimensionsMap: { ApiName: props.apiName },
                statistic: 'Sum',
                period: cdk.Duration.minutes(5)
              })
            ]
          }),
          new cloudwatch.GraphWidget({
            title: 'API Cache Hit Rate',
            width: 8,
            height: 6,
            left: [
              new cloudwatch.MathExpression({
                expression: '(cacheHit / (cacheHit + cacheMiss)) * 100',
                label: 'Cache Hit Rate %',
                usingMetrics: {
                  cacheHit: new cloudwatch.Metric({
                    namespace: 'AWS/ApiGateway',
                    metricName: 'CacheHitCount',
                    dimensionsMap: { ApiName: props.apiName },
                    statistic: 'Sum'
                  }),
                  cacheMiss: new cloudwatch.Metric({
                    namespace: 'AWS/ApiGateway',
                    metricName: 'CacheMissCount',
                    dimensionsMap: { ApiName: props.apiName },
                    statistic: 'Sum'
                  })
                }
              })
            ]
          }),
          new cloudwatch.GraphWidget({
            title: 'API Response Times (p95)',
            width: 8,
            height: 6,
            left: [
              new cloudwatch.Metric({
                namespace: 'AWS/ApiGateway',
                metricName: 'Latency',
                dimensionsMap: { ApiName: props.apiName },
                statistic: 'p95',
                period: cdk.Duration.minutes(5)
              })
            ]
          })
        ],
        
        // Row 3: Lambda Performance
        [
          new cloudwatch.GraphWidget({
            title: 'Lambda Error Rates',
            width: 12,
            height: 6,
            left: [
              new cloudwatch.Metric({
                namespace: 'AWS/Lambda',
                metricName: 'Errors',
                statistic: 'Sum',
                period: cdk.Duration.minutes(5)
              }),
              new cloudwatch.Metric({
                namespace: 'AWS/Lambda',
                metricName: 'Throttles',
                statistic: 'Sum',
                period: cdk.Duration.minutes(5)
              })
            ]
          }),
          new cloudwatch.GraphWidget({
            title: 'Lambda Duration (avg)',
            width: 12,
            height: 6,
            left: [
              new cloudwatch.Metric({
                namespace: 'AWS/Lambda',
                metricName: 'Duration',
                statistic: 'Average',
                period: cdk.Duration.minutes(5)
              })
            ]
          })
        ],
        
        // Row 4: DynamoDB and Business Metrics
        [
          new cloudwatch.GraphWidget({
            title: 'DynamoDB Read/Write Capacity',
            width: 8,
            height: 6,
            left: [
              new cloudwatch.Metric({
                namespace: 'AWS/DynamoDB',
                metricName: 'ConsumedReadCapacityUnits',
                statistic: 'Sum',
                period: cdk.Duration.minutes(5)
              })
            ],
            right: [
              new cloudwatch.Metric({
                namespace: 'AWS/DynamoDB',
                metricName: 'ConsumedWriteCapacityUnits',
                statistic: 'Sum',
                period: cdk.Duration.minutes(5)
              })
            ]
          }),
          new cloudwatch.GraphWidget({
            title: 'C_N Business Metrics',
            width: 8,
            height: 6,
            left: [
              new cloudwatch.Metric({
                namespace: 'C_N/Oracle',
                metricName: 'SatelliteIngestSuccess',
                statistic: 'Sum',
                period: cdk.Duration.minutes(15)
              }),
              new cloudwatch.Metric({
                namespace: 'C_N/Ledger',
                metricName: 'TransactionSuccess',
                statistic: 'Sum',
                period: cdk.Duration.minutes(15)
              })
            ]
          }),
          new cloudwatch.GraphWidget({
            title: 'Daily Cost Tracking (USD)',
            width: 8,
            height: 6,
            left: [
              new cloudwatch.Metric({
                namespace: 'AWS/Billing',
                metricName: 'EstimatedCharges',
                dimensionsMap: { Currency: 'USD' },
                region: 'us-east-1',
                statistic: 'Maximum',
                period: cdk.Duration.hours(6)
              })
            ]
          })
        ],
        
        // Row 5: Security and WAF
        [
          new cloudwatch.GraphWidget({
            title: 'WAF Blocked Requests',
            width: 12,
            height: 6,
            left: [
              new cloudwatch.Metric({
                namespace: 'AWS/WAFV2',
                metricName: 'BlockedRequests',
                dimensionsMap: { 
                  WebACL: 'C_N-Trace-Composer-WAF',
                  Region: 'us-east-1'
                },
                statistic: 'Sum',
                period: cdk.Duration.minutes(5)
              })
            ]
          }),
          new cloudwatch.GraphWidget({
            title: 'X-Ray Service Map Health',
            width: 12,
            height: 6,
            left: [
              new cloudwatch.Metric({
                namespace: 'AWS/X-Ray',
                metricName: 'ResponseTime',
                statistic: 'Average',
                period: cdk.Duration.minutes(5)
              }),
              new cloudwatch.Metric({
                namespace: 'AWS/X-Ray',
                metricName: 'ErrorRate',
                statistic: 'Average',
                period: cdk.Duration.minutes(5)
              })
            ]
          })
        ]
      ]
    });

    // Create critical alarms
    
    // Step Function failure alarm
    const stepFunctionFailureAlarm = new cloudwatch.Alarm(this, 'StepFunctionFailures', {
      alarmName: 'C_N-StepFunction-Failures',
      alarmDescription: 'Step Function executions failing',
      metric: new cloudwatch.Metric({
        namespace: 'AWS/States',
        metricName: 'ExecutionsFailed',
        statistic: 'Sum',
        period: cdk.Duration.minutes(5)
      }),
      threshold: 3,
      evaluationPeriods: 2,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD
    });
    stepFunctionFailureAlarm.addAlarmAction(new cloudwatch_actions.SnsAction(props.alertTopic));
    this.alarms.push(stepFunctionFailureAlarm);

    // API Gateway high error rate alarm
    const apiErrorRateAlarm = new cloudwatch.Alarm(this, 'ApiHighErrorRate', {
      alarmName: 'C_N-API-High-Error-Rate',
      alarmDescription: 'API Gateway error rate above 5%',
      metric: new cloudwatch.MathExpression({
        expression: '(errors / requests) * 100',
        usingMetrics: {
          errors: new cloudwatch.Metric({
            namespace: 'AWS/ApiGateway',
            metricName: '5XXError',
            dimensionsMap: { ApiName: props.apiName },
            statistic: 'Sum'
          }),
          requests: new cloudwatch.Metric({
            namespace: 'AWS/ApiGateway',
            metricName: 'Count',
            dimensionsMap: { ApiName: props.apiName },
            statistic: 'Sum'
          })
        }
      }),
      threshold: 5,
      evaluationPeriods: 3,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD
    });
    apiErrorRateAlarm.addAlarmAction(new cloudwatch_actions.SnsAction(props.alertTopic));
    this.alarms.push(apiErrorRateAlarm);

    // API Gateway high latency alarm
    const apiLatencyAlarm = new cloudwatch.Alarm(this, 'ApiHighLatency', {
      alarmName: 'C_N-API-High-Latency',
      alarmDescription: 'API Gateway p95 latency above 2 seconds',
      metric: new cloudwatch.Metric({
        namespace: 'AWS/ApiGateway',
        metricName: 'Latency',
        dimensionsMap: { ApiName: props.apiName },
        statistic: 'p95',
        period: cdk.Duration.minutes(5)
      }),
      threshold: 2000, // 2 seconds in milliseconds
      evaluationPeriods: 3,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD
    });
    apiLatencyAlarm.addAlarmAction(new cloudwatch_actions.SnsAction(props.alertTopic));
    this.alarms.push(apiLatencyAlarm);

    // Lambda error rate alarm
    const lambdaErrorAlarm = new cloudwatch.Alarm(this, 'LambdaErrors', {
      alarmName: 'C_N-Lambda-Errors',
      alarmDescription: 'Lambda functions experiencing errors',
      metric: new cloudwatch.Metric({
        namespace: 'AWS/Lambda',
        metricName: 'Errors',
        statistic: 'Sum',
        period: cdk.Duration.minutes(5)
      }),
      threshold: 10,
      evaluationPeriods: 2,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD
    });
    lambdaErrorAlarm.addAlarmAction(new cloudwatch_actions.SnsAction(props.alertTopic));
    this.alarms.push(lambdaErrorAlarm);

    // Daily cost alarm
    const dailyCostAlarm = new cloudwatch.Alarm(this, 'DailyCostAlarm', {
      alarmName: 'C_N-Daily-Cost-Exceeded',
      alarmDescription: 'Daily AWS costs exceeded $25 threshold',
      metric: new cloudwatch.Metric({
        namespace: 'AWS/Billing',
        metricName: 'EstimatedCharges',
        dimensionsMap: { Currency: 'USD' },
        region: 'us-east-1',
        statistic: 'Maximum',
        period: cdk.Duration.hours(6)
      }),
      threshold: 25,
      evaluationPeriods: 1,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD
    });
    dailyCostAlarm.addAlarmAction(new cloudwatch_actions.SnsAction(props.alertTopic));
    this.alarms.push(dailyCostAlarm);

    // DynamoDB throttling alarm
    const dynamoThrottleAlarm = new cloudwatch.Alarm(this, 'DynamoThrottles', {
      alarmName: 'C_N-DynamoDB-Throttles',
      alarmDescription: 'DynamoDB requests being throttled',
      metric: new cloudwatch.Metric({
        namespace: 'AWS/DynamoDB',
        metricName: 'ThrottledRequests',
        statistic: 'Sum',
        period: cdk.Duration.minutes(5)
      }),
      threshold: 5,
      evaluationPeriods: 2,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD
    });
    dynamoThrottleAlarm.addAlarmAction(new cloudwatch_actions.SnsAction(props.alertTopic));
    this.alarms.push(dynamoThrottleAlarm);

    // Apply tags
    cdk.Tags.of(this).add('WORLD', 'Continuum_Overworld');
    cdk.Tags.of(this).add('ORCHESTRATOR', 'C_N');
    cdk.Tags.of(this).add('ENV', props.environment);
    cdk.Tags.of(this).add('CAPABILITY', 'Observability');
  }
}