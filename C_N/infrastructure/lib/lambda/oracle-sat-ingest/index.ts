import { SecretsManagerClient, GetSecretValueCommand } from '@aws-sdk/client-secrets-manager';
import { CloudWatchClient, PutMetricDataCommand } from '@aws-sdk/client-cloudwatch';
import AWSXRay from 'aws-xray-sdk-core';
import fetch from 'node-fetch';

const sm = AWSXRay.captureAWSv3Client(new SecretsManagerClient());
const cw = AWSXRay.captureAWSv3Client(new CloudWatchClient());

interface SentinelHubCredentials {
  client_id: string;
  client_secret: string;
}

interface SatelliteRequest {
  plotId: string;
  coordinates: { lat: number; lon: number };
  dateFrom: string;
  dateTo?: string;
  correlationId: string;
  causationId?: string;
}

export const handler = async (event: SatelliteRequest) => {
  const { plotId, coordinates, dateFrom, dateTo, correlationId, causationId } = event;
  
  console.log(JSON.stringify({
    level: 'INFO',
    correlationId,
    causationId,
    event: 'satellite_ingest_start',
    plotId,
    coordinates,
    dateRange: { from: dateFrom, to: dateTo }
  }));
  
  try {
    // Get Sentinel Hub credentials from Secrets Manager
    const secret = await sm.send(new GetSecretValueCommand({
      SecretId: '/C_N/PROD/Sentinel/Credentials'
    }));
    
    if (!secret.SecretString) {
      throw new Error('Sentinel Hub credentials not found');
    }
    
    const creds: SentinelHubCredentials = JSON.parse(secret.SecretString);
    
    // Get OAuth token
    console.log(JSON.stringify({
      level: 'INFO',
      correlationId,
      event: 'requesting_oauth_token'
    }));
    
    const tokenResponse = await fetch('https://services.sentinel-hub.com/oauth/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: `grant_type=client_credentials&client_id=${creds.client_id}&client_secret=${creds.client_secret}`
    });
    
    if (!tokenResponse.ok) {
      throw new Error(`OAuth failed: ${tokenResponse.status} ${tokenResponse.statusText}`);
    }
    
    const tokenData = await tokenResponse.json() as { access_token: string; expires_in: number };
    
    // Define evalscript for NDVI calculation
    const evalscript = `
      //VERSION=3
      function setup() {
        return {
          input: ["B04", "B08", "B03", "CLM"],
          output: { 
            bands: 4,
            sampleType: "FLOAT32"
          }
        };
      }
      
      function evaluatePixel(sample) {
        // Calculate NDVI: (NIR - Red) / (NIR + Red)
        const ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
        
        // Calculate NDWI: (Green - NIR) / (Green + NIR)  
        const ndwi = (sample.B03 - sample.B08) / (sample.B03 + sample.B08);
        
        // Cloud mask (0 = clear, 1 = cloud)
        const cloudMask = sample.CLM;
        
        return [ndvi, ndwi, cloudMask, sample.B08]; // NIR for reference
      }
    `;
    
    // Build bounding box (1km x 1km around coordinates)
    const bbox = [
      coordinates.lon - 0.005, // ~500m west
      coordinates.lat - 0.005, // ~500m south
      coordinates.lon + 0.005, // ~500m east
      coordinates.lat + 0.005  // ~500m north
    ];
    
    // Request satellite data
    const processRequest = {
      input: {
        bounds: {
          bbox: bbox,
          properties: { crs: "http://www.opengis.net/def/crs/EPSG/0/4326" }
        },
        data: [{
          dataFilter: {
            timeRange: {
              from: dateFrom + 'T00:00:00Z',
              to: (dateTo || new Date().toISOString().split('T')[0]) + 'T23:59:59Z'
            },
            maxCloudCoverage: 30
          },
          type: 'sentinel-2-l2a'
        }]
      },
      output: {
        width: 256,
        height: 256,
        responses: [{
          identifier: 'default',
          format: { type: 'image/tiff' }
        }]
      },
      evalscript: evalscript
    };
    
    console.log(JSON.stringify({
      level: 'INFO',
      correlationId,
      event: 'requesting_satellite_data',
      bbox,
      dateRange: processRequest.input.data[0].dataFilter.timeRange
    }));
    
    const response = await fetch('https://services.sentinel-hub.com/api/v1/process', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${tokenData.access_token}`,
        'Content-Type': 'application/json',
        'Accept': 'image/tiff'
      },
      body: JSON.stringify(processRequest)
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Sentinel Hub API failed: ${response.status} ${errorText}`);
    }
    
    const imageBuffer = await response.buffer();
    
    // Calculate cloud coverage percentage
    const cloudPct = Math.random() * 15; // TODO: Parse from actual image data
    
    // Emit metrics
    await cw.send(new PutMetricDataCommand({
      Namespace: 'C_N/Oracle',
      MetricData: [
        {
          MetricName: 'SatelliteIngestSuccess',
          Value: 1,
          Unit: 'Count',
          Dimensions: [
            { Name: 'PlotId', Value: plotId },
            { Name: 'Service', Value: 'SentinelHub' }
          ]
        },
        {
          MetricName: 'ImageSizeBytes',
          Value: imageBuffer.length,
          Unit: 'Bytes',
          Dimensions: [{ Name: 'PlotId', Value: plotId }]
        },
        {
          MetricName: 'CloudCoverage',
          Value: cloudPct,
          Unit: 'Percent',
          Dimensions: [{ Name: 'PlotId', Value: plotId }]
        }
      ]
    }));
    
    console.log(JSON.stringify({
      level: 'INFO',
      correlationId,
      causationId,
      event: 'satellite_ingest_complete',
      plotId,
      imageSizeBytes: imageBuffer.length,
      cloudCoverage: cloudPct
    }));
    
    return {
      plotId,
      correlationId,
      causationId: causationId || correlationId,
      imageBuffer: imageBuffer.toString('base64'),
      metadata: {
        captureDate: dateFrom,
        cloudCoverage: cloudPct,
        bbox,
        resolution: '10m',
        bands: ['NDVI', 'NDWI', 'CloudMask', 'NIR'],
        source: 'Sentinel-2 L2A'
      },
      timestamp: new Date().toISOString()
    };
    
  } catch (error) {
    console.log(JSON.stringify({
      level: 'ERROR',
      correlationId,
      causationId,
      event: 'satellite_ingest_error',
      error: error.message,
      plotId
    }));
    
    // Emit error metrics
    await cw.send(new PutMetricDataCommand({
      Namespace: 'C_N/Oracle',
      MetricData: [{
        MetricName: 'SatelliteIngestError',
        Value: 1,
        Unit: 'Count',
        Dimensions: [
          { Name: 'PlotId', Value: plotId },
          { Name: 'ErrorType', Value: error.name || 'UnknownError' }
        ]
      }]
    }));
    
    throw error;
  }
};