import os
import json
import boto3
from datetime import datetime, timedelta
import requests
from typing import Dict, Any, Tuple
import base64
import io
from PIL import Image
import numpy as np

# AWS clients
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
eventbridge = boto3.client('events')
ssm = boto3.client('ssm')

# Configuration
FARM_ID = os.environ.get('FARM_ID', '2BH')
FARM_POLYGON = json.loads(os.environ.get('FARM_POLYGON_GEOJSON', '{}'))
S3_BUCKET = os.environ.get('S3_BUCKET', 'gsg-data-curated')

def get_sentinel_token() -> str:
    """Get Sentinel Hub OAuth token."""
    client_id = os.environ.get('SENTINELHUB_CLIENT_ID')
    client_secret = os.environ.get('SENTINELHUB_CLIENT_SECRET')
    
    response = requests.post(
        'https://services.sentinel-hub.com/oauth/token',
        data={
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret
        }
    )
    response.raise_for_status()
    return response.json()['access_token']

def calculate_ndvi_stats(image_data: bytes) -> Tuple[float, float, float]:
    """Calculate NDVI statistics from the image data."""
    img = Image.open(io.BytesIO(image_data))
    img_array = np.array(img)
    
    # Assuming the image has NDVI values normalized to 0-255
    ndvi_normalized = img_array / 255.0
    ndvi = (ndvi_normalized * 2) - 1  # Convert to -1 to 1 range
    
    # Filter valid NDVI values (land areas)
    valid_ndvi = ndvi[ndvi > -0.1]  # Exclude water and invalid pixels
    
    if len(valid_ndvi) == 0:
        return 0.0, 0.0, 0.0
    
    mean_val = float(np.mean(valid_ndvi))
    p10_val = float(np.percentile(valid_ndvi, 10))
    p90_val = float(np.percentile(valid_ndvi, 90))
    
    return mean_val, p10_val, p90_val

def fetch_ndvi_data(token: str, polygon: Dict) -> Dict[str, Any]:
    """Fetch NDVI data from Sentinel Hub."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=3)
    
    evalscript = """
    //VERSION=3
    function setup() {
        return {
            input: [{
                bands: ["B04", "B08", "SCL"],
                units: "DN"
            }],
            output: [
                {
                    id: "ndvi",
                    bands: 1,
                    sampleType: "UINT8"
                },
                {
                    id: "statistics",
                    bands: 0,
                    sampleType: "FLOAT32"
                }
            ]
        };
    }

    function evaluatePixel(sample) {
        // Cloud masking using SCL band
        if (sample.SCL == 3 || sample.SCL == 9 || sample.SCL == 8 || sample.SCL == 10) {
            return {
                ndvi: [0],
                statistics: []
            };
        }
        
        let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
        
        // Normalize NDVI from [-1, 1] to [0, 255]
        let ndvi_byte = Math.max(0, Math.min(255, Math.floor((ndvi + 1) * 127.5)));
        
        return {
            ndvi: [ndvi_byte],
            statistics: []
        };
    }
    """
    
    request_body = {
        "input": {
            "bounds": {
                "geometry": polygon['geometry']
            },
            "data": [
                {
                    "type": "sentinel-2-l2a",
                    "dataFilter": {
                        "timeRange": {
                            "from": start_date.strftime("%Y-%m-%dT00:00:00Z"),
                            "to": end_date.strftime("%Y-%m-%dT23:59:59Z")
                        },
                        "maxCloudCoverage": 30
                    }
                }
            ]
        },
        "output": {
            "width": 512,
            "height": 512,
            "responses": [
                {
                    "identifier": "ndvi",
                    "format": {
                        "type": "image/png"
                    }
                }
            ]
        },
        "evalscript": evalscript
    }
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.post(
        'https://services.sentinel-hub.com/api/v1/process',
        json=request_body,
        headers=headers
    )
    response.raise_for_status()
    
    return {
        'image_data': response.content,
        'acquisition_date': end_date.strftime("%Y-%m-%d")
    }

def save_to_s3(image_data: bytes, date_str: str) -> str:
    """Save NDVI image to S3."""
    key = f"sat/{FARM_ID}/{date_str}/ndvi.png"
    
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=image_data,
        ContentType='image/png',
        Metadata={
            'farm_id': FARM_ID,
            'acquisition_date': date_str,
            'processing_date': datetime.now().isoformat()
        }
    )
    
    return f"s3://{S3_BUCKET}/{key}"

def save_to_dynamodb(timestamp: str, mean: float, p10: float, p90: float):
    """Save NDVI metrics to DynamoDB."""
    table = dynamodb.Table('readings')
    
    items = [
        {
            'pk': f'{FARM_ID}#{timestamp}',
            'sk': 'sat.ndvi.mean',
            'farm_id': FARM_ID,
            'timestamp': timestamp,
            'sensor': 'sat.ndvi.mean',
            'value': mean,
            'unit': 'index',
            'created_at': datetime.now().isoformat()
        },
        {
            'pk': f'{FARM_ID}#{timestamp}',
            'sk': 'sat.ndvi.p10',
            'farm_id': FARM_ID,
            'timestamp': timestamp,
            'sensor': 'sat.ndvi.p10',
            'value': p10,
            'unit': 'index',
            'created_at': datetime.now().isoformat()
        },
        {
            'pk': f'{FARM_ID}#{timestamp}',
            'sk': 'sat.ndvi.p90',
            'farm_id': FARM_ID,
            'timestamp': timestamp,
            'sensor': 'sat.ndvi.p90',
            'value': p90,
            'unit': 'index',
            'created_at': datetime.now().isoformat()
        }
    ]
    
    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)

def send_event(detail: Dict[str, Any]):
    """Send completion event to EventBridge."""
    eventbridge.put_events(
        Entries=[
            {
                'Source': 'farm-ingest.satellite',
                'DetailType': 'sat_ingest_complete',
                'Detail': json.dumps(detail),
                'EventBusName': 'default'
            }
        ]
    )

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for satellite NDVI processing."""
    try:
        # Get Sentinel Hub token
        token = get_sentinel_token()
        
        # Fetch NDVI data
        ndvi_result = fetch_ndvi_data(token, FARM_POLYGON)
        
        # Calculate statistics
        mean, p10, p90 = calculate_ndvi_stats(ndvi_result['image_data'])
        
        # Save to S3
        s3_path = save_to_s3(
            ndvi_result['image_data'], 
            ndvi_result['acquisition_date']
        )
        
        # Save to DynamoDB
        timestamp = datetime.now().isoformat()
        save_to_dynamodb(timestamp, mean, p10, p90)
        
        # Send completion event
        send_event({
            'farm_id': FARM_ID,
            'timestamp': timestamp,
            'acquisition_date': ndvi_result['acquisition_date'],
            's3_path': s3_path,
            'metrics': {
                'mean': mean,
                'p10': p10,
                'p90': p90
            }
        })
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'NDVI processing complete',
                'farm_id': FARM_ID,
                'metrics': {
                    'mean': mean,
                    'p10': p10,
                    'p90': p90
                },
                's3_path': s3_path
            })
        }
        
    except Exception as e:
        print(f"Error processing NDVI: {str(e)}")
        raise