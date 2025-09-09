import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as kms from 'aws-cdk-lib/aws-kms';
import * as iam from 'aws-cdk-lib/aws-iam';

export interface FarmStorageStackProps extends cdk.StackProps {
  kmsKey: kms.IKey;
  environment: string;
}

export class CNFarmStorageStack extends cdk.Stack {
  public readonly geometryBucket: s3.Bucket;
  public readonly tilesBucket: s3.Bucket;

  constructor(scope: Construct, id: string, props: FarmStorageStackProps) {
    super(scope, id, props);

    // 1. Geometry Storage Bucket (Versioned, No Expiration)
    this.geometryBucket = new s3.Bucket(this, 'GeometryBucket', {
      bucketName: 'c-n-geo-086143043656',
      versioned: true,
      encryption: s3.BucketEncryption.KMS,
      encryptionKey: props.kmsKey,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      objectOwnership: s3.ObjectOwnership.BUCKET_OWNER_ENFORCED,
      lifecycleRules: [
        {
          id: 'retain-geometry-versions',
          enabled: true,
          // Never delete geometry versions for audit compliance
          noncurrentVersionExpiration: undefined
        }
      ],
      removalPolicy: cdk.RemovalPolicy.RETAIN
    });

    // Add bucket policy to deny insecure connections
    this.geometryBucket.addToResourcePolicy(
      new iam.PolicyStatement({
        sid: 'DenyInsecureConnections',
        effect: iam.Effect.DENY,
        principals: [new iam.AnyPrincipal()],
        actions: ['s3:*'],
        resources: [
          this.geometryBucket.arnForObjects('*'),
          this.geometryBucket.bucketArn
        ],
        conditions: {
          Bool: {
            'aws:SecureTransport': 'false'
          }
        }
      })
    );

    // 2. Oracle Tiles Bucket (Versioned with Lifecycle)
    this.tilesBucket = new s3.Bucket(this, 'TilesBucket', {
      bucketName: 'c-n-oracle-tiles-086143043656',
      versioned: true,
      encryption: s3.BucketEncryption.KMS,
      encryptionKey: props.kmsKey,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      objectOwnership: s3.ObjectOwnership.BUCKET_OWNER_ENFORCED,
      lifecycleRules: [
        {
          id: 'expire-old-tiles',
          enabled: true,
          noncurrentVersionExpiration: cdk.Duration.days(60),
          abortIncompleteMultipartUploadAfter: cdk.Duration.days(7)
        },
        {
          id: 'intelligent-tiering',
          enabled: true,
          transitions: [
            {
              storageClass: s3.StorageClass.INTELLIGENT_TIERING,
              transitionAfter: cdk.Duration.days(1)
            },
            {
              storageClass: s3.StorageClass.GLACIER,
              transitionAfter: cdk.Duration.days(90)
            }
          ]
        }
      ],
      removalPolicy: cdk.RemovalPolicy.RETAIN
    });

    // Add bucket policy to deny insecure connections
    this.tilesBucket.addToResourcePolicy(
      new iam.PolicyStatement({
        sid: 'DenyInsecureConnections',
        effect: iam.Effect.DENY,
        principals: [new iam.AnyPrincipal()],
        actions: ['s3:*'],
        resources: [
          this.tilesBucket.arnForObjects('*'),
          this.tilesBucket.bucketArn
        ],
        conditions: {
          Bool: {
            'aws:SecureTransport': 'false'
          }
        }
      })
    );

    // Add intelligent tiering configuration
    new s3.CfnBucket.IntelligentTieringConfiguration(this, 'TilesIntelligentTiering', {
      bucket: this.tilesBucket.bucketName,
      id: 'EntireBucket',
      status: 'Enabled',
      prefix: '',
      optionalFields: ['BucketKeyStatus']
    });

    // Create folder structure with prefixes for organization
    new cdk.CfnOutput(this, 'GeometryBucketStructure', {
      value: JSON.stringify({
        farms: 'farms/{farmId}/v{version}/farm.geojson',
        plots: 'plots/{plotId}/v{version}/plot.geojson',
        boundaries: 'boundaries/{country}/{region}/*.geojson'
      }),
      description: 'Geometry bucket folder structure'
    });

    new cdk.CfnOutput(this, 'TilesBucketStructure', {
      value: JSON.stringify({
        satellite: 'tiles/{plotId}/{date}/ndvi.png',
        weather: 'weather/{plotId}/{date}/conditions.json',
        composite: 'composite/{plotId}/{date}/analysis.tiff'
      }),
      description: 'Tiles bucket folder structure'
    });

    // Output bucket names and ARNs
    new cdk.CfnOutput(this, 'GeometryBucketName', {
      value: this.geometryBucket.bucketName,
      description: 'Geometry Storage Bucket Name',
      exportName: 'CN-GeometryBucket-Name'
    });

    new cdk.CfnOutput(this, 'GeometryBucketArn', {
      value: this.geometryBucket.bucketArn,
      description: 'Geometry Storage Bucket ARN',
      exportName: 'CN-GeometryBucket-Arn'
    });

    new cdk.CfnOutput(this, 'TilesBucketName', {
      value: this.tilesBucket.bucketName,
      description: 'Oracle Tiles Bucket Name',
      exportName: 'CN-TilesBucket-Name'
    });

    new cdk.CfnOutput(this, 'TilesBucketArn', {
      value: this.tilesBucket.bucketArn,
      description: 'Oracle Tiles Bucket ARN',
      exportName: 'CN-TilesBucket-Arn'
    });

    // Apply comprehensive tags
    cdk.Tags.of(this).add('WORLD', 'Continuum_Overworld');
    cdk.Tags.of(this).add('ORCHESTRATOR', 'C_N');
    cdk.Tags.of(this).add('ENV', props.environment);
    cdk.Tags.of(this).add('CAPABILITY', 'FarmStorage');
    cdk.Tags.of(this).add('SECURITY', 'Enterprise');
    cdk.Tags.of(this).add('COMPLIANCE', 'KMS-TLS-Only');
    cdk.Tags.of(this).add('DATA_CLASSIFICATION', 'Farm-Geometries');
  }
}