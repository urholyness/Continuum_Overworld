import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as events from 'aws-cdk-lib/aws-events';
import * as schemas from 'aws-cdk-lib/aws-eventschemas';

export interface FarmSchemasStackProps extends cdk.StackProps {
  eventBus: events.EventBus;
  environment: string;
}

export class CNFarmSchemasConstruct extends Construct {
  public readonly schemaRegistry: schemas.CfnRegistry;
  public readonly farmOnboardedSchema: schemas.CfnSchema;
  public readonly ndviProcessedSchema: schemas.CfnSchema;
  public readonly weatherSnapshotSchema: schemas.CfnSchema;
  public readonly oracleDataProcessedSchema: schemas.CfnSchema;

  constructor(scope: Construct, id: string, props: FarmSchemasStackProps) {
    super(scope, id);

    // Create schema registry
    this.schemaRegistry = new schemas.CfnRegistry(this, 'FarmSchemaRegistry', {
      registryName: 'C_N-Farm-Registry',
      description: 'Event schema registry for farm management and Oracle data processing',
      tags: [
        { key: 'WORLD', value: 'Continuum_Overworld' },
        { key: 'ORCHESTRATOR', value: 'C_N' },
        { key: 'ENV', value: props.environment },
        { key: 'CAPABILITY', value: 'EventSchemas' }
      ]
    });

    // Farm.Onboarded@v1 Schema
    this.farmOnboardedSchema = new schemas.CfnSchema(this, 'FarmOnboardedSchema', {
      registryName: this.schemaRegistry.registryName!,
      schemaName: 'Farm.Onboarded@v1',
      type: 'JSONSchemaDraft4',
      description: 'Schema for farm onboarding completed events',
      content: JSON.stringify({
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type": "object",
        "title": "Farm Onboarded Event",
        "description": "Event emitted when a farm is successfully onboarded with geometry validation",
        "properties": {
          "version": {
            "type": "string",
            "enum": ["0"],
            "description": "Event version"
          },
          "id": {
            "type": "string",
            "description": "Unique event identifier"
          },
          "detail-type": {
            "type": "string",
            "enum": ["Farm.Onboarded@v1"]
          },
          "source": {
            "type": "string",
            "enum": ["Farm.Management"]
          },
          "account": {
            "type": "string",
            "pattern": "^[0-9]{12}$"
          },
          "time": {
            "type": "string",
            "format": "date-time"
          },
          "region": {
            "type": "string"
          },
          "detail": {
            "type": "object",
            "properties": {
              "farmId": {
                "type": "string",
                "pattern": "^FARM-[0-9]+$",
                "description": "Unique farm identifier"
              },
              "farmName": {
                "type": "string",
                "minLength": 1,
                "maxLength": 200,
                "description": "Human-readable farm name"
              },
              "plotCount": {
                "type": "integer",
                "minimum": 1,
                "maximum": 1000,
                "description": "Number of plots in the farm"
              },
              "totalAreaHa": {
                "type": "number",
                "minimum": 0.1,
                "maximum": 10000,
                "description": "Total farm area in hectares"
              },
              "plots": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "plotId": {
                      "type": "string",
                      "pattern": "^FARM-[0-9]+-P[0-9]+$"
                    },
                    "areaHa": {
                      "type": "number",
                      "minimum": 0.01
                    }
                  },
                  "required": ["plotId", "areaHa"]
                }
              },
              "correlationId": {
                "type": "string",
                "description": "Request correlation identifier"
              },
              "timestamp": {
                "type": "string",
                "format": "date-time"
              },
              "metadata": {
                "type": "object",
                "properties": {
                  "country": {
                    "type": "string",
                    "pattern": "^[A-Z]{2}$"
                  },
                  "geometryValidated": {
                    "type": "boolean"
                  },
                  "version": {
                    "type": "integer",
                    "minimum": 1
                  }
                }
              }
            },
            "required": ["farmId", "farmName", "plotCount", "totalAreaHa", "correlationId", "timestamp"]
          }
        },
        "required": ["version", "id", "detail-type", "source", "account", "time", "region", "detail"]
      })
    });

    // NDVI.Processed@v1 Schema
    this.ndviProcessedSchema = new schemas.CfnSchema(this, 'NDVIProcessedSchema', {
      registryName: this.schemaRegistry.registryName!,
      schemaName: 'NDVI.Processed@v1',
      type: 'JSONSchemaDraft4',
      description: 'Schema for NDVI satellite data processing events',
      content: JSON.stringify({
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type": "object",
        "title": "NDVI Processed Event",
        "description": "Event emitted when satellite NDVI data is processed for a plot",
        "properties": {
          "version": {
            "type": "string",
            "enum": ["0"]
          },
          "id": {
            "type": "string"
          },
          "detail-type": {
            "type": "string",
            "enum": ["NDVI.Processed@v1"]
          },
          "source": {
            "type": "string",
            "enum": ["Oracle.Satellite"]
          },
          "account": {
            "type": "string",
            "pattern": "^[0-9]{12}$"
          },
          "time": {
            "type": "string",
            "format": "date-time"
          },
          "region": {
            "type": "string"
          },
          "detail": {
            "type": "object",
            "properties": {
              "plotId": {
                "type": "string",
                "pattern": "^FARM-[0-9]+-P[0-9]+$",
                "description": "Plot identifier"
              },
              "farmId": {
                "type": "string",
                "pattern": "^FARM-[0-9]+$",
                "description": "Farm identifier"
              },
              "ndvi": {
                "type": ["number", "null"],
                "minimum": -1,
                "maximum": 1,
                "description": "Normalized Difference Vegetation Index value"
              },
              "cloudCoverage": {
                "type": "number",
                "minimum": 0,
                "maximum": 100,
                "description": "Cloud coverage percentage"
              },
              "dataQuality": {
                "type": "object",
                "properties": {
                  "validPixels": {
                    "type": "integer",
                    "minimum": 0
                  },
                  "totalPixels": {
                    "type": "integer",
                    "minimum": 1
                  },
                  "qualityScore": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1
                  },
                  "qualityLevel": {
                    "type": "string",
                    "enum": ["HIGH", "MEDIUM", "LOW"]
                  }
                },
                "required": ["validPixels", "totalPixels", "qualityScore", "qualityLevel"]
              },
              "satelliteData": {
                "type": "object",
                "properties": {
                  "captureDate": {
                    "type": "string",
                    "format": "date"
                  },
                  "satellite": {
                    "type": "string",
                    "enum": ["Sentinel-2"]
                  },
                  "resolution": {
                    "type": "string",
                    "pattern": "^[0-9]+m$"
                  },
                  "bbox": {
                    "type": "array",
                    "items": {
                      "type": "number"
                    },
                    "minItems": 4,
                    "maxItems": 4
                  }
                },
                "required": ["captureDate", "satellite", "resolution", "bbox"]
              },
              "storage": {
                "type": "object",
                "properties": {
                  "tileKey": {
                    "type": "string",
                    "description": "S3 key for processed tile"
                  },
                  "bucket": {
                    "type": "string",
                    "description": "S3 bucket name"
                  }
                },
                "required": ["tileKey", "bucket"]
              },
              "correlationId": {
                "type": "string"
              },
              "timestamp": {
                "type": "string",
                "format": "date-time"
              }
            },
            "required": ["plotId", "farmId", "ndvi", "cloudCoverage", "dataQuality", "satelliteData", "storage", "correlationId", "timestamp"]
          }
        },
        "required": ["version", "id", "detail-type", "source", "account", "time", "region", "detail"]
      })
    });

    // Weather.Snapshotted@v1 Schema
    this.weatherSnapshotSchema = new schemas.CfnSchema(this, 'WeatherSnapshotSchema', {
      registryName: this.schemaRegistry.registryName!,
      schemaName: 'Weather.Snapshotted@v1',
      type: 'JSONSchemaDraft4',
      description: 'Schema for weather data snapshot events',
      content: JSON.stringify({
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type": "object",
        "title": "Weather Snapshot Event",
        "description": "Event emitted when weather data is captured for a plot",
        "properties": {
          "version": {
            "type": "string",
            "enum": ["0"]
          },
          "id": {
            "type": "string"
          },
          "detail-type": {
            "type": "string",
            "enum": ["Weather.Snapshotted@v1"]
          },
          "source": {
            "type": "string",
            "enum": ["Oracle.Weather"]
          },
          "account": {
            "type": "string",
            "pattern": "^[0-9]{12}$"
          },
          "time": {
            "type": "string",
            "format": "date-time"
          },
          "region": {
            "type": "string"
          },
          "detail": {
            "type": "object",
            "properties": {
              "plotId": {
                "type": "string",
                "pattern": "^FARM-[0-9]+-P[0-9]+$"
              },
              "farmId": {
                "type": "string",
                "pattern": "^FARM-[0-9]+$"
              },
              "coordinates": {
                "type": "object",
                "properties": {
                  "lat": {
                    "type": "number",
                    "minimum": -90,
                    "maximum": 90
                  },
                  "lon": {
                    "type": "number",
                    "minimum": -180,
                    "maximum": 180
                  }
                },
                "required": ["lat", "lon"]
              },
              "weather": {
                "type": "object",
                "properties": {
                  "temperature": {
                    "type": "object",
                    "properties": {
                      "current": {
                        "type": "number"
                      },
                      "min": {
                        "type": "number"
                      },
                      "max": {
                        "type": "number"
                      },
                      "unit": {
                        "type": "string",
                        "enum": ["C", "F"]
                      }
                    },
                    "required": ["current", "unit"]
                  },
                  "humidity": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 100
                  },
                  "precipitation": {
                    "type": "object",
                    "properties": {
                      "amount": {
                        "type": "number",
                        "minimum": 0
                      },
                      "unit": {
                        "type": "string",
                        "enum": ["mm", "in"]
                      }
                    },
                    "required": ["amount", "unit"]
                  },
                  "windSpeed": {
                    "type": "number",
                    "minimum": 0
                  },
                  "conditions": {
                    "type": "string"
                  }
                },
                "required": ["temperature", "humidity", "precipitation"]
              },
              "correlationId": {
                "type": "string"
              },
              "timestamp": {
                "type": "string",
                "format": "date-time"
              }
            },
            "required": ["plotId", "farmId", "coordinates", "weather", "correlationId", "timestamp"]
          }
        },
        "required": ["version", "id", "detail-type", "source", "account", "time", "region", "detail"]
      })
    });

    // Oracle.DataProcessed@v1 Schema (Composite event)
    this.oracleDataProcessedSchema = new schemas.CfnSchema(this, 'OracleDataProcessedSchema', {
      registryName: this.schemaRegistry.registryName!,
      schemaName: 'Oracle.DataProcessed@v1',
      type: 'JSONSchemaDraft4',
      description: 'Schema for composite Oracle data processing completion events',
      content: JSON.stringify({
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type": "object",
        "title": "Oracle Data Processed Event",
        "description": "Event emitted when composite Oracle processing (satellite + weather) is completed",
        "properties": {
          "version": {
            "type": "string",
            "enum": ["0"]
          },
          "id": {
            "type": "string"
          },
          "detail-type": {
            "type": "string",
            "enum": ["Oracle.DataProcessed@v1"]
          },
          "source": {
            "type": "string",
            "enum": ["Oracle.Composite"]
          },
          "account": {
            "type": "string",
            "pattern": "^[0-9]{12}$"
          },
          "time": {
            "type": "string",
            "format": "date-time"
          },
          "region": {
            "type": "string"
          },
          "detail": {
            "type": "object",
            "properties": {
              "plotId": {
                "type": "string",
                "pattern": "^FARM-[0-9]+-P[0-9]+$"
              },
              "farmId": {
                "type": "string",
                "pattern": "^FARM-[0-9]+$"
              },
              "processingResults": {
                "type": "object",
                "properties": {
                  "satellite": {
                    "type": "object",
                    "properties": {
                      "success": {
                        "type": "boolean"
                      },
                      "ndvi": {
                        "type": ["number", "null"]
                      },
                      "qualityScore": {
                        "type": "number"
                      }
                    },
                    "required": ["success"]
                  },
                  "weather": {
                    "type": "object",
                    "properties": {
                      "success": {
                        "type": "boolean"
                      },
                      "temperature": {
                        "type": ["number", "null"]
                      },
                      "conditions": {
                        "type": ["string", "null"]
                      }
                    },
                    "required": ["success"]
                  }
                },
                "required": ["satellite", "weather"]
              },
              "qualityAssessment": {
                "type": "object",
                "properties": {
                  "overallQuality": {
                    "type": "string",
                    "enum": ["HIGH", "MEDIUM", "LOW", "FAILED"]
                  },
                  "recommendations": {
                    "type": "array",
                    "items": {
                      "type": "string"
                    }
                  }
                },
                "required": ["overallQuality"]
              },
              "correlationId": {
                "type": "string"
              },
              "timestamp": {
                "type": "string",
                "format": "date-time"
              }
            },
            "required": ["plotId", "farmId", "processingResults", "qualityAssessment", "correlationId", "timestamp"]
          }
        },
        "required": ["version", "id", "detail-type", "source", "account", "time", "region", "detail"]
      })
    });

    // Output schema ARNs
    new cdk.CfnOutput(this, 'SchemaRegistryArn', {
      value: this.schemaRegistry.attrArn,
      description: 'Farm Schema Registry ARN',
      exportName: 'CN-FarmSchemaRegistry-Arn'
    });

    new cdk.CfnOutput(this, 'FarmOnboardedSchemaArn', {
      value: this.farmOnboardedSchema.attrArn,
      description: 'Farm Onboarded Schema ARN',
      exportName: 'CN-FarmOnboardedSchema-Arn'
    });

    new cdk.CfnOutput(this, 'NDVIProcessedSchemaArn', {
      value: this.ndviProcessedSchema.attrArn,
      description: 'NDVI Processed Schema ARN',
      exportName: 'CN-NDVIProcessedSchema-Arn'
    });
  }
}