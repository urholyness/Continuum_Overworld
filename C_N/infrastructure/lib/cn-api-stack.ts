import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as wafv2 from 'aws-cdk-lib/aws-wafv2';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as cloudwatch from 'aws-cdk-lib/aws-cloudwatch';
import * as logs from 'aws-cdk-lib/aws-logs';

export interface CNApiStackProps extends cdk.StackProps {
  traceComposerFunction: lambda.Function;
  shareLinkMintFunction: lambda.Function;
  tokenAuthorizerFunction: lambda.Function;
}

export class CNApiStack extends cdk.Stack {
  public readonly api: apigateway.RestApi;
  public readonly webAcl: wafv2.CfnWebACL;

  constructor(scope: Construct, id: string, props: CNApiStackProps) {
    super(scope, id, props);

    // Create CloudWatch Log Group for API access logs
    const accessLogGroup = new logs.LogGroup(this, 'ApiAccessLogs', {
      logGroupName: '/aws/apigateway/C_N-Trace-Composer-Access',
      retention: logs.RetentionDays.ONE_MONTH
    });

    // Create API Gateway with caching enabled
    this.api = new apigateway.RestApi(this, 'TraceComposerAPI', {
      restApiName: 'C_N-Trace-Composer',
      description: 'Public API for GreenStem Global product and funds tracing',
      endpointConfiguration: {
        types: [apigateway.EndpointType.REGIONAL]
      },
      deployOptions: {
        stageName: 'prod',
        cachingEnabled: true,
        cacheClusterEnabled: true,
        cacheClusterSize: '0.5', // 0.5 GB cache cluster
        cacheTtl: cdk.Duration.seconds(300), // 5 minutes
        cacheDataEncrypted: true,
        cacheKeyParameters: ['method.request.querystring.batchId', 'method.request.querystring.contributionId'],
        loggingLevel: apigateway.MethodLoggingLevel.INFO,
        dataTraceEnabled: true,
        accessLogDestination: apigateway.LogGroupLogDestination.fromLogGroup(accessLogGroup),
        accessLogFormat: apigateway.AccessLogFormat.custom(
          JSON.stringify({
            requestId: '$requestId',
            ip: '$sourceIp',
            user: '$context.identity.user',
            requestTime: '$requestTime',
            httpMethod: '$httpMethod',
            resourcePath: '$resourcePath',
            status: '$status',
            protocol: '$protocol',
            responseLength: '$responseLength',
            responseTime: '$responseTime',
            cacheHitStatus: '$cacheHitStatus',
            correlationId: '$requestHeader.X-Correlation-Id'
          })
        ),
        throttle: {
          rateLimit: 2000,
          burstLimit: 5000
        }
      },
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
        allowHeaders: [
          'Content-Type',
          'X-Amz-Date',
          'Authorization',
          'X-Api-Key',
          'X-Amz-Security-Token',
          'X-Correlation-Id'
        ]
      }
    });

    // Create custom authorizer
    const authorizer = new apigateway.TokenAuthorizer(this, 'TraceAuthorizer', {
      handler: props.tokenAuthorizerFunction,
      resultsCacheTtl: cdk.Duration.minutes(5),
      identitySource: 'method.request.header.Authorization'
    });

    // Create Lambda integrations with caching
    const traceComposerIntegration = new apigateway.LambdaIntegration(props.traceComposerFunction, {
      cacheNamespace: 'trace-composer',
      cacheKeyParameters: ['method.request.querystring.batchId', 'method.request.querystring.contributionId'],
      requestTemplates: {
        'application/json': JSON.stringify({
          httpMethod: '$context.httpMethod',
          path: '$context.resourcePath',
          queryStringParameters: '$input.params().querystring',
          headers: '$input.params().header',
          body: '$util.escapeJavaScript($input.body)',
          requestContext: {
            requestId: '$context.requestId',
            identity: {
              sourceIp: '$context.identity.sourceIp',
              userAgent: '$context.identity.userAgent'
            }
          }
        })
      }
    });

    // Public trace endpoints
    const publicResource = this.api.root.addResource('public');
    const traceResource = publicResource.addResource('trace');
    
