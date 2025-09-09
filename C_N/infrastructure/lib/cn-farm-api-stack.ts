import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as wafv2 from 'aws-cdk-lib/aws-wafv2';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as kms from 'aws-cdk-lib/aws-kms';

export interface FarmApiStackProps extends cdk.StackProps {
  farmValidatorFunction: lambda.Function;
  satelliteFunction: lambda.Function;
  kmsKey: kms.IKey;
  environment: string;
}

export class CNFarmApiStack extends cdk.Stack {
  public readonly api: apigateway.RestApi;
  public readonly webAcl: wafv2.CfnWebACL;

  constructor(scope: Construct, id: string, props: FarmApiStackProps) {
    super(scope, id, props);

    // Create CloudWatch log group for API Gateway
    const accessLogGroup = new logs.LogGroup(this, 'ApiAccessLogs', {
      logGroupName: '/aws/apigateway/C_N-FarmAPI-AccessLogs',
      retention: logs.RetentionDays.ONE_MONTH,
      encryptionKey: props.kmsKey,
      removalPolicy: cdk.RemovalPolicy.RETAIN
    });

    // Create JWT Authorizer (placeholder - would need Cognito User Pool in production)
    const jwtAuthorizer = new apigateway.CognitoUserPoolsAuthorizer(this, 'JwtAuthorizer', {
      cognitoUserPools: [], // Would reference actual User Pool
      authorizerName: 'C_N-Farm-JWT-Authorizer'
    });

    // Create API Gateway with enterprise settings
    this.api = new apigateway.RestApi(this, 'FarmAPI', {
      restApiName: 'C_N-Farm-Management-API',
      description: 'Enterprise farm management API with geometry validation',
      deployOptions: {
        stageName: 'prod',
        accessLogDestination: new apigateway.LogGroupLogDestination(accessLogGroup),
        accessLogFormat: apigateway.AccessLogFormat.custom(
          JSON.stringify({
            requestId: '$context.requestId',
            ip: '$context.identity.sourceIp',
            user: '$context.identity.user',
            requestTime: '$context.requestTime',
            httpMethod: '$context.httpMethod',
            resourcePath: '$context.resourcePath',
            status: '$context.status',
            protocol: '$context.protocol',
            responseLength: '$context.responseLength',
            responseLatency: '$context.responseTime',
            userAgent: '$context.identity.userAgent',
            correlationId: '$context.requestId'
          })
        ),
        cachingEnabled: true,
        cacheClusterEnabled: true,
        cacheClusterSize: '0.5',
        cacheTtl: cdk.Duration.minutes(5),
        throttlingRateLimit: 100,  // requests per second
        throttlingBurstLimit: 200,
        tracingEnabled: true  // X-Ray tracing
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
      },
      endpointConfiguration: {
        types: [apigateway.EndpointType.REGIONAL]
      },
      policy: new iam.PolicyDocument({
        statements: [
          new iam.PolicyStatement({
            effect: iam.Effect.ALLOW,
            principals: [new iam.AnyPrincipal()],
            actions: ['execute-api:Invoke'],
            resources: ['*'],
            conditions: {
              StringEquals: {
                'aws:SecureTransport': 'true'
              }
            }
          })
        ]
      })
    });

    // Create API Key for additional protection
    const apiKey = new apigateway.ApiKey(this, 'FarmAPIKey', {
      apiKeyName: 'C_N-FarmAPI-Key',
      description: 'API key for farm management operations'
    });

    // Create Usage Plan
    const usagePlan = new apigateway.UsagePlan(this, 'FarmAPIUsagePlan', {
      name: 'FarmManagement',
      description: 'Usage plan for farm onboarding and management',
      throttle: {
        rateLimit: 10,  // requests per second
        burstLimit: 20
      },
      quota: {
        limit: 1000,
        period: apigateway.Period.DAY
      },
      apiStages: [{
        api: this.api,
        stage: this.api.deploymentStage
      }]
    });

    // Associate API key with usage plan
    usagePlan.addApiKey(apiKey);

    // Create resources and methods
    const adminResource = this.api.root.addResource('admin');
    const farmsResource = adminResource.addResource('farms');
    const plotsResource = adminResource.addResource('plots');

    // Farm onboarding endpoint
    const farmValidatorIntegration = new apigateway.LambdaIntegration(props.farmValidatorFunction, {
      requestTemplates: {
        'application/json': JSON.stringify({
          body: '$input.body',
          requestContext: {
            requestId: '$context.requestId',
            authorizer: {
              claims: {
                sub: '$context.authorizer.claims.sub'
              }
            }
          },
          headers: {
            'X-Correlation-Id': '$input.params(\'X-Correlation-Id\')',
            'User-Agent': '$input.params(\'User-Agent\')'
          }
        })
      },
      integrationResponses: [{
        statusCode: '200',
        responseParameters: {
          'method.response.header.X-Correlation-Id': 'integration.response.header.X-Correlation-Id',
          'method.response.header.X-Farm-ID': 'integration.response.header.X-Farm-ID'
        }
      }]
    });

    farmsResource.addMethod('POST', farmValidatorIntegration, {
      authorizer: jwtAuthorizer,
      apiKeyRequired: true,
      methodResponses: [{
        statusCode: '200',
        responseParameters: {
          'method.response.header.X-Correlation-Id': true,
          'method.response.header.X-Farm-ID': true,
          'method.response.header.Access-Control-Allow-Origin': true
        }
      }]
    });

    // Satellite data endpoint
    const satelliteIntegration = new apigateway.LambdaIntegration(props.satelliteFunction, {
      requestTemplates: {
        'application/json': JSON.stringify({
          body: '$input.body',
          requestContext: {
            requestId: '$context.requestId'
          },
          headers: {
            'X-Correlation-Id': '$input.params(\'X-Correlation-Id\')'
          }
        })
      }
    });

    plotsResource.addResource('satellite').addMethod('POST', satelliteIntegration, {
      authorizer: jwtAuthorizer,
      apiKeyRequired: true
    });

    // Create WAF Web ACL
    this.webAcl = new wafv2.CfnWebACL(this, 'FarmAPIWebACL', {
      scope: 'REGIONAL',
      defaultAction: { allow: {} },
      name: 'C_N-FarmAPI-WAF',
      description: 'WAF for C_N Farm Management API',
      rules: [
        {
          name: 'RateLimitRule',
          priority: 1,
          statement: {
            rateBasedStatement: {
              limit: 100,  // 100 requests per 5 minutes
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
          name: 'GeoMatchRule',
          priority: 2,
          statement: {
            andStatement: {
              statements: [
                {
                  byteMatchStatement: {
                    searchString: '/admin/',
                    fieldToMatch: { uriPath: {} },
                    textTransformations: [{
                      priority: 0,
                      type: 'LOWERCASE'
                    }],
                    positionalConstraint: 'STARTS_WITH'
                  }
                },
                {
                  notStatement: {
                    statement: {
                      geoMatchStatement: {
                        countryCodes: ['KE', 'US', 'GB', 'DE', 'FR'] // Kenya, US, UK, Germany, France
                      }
                    }
                  }
                }
              ]
            }
          },
          action: { block: {} },
          visibilityConfig: {
            sampledRequestsEnabled: true,
            cloudWatchMetricsEnabled: true,
            metricName: 'GeoMatchRule'
          }
        },
        {
          name: 'SQLiRule',
          priority: 3,
          statement: {
            managedRuleGroupStatement: {
              vendorName: 'AWS',
              name: 'AWSManagedRulesSQLiRuleSet'
            }
          },
          action: { block: {} },
          visibilityConfig: {
            sampledRequestsEnabled: true,
            cloudWatchMetricsEnabled: true,
            metricName: 'SQLiRule'
          },
          overrideAction: { none: {} }
        },
        {
          name: 'CommonRuleSet',
          priority: 4,
          statement: {
            managedRuleGroupStatement: {
              vendorName: 'AWS',
              name: 'AWSManagedRulesCommonRuleSet'
            }
          },
          action: { block: {} },
          visibilityConfig: {
            sampledRequestsEnabled: true,
            cloudWatchMetricsEnabled: true,
            metricName: 'CommonRuleSet'
          },
          overrideAction: { none: {} }
        }
      ],
      visibilityConfig: {
        sampledRequestsEnabled: true,
        cloudWatchMetricsEnabled: true,
        metricName: 'FarmAPIWebACL'
      },
      tags: [
        { key: 'WORLD', value: 'Continuum_Overworld' },
        { key: 'ORCHESTRATOR', value: 'C_N' },
        { key: 'ENV', value: props.environment },
        { key: 'CAPABILITY', value: 'API-Security' }
      ]
    });

    // Associate WAF with API Gateway
    new wafv2.CfnWebACLAssociation(this, 'WebACLAssociation', {
      resourceArn: this.api.arnForExecuteApi(),
      webAclArn: this.webAcl.attrArn
    });

    // Create custom domain (placeholder - requires certificate)
    // const domain = new apigateway.DomainName(this, 'FarmAPIDomain', {
    //   domainName: 'api-farms.greenstemglobal.com',
    //   certificate: certificate,
    //   endpointType: apigateway.EndpointType.REGIONAL
    // });

    // Outputs
    new cdk.CfnOutput(this, 'FarmAPIUrl', {
      value: this.api.url,
      description: 'Farm Management API URL',
      exportName: 'CN-FarmAPI-URL'
    });

    new cdk.CfnOutput(this, 'FarmAPIId', {
      value: this.api.restApiId,
      description: 'Farm Management API ID',
      exportName: 'CN-FarmAPI-ID'
    });

    new cdk.CfnOutput(this, 'APIKeyId', {
      value: apiKey.keyId,
      description: 'Farm API Key ID',
      exportName: 'CN-FarmAPI-KeyId'
    });

    new cdk.CfnOutput(this, 'WebACLArn', {
      value: this.webAcl.attrArn,
      description: 'WAF Web ACL ARN',
      exportName: 'CN-FarmAPI-WebACL-Arn'
    });

    // Example API usage documentation
    new cdk.CfnOutput(this, 'APIUsageExamples', {
      value: JSON.stringify({
        farmOnboarding: {
          method: 'POST',
          url: `${this.api.url}admin/farms`,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer JWT_TOKEN',
            'X-API-Key': 'API_KEY',
            'X-Correlation-Id': 'unique-correlation-id'
          },
          body: {
            featureCollection: {
              type: 'FeatureCollection',
              features: [
                {
                  type: 'Feature',
                  properties: { type: 'farm', name: 'Test Farm' },
                  geometry: { type: 'Polygon', coordinates: [] }
                }
              ]
            }
          }
        },
        satelliteData: {
          method: 'POST',
          url: `${this.api.url}admin/plots/satellite`,
          headers: {
            'Authorization': 'Bearer JWT_TOKEN',
            'X-API-Key': 'API_KEY'
          },
          body: {
            plotId: 'FARM-123-P1',
            farmId: 'FARM-123'
          }
        }
      }),
      description: 'API Usage Examples'
    });

    // Apply comprehensive tags
    cdk.Tags.of(this).add('WORLD', 'Continuum_Overworld');
    cdk.Tags.of(this).add('ORCHESTRATOR', 'C_N');
    cdk.Tags.of(this).add('ENV', props.environment);
    cdk.Tags.of(this).add('CAPABILITY', 'FarmAPI');
    cdk.Tags.of(this).add('SECURITY', 'WAF-JWT-ApiKey');
    cdk.Tags.of(this).add('COMPLIANCE', 'Enterprise-Grade');
  }
}