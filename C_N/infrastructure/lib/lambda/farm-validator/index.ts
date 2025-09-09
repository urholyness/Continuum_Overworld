import { APIGatewayProxyHandler, APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';
import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3';
import { DynamoDBClient, PutItemCommand } from '@aws-sdk/client-dynamodb';
import { EventBridgeClient, PutEventsCommand } from '@aws-sdk/client-eventbridge';
import { CloudWatchClient, PutMetricDataCommand } from '@aws-sdk/client-cloudwatch';
import { marshall } from '@aws-sdk/util-dynamodb';
import * as turf from '@turf/turf';
import * as crypto from 'crypto';
import AWSXRay from 'aws-xray-sdk-core';

const s3 = AWSXRay.captureAWSv3Client(new S3Client());
const ddb = AWSXRay.captureAWSv3Client(new DynamoDBClient());
const eventbridge = AWSXRay.captureAWSv3Client(new EventBridgeClient());
const cloudwatch = AWSXRay.captureAWSv3Client(new CloudWatchClient());

interface GeometryValidationResult {
  valid: boolean;
  error?: string;
  warnings?: string[];
}

interface FarmFeature {
  type: 'Feature';
  properties: {
    type: 'farm';
    farmId?: string;
    name?: string;
    country?: string;
    [key: string]: any;
  };
  geometry: {
    type: 'Polygon' | 'MultiPolygon';
    coordinates: number[][][] | number[][][][];
  };
}

interface PlotFeature {
  type: 'Feature';
  properties: {
    type: 'plot';
    plotId?: string;
    name?: string;
    cropType?: string;
    [key: string]: any;
  };
  geometry: {
    type: 'Polygon' | 'MultiPolygon';
    coordinates: number[][][] | number[][][][];
  };
}

export const handler: APIGatewayProxyHandler = async (event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> => {
  const correlationId = event.requestContext.requestId;
  
  console.log(JSON.stringify({
    level: 'INFO',
    correlationId,
    event: 'farm_validation_request',
    httpMethod: event.httpMethod,
    path: event.path,
    userAgent: event.headers['User-Agent']
  }));
  
  try {
    if (event.httpMethod !== 'POST') {
      return createResponse(405, { error: 'Method not allowed' }, correlationId);
    }
    
    if (!event.body) {
      return createResponse(400, { 
        error: 'Missing request body',
        expectedFormat: {
          featureCollection: {
            type: 'FeatureCollection',
            features: [
              { type: 'Feature', properties: { type: 'farm' }, geometry: { type: 'Polygon' } },
              { type: 'Feature', properties: { type: 'plot' }, geometry: { type: 'Polygon' } }
            ]
          }
        }
      }, correlationId);
    }
    
    const body = JSON.parse(event.body);
    const { featureCollection } = body;
    
    // Validate GeoJSON structure
    if (!featureCollection || featureCollection.type !== 'FeatureCollection') {
      return createResponse(400, { error: 'Invalid GeoJSON FeatureCollection' }, correlationId);
    }
    
    const farmFeature = featureCollection.features.find((f: any) => f.properties.type === 'farm') as FarmFeature;
    if (!farmFeature) {
      return createResponse(400, { error: 'No farm feature found' }, correlationId);
    }
    
    // CRITICAL: Validate farm geometry
    const farmValidation = validatePolygon(farmFeature.geometry);
    if (!farmValidation.valid) {
      return createResponse(400, { 
        error: `Farm geometry invalid: ${farmValidation.error}`,
        details: farmValidation
      }, correlationId);
    }
    
    const farmId = farmFeature.properties.farmId || `FARM-${Date.now()}`;
    const farmName = farmFeature.properties.name || 'Unnamed Farm';
    const version = 1;
    
    // Calculate spatial properties
    const farmArea = turf.area(farmFeature) / 10000; // hectares
    const farmCentroid = turf.centroid(farmFeature);
    const farmBbox = turf.bbox(farmFeature);
    const geohash5 = encodeGeohash(
      farmCentroid.geometry.coordinates[1],
      farmCentroid.geometry.coordinates[0], 
      5
    );
    
    // Area constraints
    if (farmArea < 0.1 || farmArea > 10000) {
      return createResponse(400, { 
        error: `Farm area ${farmArea.toFixed(2)}ha outside valid range (0.1-10000ha)` 
      }, correlationId);
    }
    
    // Store versioned GeoJSON in S3
    const farmS3Key = `farms/${farmId}/v${version}/farm.geojson`;
    await s3.send(new PutObjectCommand({
      Bucket: 'c-n-geo-086143043656',
      Key: farmS3Key,
      Body: JSON.stringify(farmFeature),
      ContentType: 'application/geo+json',
      ServerSideEncryption: 'aws:kms',
      SSEKMSKeyId: 'alias/Aegis_KMS__PROD',
      Metadata: {
        farmId: farmId,
        version: String(version),
        correlationId: correlationId
      }
    }));
    
    // Store in DynamoDB with audit fields
    const farmItem = {
      farmId: farmId,
      name: farmName,
      country: farmFeature.properties.country || 'KE',
      centroid: {
        lat: farmCentroid.geometry.coordinates[1],
        lon: farmCentroid.geometry.coordinates[0]
      },
      bbox: farmBbox,
      areaHa: farmArea,
      geohash5: geohash5,
      geoS3Key: farmS3Key,
      version: version,
      createdAt: new Date().toISOString(),
      createdBy: event.requestContext?.authorizer?.claims?.sub || 'system',
      correlationId: correlationId
    };
    
    await ddb.send(new PutItemCommand({
      TableName: 'C_N-FarmRegistry',
      Item: marshall(farmItem),
      ConditionExpression: 'attribute_not_exists(farmId)'
    }));
    
    // Process plots with validation
    const plots = featureCollection.features.filter((f: any) => f.properties.type === 'plot') as PlotFeature[];
    const plotResults: Array<{ plotId: string; areaHa: number }> = [];
    
    for (const plot of plots) {
      const plotValidation = validatePolygon(plot.geometry);
      if (!plotValidation.valid) {
        console.warn(JSON.stringify({
          level: 'WARN',
          correlationId,
          event: 'plot_validation_failed',
          error: plotValidation.error,
          plotIndex: plotResults.length
        }));
        continue;
      }
      
      const plotId = plot.properties.plotId || `${farmId}-P${plotResults.length + 1}`;
      const plotArea = turf.area(plot) / 10000;
      const plotCentroid = turf.centroid(plot);
      const geohash7 = encodeGeohash(
        plotCentroid.geometry.coordinates[1],
        plotCentroid.geometry.coordinates[0],
        7
      );
      
      // Store plot GeoJSON
      const plotS3Key = `plots/${plotId}/v${version}/plot.geojson`;
      await s3.send(new PutObjectCommand({
        Bucket: 'c-n-geo-086143043656',
        Key: plotS3Key,
        Body: JSON.stringify(plot),
        ContentType: 'application/geo+json',
        ServerSideEncryption: 'aws:kms',
        SSEKMSKeyId: 'alias/Aegis_KMS__PROD'
      }));
      
      // Store in DynamoDB
      await ddb.send(new PutItemCommand({
        TableName: 'C_N-Oracle-FarmPlots',
        Item: marshall({
          plotId: plotId,
          farmId: farmId,
          name: plot.properties.name || `Plot ${plotResults.length + 1}`,
          cropType: plot.properties.cropType || 'French Beans',
          centroid: {
            lat: plotCentroid.geometry.coordinates[1],
            lon: plotCentroid.geometry.coordinates[0]
          },
          areaHa: plotArea,
          geohash7: geohash7,
          geoS3Key: plotS3Key,
          version: version,
          createdAt: new Date().toISOString()
        })
      }));
      
      plotResults.push({ plotId, areaHa: plotArea });
    }
    
    // Emit Farm.Onboarded@v1 event
    await eventbridge.send(new PutEventsCommand({
      Entries: [{
        Source: 'Farm.Management',
        DetailType: 'Farm.Onboarded@v1',
        Detail: JSON.stringify({
          farmId: farmId,
          farmName: farmName,
          plotCount: plotResults.length,
          totalAreaHa: farmArea,
          plots: plotResults,
          correlationId: correlationId,
          timestamp: new Date().toISOString()
        }),
        EventBusName: 'C_N-EventBus-Core'
      }]
    }));
    
    // Emit CloudWatch metrics
    await cloudwatch.send(new PutMetricDataCommand({
      Namespace: 'C_N/FarmManagement',
      MetricData: [
        {
          MetricName: 'FarmOnboarded',
          Value: 1,
          Unit: 'Count',
          Dimensions: [
            { Name: 'Country', Value: farmFeature.properties.country || 'KE' },
            { Name: 'Service', Value: 'FarmValidator' }
          ]
        },
        {
          MetricName: 'FarmAreaHa',
          Value: farmArea,
          Unit: 'Count',
          Dimensions: [{ Name: 'FarmId', Value: farmId }]
        },
        {
          MetricName: 'PlotCount',
          Value: plotResults.length,
          Unit: 'Count',
          Dimensions: [{ Name: 'FarmId', Value: farmId }]
        }
      ]
    }));
    
    // Write Aegis audit log
    console.log(JSON.stringify({
      _aegis: true,
      event: 'FARM_ONBOARDED',
      farmId: farmId,
      farmName: farmName,
      plotCount: plotResults.length,
      totalAreaHa: farmArea,
      correlationId: correlationId,
      principal: event.requestContext?.authorizer?.claims?.sub || 'system',
      timestamp: new Date().toISOString()
    }));
    
    return createResponse(200, {
      success: true,
      farmId: farmId,
      farmName: farmName,
      farmArea: farmArea,
      plots: plotResults,
      version: version,
      s3Keys: {
        farm: farmS3Key,
        plots: plotResults.map((p, i) => `plots/${p.plotId}/v${version}/plot.geojson`)
      }
    }, correlationId, {
      'X-Farm-ID': farmId,
      'X-Plot-Count': String(plotResults.length)
    });
    
  } catch (error) {
    console.error(JSON.stringify({
      level: 'ERROR',
      correlationId,
      event: 'farm_validation_error',
      error: error.message,
      stack: error.stack?.split('\\n')[0]
    }));
    
    // Emit error metrics
    await cloudwatch.send(new PutMetricDataCommand({
      Namespace: 'C_N/FarmManagement',
      MetricData: [{
        MetricName: 'FarmValidationError',
        Value: 1,
        Unit: 'Count',
        Dimensions: [
          { Name: 'ErrorType', Value: error.name || 'UnknownError' },
          { Name: 'Service', Value: 'FarmValidator' }
        ]
      }]
    }));
    
    return createResponse(500, {
      error: 'Internal server error',
      correlationId: correlationId
    }, correlationId);
  }
};

function validatePolygon(geometry: any): GeometryValidationResult {
  try {
    if (geometry.type !== 'Polygon' && geometry.type !== 'MultiPolygon') {
      return { valid: false, error: 'Not a polygon or multipolygon' };
    }
    
    const poly = geometry.type === 'Polygon' 
      ? turf.polygon(geometry.coordinates)
      : turf.multiPolygon(geometry.coordinates);
    
    // Check for self-intersections
    const kinks = turf.kinks(poly);
    if (kinks.features.length > 0) {
      return { valid: false, error: 'Self-intersecting polygon detected' };
    }
    
    // Check ring orientation (outer=CCW, holes=CW)
    if (geometry.type === 'Polygon') {
      const isClockwise = turf.booleanClockwise(geometry.coordinates[0]);
      if (isClockwise) {
        return { valid: false, error: 'Outer ring must be counter-clockwise' };
      }
    }
    
    // Check minimum area (0.01 ha = 100 m²)
    const area = turf.area(poly) / 10000;
    if (area < 0.01) {
      return { valid: false, error: 'Area too small (< 0.01 ha)' };
    }
    
    // Check for reasonable coordinate values
    const bbox = turf.bbox(poly);
    if (bbox[0] < -180 || bbox[0] > 180 || bbox[2] < -180 || bbox[2] > 180) {
      return { valid: false, error: 'Invalid longitude values' };
    }
    if (bbox[1] < -90 || bbox[1] > 90 || bbox[3] < -90 || bbox[3] > 90) {
      return { valid: false, error: 'Invalid latitude values' };
    }
    
    return { valid: true };
  } catch (error) {
    return { valid: false, error: error.message };
  }
}

function encodeGeohash(lat: number, lon: number, precision: number = 5): string {
  const BASE32 = '0123456789bcdefghjkmnpqrstuvwxyz';
  let hash = '';
  let bits = 0;
  let bit = 0;
  let even = true;
  const latRange = [-90, 90];
  const lonRange = [-180, 180];
  
  while (hash.length < precision) {
    if (even) {
      const mid = (lonRange[0] + lonRange[1]) / 2;
      if (lon > mid) {
        bits |= (1 << (4 - bit));
        lonRange[0] = mid;
      } else {
        lonRange[1] = mid;
      }
    } else {
      const mid = (latRange[0] + latRange[1]) / 2;
      if (lat > mid) {
        bits |= (1 << (4 - bit));
        latRange[0] = mid;
      } else {
        latRange[1] = mid;
      }
    }
    even = !even;
    bit++;
    if (bit === 5) {
      hash += BASE32[bits];
      bits = 0;
      bit = 0;
    }
  }
  return hash;
}

function createResponse(
  statusCode: number,
  body: any,
  correlationId: string,
  additionalHeaders: Record<string, string> = {}
): APIGatewayProxyResult {
  return {
    statusCode,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Correlation-Id',
      'X-Correlation-Id': correlationId,
      'X-Service': 'C_N-Farm-Validator',
      ...additionalHeaders
    },
    body: JSON.stringify(body, null, 2)
  };
}