    // Product trace endpoint: GET /public/trace/product?batchId=24-0901-FB
    const productResource = traceResource.addResource('product');
    productResource.addMethod('GET', traceComposerIntegration, {
      authorizer,
      requestParameters: {
        'method.request.querystring.batchId': true
      },
      requestValidatorOptions: {
        validateRequestParameters: true
      },
      methodResponses: [
        {
          statusCode: '200',
          responseParameters: {
            'method.response.header.Cache-Control': true,
            'method.response.header.X-Correlation-Id': true
          }
        },
        {
          statusCode: '404',
          responseParameters: {
            'method.response.header.X-Correlation-Id': true
          }
        }
      ]
    });

    // Funds trace endpoint: GET /public/trace/funds?contributionId=INV-2024-001
    const fundsResource = traceResource.addResource('funds');
    fundsResource.addMethod('GET', traceComposerIntegration, {
      authorizer,
      requestParameters: {
        'method.request.querystring.contributionId': true
      },
      requestValidatorOptions: {
        validateRequestParameters: true
      },
      methodResponses: [
        {
          statusCode: '200',
          responseParameters: {
            'method.response.header.Cache-Control': true,
            'method.response.header.X-Correlation-Id': true
          }
        },
        {
          statusCode: '404',
          responseParameters: {
            'method.response.header.X-Correlation-Id': true
          }
        }
      ]
    });

    // Share link generation: POST /public/share
    const shareResource = publicResource.addResource('share');
    shareResource.addMethod('POST', new apigateway.LambdaIntegration(props.shareLinkMintFunction), {
      authorizer,
      requestValidatorOptions: {
        validateRequestBody: true,
        validateRequestParameters: true
      }
    });

    // Health check endpoint (no auth required)
    const healthResource = this.api.root.addResource('health');
    healthResource.addMethod('GET', new apigateway.MockIntegration({
      integrationResponses: [
        {
          statusCode: '200',
          responseTemplates: {
            'application/json': JSON.stringify({
              status: 'healthy',
              service: 'C_N-Trace-Composer',
              timestamp: '$context.requestTime',
              version: '1.0.0'
            })
          }
        }
      ],
      requestTemplates: {
        'application/json': '{"statusCode": 200}'
      }
    }), {
      methodResponses: [{ statusCode: '200' }]
    });

    // Create WAF WebACL with comprehensive rules
    this.webAcl = new wafv2.CfnWebACL(this, 'TraceComposerWAF', {
      name: 'C_N-Trace-Composer-WAF',
      scope: 'REGIONAL',
      defaultAction: { allow: {} },
      visibilityConfig: {
        sampledRequestsEnabled: true,
        cloudWatchMetricsEnabled: true,
        metricName: 'C_N-Trace-Composer-WAF'
      },
      rules: [
        {
          name: 'RateLimitRule',
          priority: 1,
          statement: {
            rateBasedStatement: {
              limit: 2000, // 2000 requests per 5 minutes per IP
              aggregateKeyType: 'IP'
            }
          },
          action: { block: {} },
          visibilityConfig: {
            sampledRequestsEnabled: true,
            cloudWatchMetricsEnabled: true,
            metricName: 'RateLimitRule'
          }
        },
        {
          name: 'AWSManagedRulesCommonRuleSet',
          priority: 2,
          overrideAction: { none: {} },
          statement: {
            managedRuleGroupStatement: {
              vendorName: 'AWS',
              name: 'AWSManagedRulesCommonRuleSet'
            }
          },
          visibilityConfig: {
            sampledRequestsEnabled: true,
            cloudWatchMetricsEnabled: true,
            metricName: 'CommonRuleSet'
          }
        },
        {
          name: 'AWSManagedRulesKnownBadInputsRuleSet',
          priority: 3,
          overrideAction: { none: {} },
          statement: {
            managedRuleGroupStatement: {
              vendorName: 'AWS',
              name: 'AWSManagedRulesKnownBadInputsRuleSet'
            }
          },
          visibilityConfig: {
            sampledRequestsEnabled: true,
            cloudWatchMetricsEnabled: true,
            metricName: 'BadInputsRuleSet'
          }
        },
        {
          name: 'AWSManagedRulesAmazonIpReputationList',
          priority: 4,
          overrideAction: { none: {} },
          statement: {
            managedRuleGroupStatement: {
              vendorName: 'AWS',
              name: 'AWSManagedRulesAmazonIpReputationList'
            }
          },
          visibilityConfig: {
            sampledRequestsEnabled: true,
            cloudWatchMetricsEnabled: true,
            metricName: 'IpReputationList'
          }
        }
      ]
    });

