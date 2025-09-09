import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as cloudwatch from 'aws-cdk-lib/aws-cloudwatch';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as subscriptions from 'aws-cdk-lib/aws-sns-subscriptions';
import * as cloudwatch_actions from 'aws-cdk-lib/aws-cloudwatch-actions';
import * as ce from 'aws-cdk-lib/aws-ce';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as stepfunctions from 'aws-cdk-lib/aws-stepfunctions';

export interface FarmObservabilityStackProps extends cdk.StackProps {
  farmValidatorFunction: lambda.Function;
  satelliteFunction: lambda.Function;
  api: apigateway.RestApi;
  farmOnboardStateMachine?: stepfunctions.StateMachine;
  satWeatherStateMachine?: stepfunctions.StateMachine;
  environment: string;
}

export class CNFarmObservabilityStack extends cdk.Stack {
  public readonly dashboard: cloudwatch.Dashboard;
  public readonly alertTopic: sns.Topic;
  public readonly alarms: cloudwatch.Alarm[];

  constructor(scope: Construct, id: string, props: FarmObservabilityStackProps) {
    super(scope, id, props);

    this.alarms = [];

    // Create SNS topic for alerts
    this.alertTopic = new sns.Topic(this, 'FarmOperationsAlerts', {
      topicName: 'C_N-Farm-Operations-Alerts',
      displayName: 'Farm Operations Monitoring Alerts',
      // Add email subscription in production
      // subscriptions: [
      //   new subscriptions.EmailSubscription('operations@greenstemglobal.com')
      // ]
    });

    // Create comprehensive dashboard
    this.dashboard = new cloudwatch.Dashboard(this, 'FarmOperationsDashboard', {
      dashboardName: 'C_N-Farm-Operations',
      widgets: [
        // Row 1: Lambda Function Health
        [
          new cloudwatch.GraphWidget({
            title: 'Farm Validator - Error Rate',
            width: 8,
            height: 6,
            left: [
              new cloudwatch.Metric({
                namespace: 'AWS/Lambda',
                metricName: 'Errors',
                dimensionsMap: {
                  FunctionName: props.farmValidatorFunction.functionName
                },
                statistic: 'Sum',
                period: cdk.Duration.minutes(5)
              }),
              new cloudwatch.Metric({
                namespace: 'AWS/Lambda',
                metricName: 'Invocations',
                dimensionsMap: {
                  FunctionName: props.farmValidatorFunction.functionName
                },
                statistic: 'Sum',
                period: cdk.Duration.minutes(5)
              })
            ]
          }),
          new cloudwatch.GraphWidget({
            title: 'Satellite Oracle - Processing Time',
            width: 8,
            height: 6,
            left: [
              new cloudwatch.Metric({
                namespace: 'AWS/Lambda',
                metricName: 'Duration',
                dimensionsMap: {
                  FunctionName: props.satelliteFunction.functionName
                },
                statistic: 'Average',
                period: cdk.Duration.minutes(5)
              }),
              new cloudwatch.Metric({
                namespace: 'AWS/Lambda',
                metricName: 'Duration',
                dimensionsMap: {
                  FunctionName: props.satelliteFunction.functionName
                },
                statistic: 'p95',
                period: cdk.Duration.minutes(5)
              })
            ]
          }),
          new cloudwatch.GraphWidget({
            title: 'Lambda Concurrent Executions',
            width: 8,
            height: 6,
            left: [
              new cloudwatch.Metric({
                namespace: 'AWS/Lambda',
                metricName: 'ConcurrentExecutions',
                dimensionsMap: {
                  FunctionName: props.farmValidatorFunction.functionName
                },
                statistic: 'Maximum',
                period: cdk.Duration.minutes(5)
              }),
              new cloudwatch.Metric({
                namespace: 'AWS/Lambda',
                metricName: 'ConcurrentExecutions',
                dimensionsMap: {
                  FunctionName: props.satelliteFunction.functionName
                },
                statistic: 'Maximum',
                period: cdk.Duration.minutes(5)
              })
            ]
          })
        ],

        // Row 2: API Gateway Performance
        [
          new cloudwatch.GraphWidget({
            title: 'API Gateway - Request Volume',
            width: 8,
            height: 6,
            left: [
              new cloudwatch.Metric({
                namespace: 'AWS/ApiGateway',
                metricName: 'Count',
                dimensionsMap: {
                  ApiName: props.api.restApiName!
                },
                statistic: 'Sum',
                period: cdk.Duration.minutes(5)
              })
            ]
          }),
          new cloudwatch.GraphWidget({
            title: 'API Gateway - Error Rates',
            width: 8,
            height: 6,
            left: [
              new cloudwatch.Metric({
                namespace: 'AWS/ApiGateway',
                metricName: '4XXError',
                dimensionsMap: {
                  ApiName: props.api.restApiName!
                },
                statistic: 'Sum',
                period: cdk.Duration.minutes(5)
              }),
              new cloudwatch.Metric({
                namespace: 'AWS/ApiGateway',
                metricName: '5XXError',
                dimensionsMap: {
                  ApiName: props.api.restApiName!
                },
                statistic: 'Sum',
                period: cdk.Duration.minutes(5)
              })
            ]
          }),
          new cloudwatch.GraphWidget({
            title: 'API Gateway - Response Times',
            width: 8,
            height: 6,
            left: [
              new cloudwatch.Metric({
                namespace: 'AWS/ApiGateway',
                metricName: 'Latency',
                dimensionsMap: {
                  ApiName: props.api.restApiName!
                },
                statistic: 'Average',
                period: cdk.Duration.minutes(5)
              }),
              new cloudwatch.Metric({
                namespace: 'AWS/ApiGateway',
                metricName: 'Latency',
                dimensionsMap: {
                  ApiName: props.api.restApiName!
                },
                statistic: 'p95',
                period: cdk.Duration.minutes(5)
              })
            ]
          })
        ],

        // Row 3: Step Functions Orchestration
        props.farmOnboardStateMachine ? [
          new cloudwatch.GraphWidget({
            title: 'Step Functions - Farm Onboarding',
            width: 12,
            height: 6,
            left: [
              new cloudwatch.Metric({
                namespace: 'AWS/States',
                metricName: 'ExecutionsSucceeded',
                dimensionsMap: {
                  StateMachineArn: props.farmOnboardStateMachine.stateMachineArn
                },
                statistic: 'Sum',
                period: cdk.Duration.minutes(5)
              }),
              new cloudwatch.Metric({
                namespace: 'AWS/States',
                metricName: 'ExecutionsFailed',
                dimensionsMap: {
                  StateMachineArn: props.farmOnboardStateMachine.stateMachineArn
                },
                statistic: 'Sum',
                period: cdk.Duration.minutes(5)
              }),
              new cloudwatch.Metric({
                namespace: 'AWS/States',
                metricName: 'ExecutionsTimedOut',
                dimensionsMap: {
                  StateMachineArn: props.farmOnboardStateMachine.stateMachineArn
                },
                statistic: 'Sum',
                period: cdk.Duration.minutes(5)
              })
            ]
          }),
          new cloudwatch.GraphWidget({
            title: 'Step Functions - Execution Duration',
            width: 12,
            height: 6,
            left: [
              new cloudwatch.Metric({
                namespace: 'AWS/States',
                metricName: 'ExecutionTime',
                dimensionsMap: {
                  StateMachineArn: props.farmOnboardStateMachine.stateMachineArn
                },
                statistic: 'Average',
                period: cdk.Duration.minutes(5)
              })
            ]
          })
        ] : [],

        // Row 4: Business Metrics
        [
          new cloudwatch.GraphWidget({
            title: 'Farm Management - Business Metrics',
            width: 8,
            height: 6,
            left: [
              new cloudwatch.Metric({
                namespace: 'C_N/FarmManagement',
                metricName: 'FarmOnboarded',
                statistic: 'Sum',
                period: cdk.Duration.minutes(15)
              }),
              new cloudwatch.Metric({
                namespace: 'C_N/FarmManagement',
                metricName: 'PlotCount',
                statistic: 'Sum',
                period: cdk.Duration.minutes(15)
              })
            ]
          }),
          new cloudwatch.GraphWidget({
            title: 'Oracle Processing - Success Rate',
            width: 8,
            height: 6,
            left: [
              new cloudwatch.Metric({
                namespace: 'C_N/Oracle',
                metricName: 'SatelliteProcessingSuccess',
                statistic: 'Sum',
                period: cdk.Duration.minutes(15)
              }),
              new cloudwatch.Metric({
                namespace: 'C_N/Oracle',
                metricName: 'SatelliteProcessingError',
                statistic: 'Sum',
                period: cdk.Duration.minutes(15)
              })
            ]
          }),
          new cloudwatch.GraphWidget({
            title: 'Data Quality Metrics',
            width: 8,
            height: 6,
            left: [
              new cloudwatch.Metric({
                namespace: 'C_N/Oracle',
                metricName: 'NDVI',
                statistic: 'Average',
                period: cdk.Duration.hours(1)
              }),
              new cloudwatch.Metric({
                namespace: 'C_N/Oracle',
                metricName: 'DataQuality',
                statistic: 'Average',
                period: cdk.Duration.hours(1)
              })
            ]
          })
        ],

        // Row 5: Infrastructure Health
        [
          new cloudwatch.GraphWidget({
            title: 'DynamoDB - Consumed Capacity',
            width: 8,
            height: 6,
            left: [
              new cloudwatch.Metric({
                namespace: 'AWS/DynamoDB',
                metricName: 'ConsumedReadCapacityUnits',
                dimensionsMap: {
                  TableName: 'C_N-FarmRegistry'
                },
                statistic: 'Sum',
                period: cdk.Duration.minutes(5)
              }),
              new cloudwatch.Metric({
                namespace: 'AWS/DynamoDB',
                metricName: 'ConsumedWriteCapacityUnits',
                dimensionsMap: {
                  TableName: 'C_N-FarmRegistry'
                },
                statistic: 'Sum',
                period: cdk.Duration.minutes(5)
              })
            ]
          }),
          new cloudwatch.GraphWidget({
            title: 'DynamoDB - Throttles',
            width: 8,
            height: 6,
            left: [
              new cloudwatch.Metric({
                namespace: 'AWS/DynamoDB',
                metricName: 'ThrottledRequests',
                dimensionsMap: {
                  TableName: 'C_N-FarmRegistry'
                },
                statistic: 'Sum',
                period: cdk.Duration.minutes(5)
              }),
              new cloudwatch.Metric({
                namespace: 'AWS/DynamoDB',
                metricName: 'ThrottledRequests',
                dimensionsMap: {
                  TableName: 'C_N-Oracle-FarmPlots'
                },
                statistic: 'Sum',
                period: cdk.Duration.minutes(5)
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
                dimensionsMap: {
                  Currency: 'USD'
                },
                region: 'us-east-1',
                statistic: 'Maximum',
                period: cdk.Duration.hours(6)
              })
            ]
          })
        ]
      ]
    });

    // Create Critical Alarms

    // Lambda Error Rate Alarm
    const farmValidatorErrorAlarm = new cloudwatch.Alarm(this, 'FarmValidatorErrorAlarm', {
      alarmName: 'C_N-FarmValidator-HighErrorRate',
      alarmDescription: 'Farm validator experiencing high error rate',
      metric: new cloudwatch.MathExpression({
        expression: '(errors / invocations) * 100',
        usingMetrics: {
          errors: new cloudwatch.Metric({
            namespace: 'AWS/Lambda',
            metricName: 'Errors',
            dimensionsMap: {
              FunctionName: props.farmValidatorFunction.functionName
            },
            statistic: 'Sum',
            period: cdk.Duration.minutes(5)
          }),
          invocations: new cloudwatch.Metric({
            namespace: 'AWS/Lambda',
            metricName: 'Invocations',
            dimensionsMap: {
              FunctionName: props.farmValidatorFunction.functionName
            },
            statistic: 'Sum',
            period: cdk.Duration.minutes(5)
          })
        }
      }),
      threshold: 5, // 5% error rate
      evaluationPeriods: 2,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
      treatMissingData: cloudwatch.TreatMissingData.NOT_BREACHING
    });
    farmValidatorErrorAlarm.addAlarmAction(new cloudwatch_actions.SnsAction(this.alertTopic));
    this.alarms.push(farmValidatorErrorAlarm);

    // API Gateway Error Rate Alarm
    const apiErrorRateAlarm = new cloudwatch.Alarm(this, 'APIHighErrorRate', {
      alarmName: 'C_N-FarmAPI-HighErrorRate',
      alarmDescription: 'Farm API experiencing high error rate',
      metric: new cloudwatch.MathExpression({
        expression: '((error4xx + error5xx) / requests) * 100',
        usingMetrics: {
          error4xx: new cloudwatch.Metric({
            namespace: 'AWS/ApiGateway',
            metricName: '4XXError',
            dimensionsMap: {
              ApiName: props.api.restApiName!
            },
            statistic: 'Sum'
          }),
          error5xx: new cloudwatch.Metric({
            namespace: 'AWS/ApiGateway',
            metricName: '5XXError',
            dimensionsMap: {
              ApiName: props.api.restApiName!
            },
            statistic: 'Sum'
          }),
          requests: new cloudwatch.Metric({
            namespace: 'AWS/ApiGateway',
            metricName: 'Count',
            dimensionsMap: {
              ApiName: props.api.restApiName!
            },
            statistic: 'Sum'
          })
        }
      }),
      threshold: 10, // 10% error rate
      evaluationPeriods: 3,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD
    });
    apiErrorRateAlarm.addAlarmAction(new cloudwatch_actions.SnsAction(this.alertTopic));
    this.alarms.push(apiErrorRateAlarm);

    // API Gateway High Latency Alarm
    const apiLatencyAlarm = new cloudwatch.Alarm(this, 'APIHighLatency', {
      alarmName: 'C_N-FarmAPI-HighLatency',
      alarmDescription: 'Farm API p95 latency above 5 seconds',
      metric: new cloudwatch.Metric({
        namespace: 'AWS/ApiGateway',
        metricName: 'Latency',
        dimensionsMap: {
          ApiName: props.api.restApiName!
        },
        statistic: 'p95',
        period: cdk.Duration.minutes(5)
      }),
      threshold: 5000, // 5 seconds
      evaluationPeriods: 3,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD
    });
    apiLatencyAlarm.addAlarmAction(new cloudwatch_actions.SnsAction(this.alertTopic));
    this.alarms.push(apiLatencyAlarm);

    // DynamoDB Throttling Alarm
    const dynamoThrottleAlarm = new cloudwatch.Alarm(this, 'DynamoThrottleAlarm', {
      alarmName: 'C_N-DynamoDB-Throttling',
      alarmDescription: 'DynamoDB tables experiencing throttling',
      metric: new cloudwatch.MathExpression({
        expression: 'farmRegistry + farmPlots',
        usingMetrics: {
          farmRegistry: new cloudwatch.Metric({
            namespace: 'AWS/DynamoDB',
            metricName: 'ThrottledRequests',
            dimensionsMap: {
              TableName: 'C_N-FarmRegistry'
            },
            statistic: 'Sum'
          }),
          farmPlots: new cloudwatch.Metric({
            namespace: 'AWS/DynamoDB',
            metricName: 'ThrottledRequests',
            dimensionsMap: {
              TableName: 'C_N-Oracle-FarmPlots'
            },
            statistic: 'Sum'
          })
        }
      }),
      threshold: 0,
      evaluationPeriods: 1,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD
    });
    dynamoThrottleAlarm.addAlarmAction(new cloudwatch_actions.SnsAction(this.alertTopic));
    this.alarms.push(dynamoThrottleAlarm);

    // Step Functions Failure Alarm (if provided)
    if (props.farmOnboardStateMachine) {
      const stepFunctionFailureAlarm = new cloudwatch.Alarm(this, 'StepFunctionFailures', {
        alarmName: 'C_N-StepFunction-FarmOnboard-Failures',
        alarmDescription: 'Farm onboarding Step Function failures',
        metric: new cloudwatch.Metric({
          namespace: 'AWS/States',
          metricName: 'ExecutionsFailed',
          dimensionsMap: {
            StateMachineArn: props.farmOnboardStateMachine.stateMachineArn
          },
          statistic: 'Sum',
          period: cdk.Duration.minutes(5)
        }),
        threshold: 1,
        evaluationPeriods: 1,
        comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD
      });
      stepFunctionFailureAlarm.addAlarmAction(new cloudwatch_actions.SnsAction(this.alertTopic));
      this.alarms.push(stepFunctionFailureAlarm);
    }

    // Daily Cost Anomaly Detection
    const dailyCostAlarm = new cloudwatch.Alarm(this, 'DailyCostAlarm', {
      alarmName: 'C_N-Daily-Cost-Spike',
      alarmDescription: 'Daily AWS costs exceeded $10 threshold',
      metric: new cloudwatch.Metric({
        namespace: 'AWS/Billing',
        metricName: 'EstimatedCharges',
        dimensionsMap: {
          Currency: 'USD'
        },
        region: 'us-east-1',
        statistic: 'Maximum',
        period: cdk.Duration.hours(6)
      }),
      threshold: 10,
      evaluationPeriods: 1,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD
    });
    dailyCostAlarm.addAlarmAction(new cloudwatch_actions.SnsAction(this.alertTopic));
    this.alarms.push(dailyCostAlarm);

    // Output dashboard URL and alert topic ARN
    new cdk.CfnOutput(this, 'DashboardURL', {
      value: `https://console.aws.amazon.com/cloudwatch/home?region=${this.region}#dashboards:name=${this.dashboard.dashboardName}`,
      description: 'CloudWatch Dashboard URL',
      exportName: 'CN-FarmOperations-Dashboard-URL'
    });

    new cdk.CfnOutput(this, 'AlertTopicArn', {
      value: this.alertTopic.topicArn,
      description: 'SNS Alert Topic ARN',
      exportName: 'CN-FarmOperations-AlertTopic-Arn'
    });

    new cdk.CfnOutput(this, 'AlarmCount', {
      value: String(this.alarms.length),
      description: 'Number of configured alarms',
      exportName: 'CN-FarmOperations-AlarmCount'
    });

    // Apply comprehensive tags
    cdk.Tags.of(this).add('WORLD', 'Continuum_Overworld');
    cdk.Tags.of(this).add('ORCHESTRATOR', 'C_N');
    cdk.Tags.of(this).add('ENV', props.environment);
    cdk.Tags.of(this).add('CAPABILITY', 'Observability');
    cdk.Tags.of(this).add('MONITORING', 'Enterprise-Grade');
  }
}