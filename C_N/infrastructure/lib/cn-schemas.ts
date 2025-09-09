export const NDVI_PROCESSED_SCHEMA = {
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["source", "detail-type", "detail", "time"],
  "properties": {
    "source": { "const": "Oracle.Satellite" },
    "detail-type": { "const": "NDVI.Processed@v1" },
    "time": { "type": "string", "format": "date-time" },
    "detail": {
      "type": "object",
      "required": ["correlationId", "causationId", "plotId", "dateISO", "index", "tileKey", "mean", "cloudPct"],
      "properties": {
        "correlationId": { "type": "string", "format": "uuid" },
        "causationId": { "type": "string", "format": "uuid" },
        "plotId": { "type": "string" },
        "dateISO": { "type": "string", "format": "date" },
        "index": { "enum": ["ndvi", "ndwi", "evi"] },
        "tileKey": { "type": "string" },
        "mean": { "type": "number", "minimum": -1, "maximum": 1 },
        "cloudPct": { "type": "number", "minimum": 0, "maximum": 100 },
        "coordinates": {
          "type": "object",
          "properties": {
            "lat": { "type": "number" },
            "lon": { "type": "number" }
          },
          "required": ["lat", "lon"]
        }
      }
    }
  }
};

export const WEATHER_SNAPSHOTTED_SCHEMA = {
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["source", "detail-type", "detail", "time"],
  "properties": {
    "source": { "const": "Oracle.Weather" },
    "detail-type": { "const": "Weather.Snapshotted@v1" },
    "time": { "type": "string", "format": "date-time" },
    "detail": {
      "type": "object",
      "required": ["correlationId", "causationId", "plotId", "dateISO", "temperature", "humidity", "precipitation"],
      "properties": {
        "correlationId": { "type": "string", "format": "uuid" },
        "causationId": { "type": "string", "format": "uuid" },
        "plotId": { "type": "string" },
        "dateISO": { "type": "string", "format": "date" },
        "temperature": { "type": "number" },
        "humidity": { "type": "number", "minimum": 0, "maximum": 100 },
        "precipitation": { "type": "number", "minimum": 0 },
        "windSpeed": { "type": "number", "minimum": 0 },
        "provider": { "enum": ["AccuWeather", "OpenWeather"] }
      }
    }
  }
};

export const CHECKPOINT_EMITTED_SCHEMA = {
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["source", "detail-type", "detail", "time"],
  "properties": {
    "source": { "const": "Ledger.Blockchain" },
    "detail-type": { "const": "Checkpoint.Emitted@v1" },
    "time": { "type": "string", "format": "date-time" },
    "detail": {
      "type": "object",
      "required": ["correlationId", "causationId", "batchId", "txHash", "blockNumber"],
      "properties": {
        "correlationId": { "type": "string", "format": "uuid" },
        "causationId": { "type": "string", "format": "uuid" },
        "batchId": { "type": "string" },
        "txHash": { "type": "string", "pattern": "^0x[a-fA-F0-9]{64}$" },
        "blockNumber": { "type": "number", "minimum": 0 },
        "confirmations": { "type": "number", "minimum": 0 },
        "gasUsed": { "type": "number", "minimum": 0 },
        "network": { "enum": ["sepolia", "mainnet"] }
      }
    }
  }
};