    // Associate WAF with API Gateway stage
    new wafv2.CfnWebACLAssociation(this, 'ApiWafAssociation', {
      resourceArn: this.api.deploymentStage.stageArn,
      webAclArn: this.webAcl.attrArn
    });

    // Create CloudWatch dashboard for API monitoring
    new cloudwatch.Dashboard(this, 'TraceComposerDashboard', {
      dashboardName: 'C_N-Trace-Composer-API',
      widgets: [
        [
          new cloudwatch.GraphWidget({
            title: 'API Requests',
            left: [
              new cloudwatch.Metric({
                namespace: 'AWS/ApiGateway',
                metricName: 'Count',
                dimensionsMap: { ApiName: this.api.restApiName },
                statistic: 'Sum'
              })
            ]
          }),
          new cloudwatch.GraphWidget({
            title: 'Cache Hit Rate',
            left: [
              new cloudwatch.MathExpression({
                expression: '(cacheHit / (cacheHit + cacheMiss)) * 100',
                usingMetrics: {
                  cacheHit: new cloudwatch.Metric({
                    namespace: 'AWS/ApiGateway',
                    metricName: 'CacheHitCount',
                    dimensionsMap: { ApiName: this.api.restApiName },
                    statistic: 'Sum'
                  }),
                  cacheMiss: new cloudwatch.Metric({
                    namespace: 'AWS/ApiGateway',
                    metricName: 'CacheMissCount',
                    dimensionsMap: { ApiName: this.api.restApiName },
                    statistic: 'Sum'
                  })
                }
              })
            ]
          })
        ],
        [
          new cloudwatch.GraphWidget({
            title: 'Response Times (p50, p90, p99)',
            left: [
              new cloudwatch.Metric({
                namespace: 'AWS/ApiGateway',
                metricName: 'Latency',
                dimensionsMap: { ApiName: this.api.restApiName },
                statistic: 'p50'
              }),
              new cloudwatch.Metric({
                namespace: 'AWS/ApiGateway',
                metricName: 'Latency',
                dimensionsMap: { ApiName: this.api.restApiName },
                statistic: 'p90'
              }),
              new cloudwatch.Metric({
                namespace: 'AWS/ApiGateway',
                metricName: 'Latency',
                dimensionsMap: { ApiName: this.api.restApiName },
                statistic: 'p99'
              })
            ]
          }),
          new cloudwatch.GraphWidget({
            title: 'WAF Blocked Requests',
            left: [
              new cloudwatch.Metric({
                namespace: 'AWS/WAFV2',
                metricName: 'BlockedRequests',
                dimensionsMap: { 
                  WebACL: 'C_N-Trace-Composer-WAF',
                  Region: 'us-east-1'
                },
                statistic: 'Sum'
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
    cdk.Tags.of(this).add('DIVISION', 'PublicAPI');
    cdk.Tags.of(this).add('CAPABILITY', 'TraceComposer');

    // Outputs
    new cdk.CfnOutput(this, 'ApiUrl', {
      value: this.api.url,
      description: 'Trace Composer API base URL'
    });

    new cdk.CfnOutput(this, 'ProductTraceEndpoint', {
      value: `${this.api.url}public/trace/product?batchId=24-0901-FB`,
      description: 'Product trace endpoint example'
    });

    new cdk.CfnOutput(this, 'FundsTraceEndpoint', {
      value: `${this.api.url}public/trace/funds?contributionId=INV-2024-001`,
      description: 'Funds trace endpoint example'
    });

    new cdk.CfnOutput(this, 'WafAclArn', {
      value: this.webAcl.attrArn,
      description: 'WAF WebACL ARN'
    });
  }
}