// File: scripts/migrate-mock-to-seed.ts
// Task 3: Migration script to seed DynamoDB with initial data

import { DynamoDBClient, PutItemCommand, BatchWriteItemCommand } from '@aws-sdk/client-dynamodb';
import { v4 as uuid } from 'uuid';

const ddb = new DynamoDBClient({ 
  region: process.env.AWS_REGION || 'eu-central-1' 
});

// Mock data based on real operational patterns
const mockData = {
  traces: [
    {
      id: 'LOT-2024-FB-001',
      farm: '2 Butterflies Homestead',
      farmId: 'farm-2bh-001',
      product: 'French Beans Extra Fine',
      productCode: 'FB-EF',
      harvestDate: '2024-01-15',
      ndvi: 0.72,
      temperature: 24,
      humidity: 65,
      coordinates: { lat: -0.3656, lng: 36.0822 },
      certifications: ['GlobalG.A.P.', 'EU-Organic'],
      quantity: 2400,
      unit: 'kg'
    },
    {
      id: 'LOT-2024-FB-002',
      farm: 'Sunrise Farm',
      farmId: 'farm-sf-001',
      product: 'French Beans Super Fine',
      productCode: 'FB-SF',
      harvestDate: '2024-01-18',
      ndvi: 0.68,
      temperature: 23,
      humidity: 62,
      coordinates: { lat: -0.2891, lng: 36.0681 },
      certifications: ['GlobalG.A.P.'],
      quantity: 1800,
      unit: 'kg'
    },
    {
      id: 'LOT-2024-CH-001',
      farm: 'Green Valley Cooperative',
      farmId: 'farm-gvc-001',
      product: 'Cayenne Chili',
      productCode: 'CH-CAY',
      harvestDate: '2024-01-20',
      ndvi: 0.75,
      temperature: 26,
      humidity: 58,
      coordinates: { lat: -0.4123, lng: 36.1234 },
      certifications: ['GlobalG.A.P.', 'HACCP'],
      quantity: 800,
      unit: 'kg'
    }
  ],
  
  events: [
    { type: 'harvest', timestamp: '2024-01-15T06:00:00Z', location: 'Field A', farmId: 'farm-2bh-001' },
    { type: 'collection', timestamp: '2024-01-15T09:00:00Z', location: 'Collection Center 1' },
    { type: 'packhouse', timestamp: '2024-01-15T10:00:00Z', location: 'Packhouse 1', temperature: 8 },
    { type: 'pre_cooling', timestamp: '2024-01-15T14:00:00Z', temperature: 6 },
    { type: 'quality_check', timestamp: '2024-01-15T16:00:00Z', status: 'passed', inspector: 'QC-Team-1' },
    { type: 'loading', timestamp: '2024-01-16T06:00:00Z', vehicle: 'KBA-123X' },
    { type: 'export', timestamp: '2024-01-16T08:00:00Z', destination: 'JKIA', airwayBill: 'AWB-123456' },
    { type: 'departure', timestamp: '2024-01-16T22:00:00Z', flight: 'KQ101', destination: 'AMS' }
  ],
  
  metrics: [
    { kpi: 'throughput_tph', value: 1.8, unit: 't/h', description: 'Packhouse throughput' },
    { kpi: 'orders_open', value: 12, unit: 'count', description: 'Open orders' },
    { kpi: 'avg_ndvi', value: 0.71, unit: 'index', description: 'Average NDVI across farms' },
    { kpi: 'export_volume_daily', value: 2400, unit: 'kg', description: 'Daily export volume' },
    { kpi: 'quality_pass_rate', value: 96.5, unit: '%', description: 'Quality check pass rate' },
    { kpi: 'cold_chain_compliance', value: 99.2, unit: '%', description: 'Cold chain compliance rate' }
  ]
};

async function migrateTraces() {
  console.log('Starting trace migration...');
  const timestamp = new Date().toISOString();
  
  for (const trace of mockData.traces) {
    const item = {
      PK: { S: 'org#org-main' },
      SK: { S: `ts#${new Date(trace.harvestDate).toISOString()}#lot#${trace.id}` },
      id: { S: trace.id },
      type: { S: 'harvest' },
      entityType: { S: 'trace' },
      farmId: { S: trace.farmId },
      farmName: { S: trace.farm },
      product: { S: trace.product },
      productCode: { S: trace.productCode },
      harvestDate: { S: trace.harvestDate },
      quantity: { N: String(trace.quantity) },
      unit: { S: trace.unit },
      certifications: { SS: trace.certifications },
      createdAt: { S: timestamp },
      payload: { S: JSON.stringify({
        farm: trace.farm,
        product: trace.product,
        ndvi: trace.ndvi,
        temperature: trace.temperature,
        humidity: trace.humidity,
        coordinates: trace.coordinates,
        certifications: trace.certifications
      })}
    };
    
    try {
      await ddb.send(new PutItemCommand({
        TableName: 'C_N-Events-Trace',
        Item: item
      }));
      console.log(`✓ Migrated trace: ${trace.id}`);
    } catch (error) {
      console.error(`✗ Failed to migrate trace ${trace.id}:`, error);
    }
    
    // Also write satellite data
    await ddb.send(new PutItemCommand({
      TableName: 'C_N-Oracle-SatelliteData',
      Item: {
        plotId: { S: `plot#${trace.farmId}` },
        timestamp: { N: String(new Date(trace.harvestDate).getTime()) },
        GSI1PK: { S: 'SATELLITE' },
        ndvi: { N: String(trace.ndvi) },
        cloudCover: { N: String(Math.random() * 20) }, // Random cloud cover
        coordinates: { S: JSON.stringify(trace.coordinates) },
        imageUrl: { S: `s3://satellite-images/${trace.farmId}/${trace.harvestDate}.tif` },
        createdAt: { S: timestamp }
      }
    }));
    
    // Write weather data
    await ddb.send(new PutItemCommand({
      TableName: 'C_N-Oracle-WeatherData',
      Item: {
        locationId: { S: `loc#${trace.farmId}` },
        timestamp: { N: String(new Date(trace.harvestDate).getTime()) },
        GSI1PK: { S: 'WEATHER' },
        temperature: { N: String(trace.temperature) },
        humidity: { N: String(trace.humidity) },
        precipitation: { N: String(Math.random() * 5) }, // Random precipitation
        windSpeed: { N: String(5 + Math.random() * 10) }, // Random wind speed
        coordinates: { S: JSON.stringify(trace.coordinates) },
        source: { S: 'OpenWeather' },
        createdAt: { S: timestamp }
      }
    }));
  }
  
  console.log(`✓ Migrated ${mockData.traces.length} traces with satellite and weather data`);
}

async function migrateEvents() {
  console.log('Starting event migration...');
  const baseTimestamp = new Date('2024-01-15').getTime();
  
  for (let i = 0; i < mockData.events.length; i++) {
    const event = mockData.events[i];
    const eventTimestamp = new Date(event.timestamp).getTime();
    
    const item = {
      PK: { S: 'org#org-main' },
      SK: { S: `ts#${event.timestamp}#evt#${uuid()}` },
      type: { S: event.type },
      entityType: { S: 'event' },
      timestamp: { N: String(eventTimestamp) },
      location: { S: event.location || 'Unknown' },
      payload: { S: JSON.stringify(event) },
      TTL: { N: String(Math.floor(Date.now() / 1000) + (30 * 24 * 60 * 60)) } // 30 days TTL
    };
    
    // Add type-specific attributes
    if (event.temperature !== undefined) {
      item['temperature'] = { N: String(event.temperature) };
    }
    if (event.status) {
      item['status'] = { S: event.status };
    }
    if (event.vehicle) {
      item['vehicle'] = { S: event.vehicle };
    }
    
    try {
      await ddb.send(new PutItemCommand({
        TableName: 'C_N-Events-Trace',
        Item: item
      }));
      console.log(`✓ Migrated event: ${event.type} at ${event.timestamp}`);
    } catch (error) {
      console.error(`✗ Failed to migrate event:`, error);
    }
  }
  
  console.log(`✓ Migrated ${mockData.events.length} events`);
}

async function createMetrics() {
  console.log('Creating operational metrics...');
  const date = new Date().toISOString().slice(0, 10).replace(/-/g, '');
  const timestamp = new Date().toISOString();
  
  for (const metric of mockData.metrics) {
    const item = {
      PK: { S: `org#org-main#date#${date}` },
      SK: { S: `kpi#${metric.kpi}#ts#${timestamp}` },
      kpi: { S: metric.kpi },
      value: { N: String(metric.value) },
      unit: { S: metric.unit },
      description: { S: metric.description },
      timestamp: { S: timestamp },
      TTL: { N: String(Math.floor(Date.now() / 1000) + (90 * 24 * 60 * 60)) } // 90 days TTL
    };
    
    try {
      await ddb.send(new PutItemCommand({
        TableName: 'C_N-Metrics-Operational',
        Item: item
      }));
      console.log(`✓ Created metric: ${metric.kpi} = ${metric.value} ${metric.unit}`);
    } catch (error) {
      console.error(`✗ Failed to create metric ${metric.kpi}:`, error);
    }
  }
  
  // Also create metric definitions
  for (const metric of mockData.metrics) {
    await ddb.send(new PutItemCommand({
      TableName: 'C_N-MetricDefinitions',
      Item: {
        PK: { S: 'METRIC' },
        SK: { S: `kpi#${metric.kpi}` },
        name: { S: metric.kpi },
        unit: { S: metric.unit },
        description: { S: metric.description },
        category: { S: metric.kpi.includes('ndvi') ? 'environmental' : 'operational' },
        displayName: { S: metric.description },
        aggregationType: { S: metric.unit === '%' ? 'average' : 'sum' },
        createdAt: { S: timestamp }
      }
    }));
  }
  
  console.log(`✓ Created ${mockData.metrics.length} operational metrics and definitions`);
}

async function createBlockchainRecords() {
  console.log('Creating blockchain records...');
  
  // Create sample blockchain transactions for traceability
  for (const trace of mockData.traces) {
    const txHash = '0x' + Buffer.from(trace.id).toString('hex').padEnd(64, '0');
    
    await ddb.send(new PutItemCommand({
      TableName: 'C_N-Events-Trace',
      Item: {
        PK: { S: 'org#org-main' },
        SK: { S: `blockchain#${txHash}` },
        type: { S: 'blockchain_tx' },
        entityType: { S: 'blockchain' },
        timestamp: { N: String(new Date(trace.harvestDate).getTime()) },
        txHash: { S: txHash },
        blockNumber: { N: String(15000000 + Math.floor(Math.random() * 1000)) },
        contractAddress: { S: '0x1234567890abcdef1234567890abcdef12345678' },
        gasUsed: { N: '21000' },
        status: { S: 'confirmed' },
        lotId: { S: trace.id },
        payload: { S: JSON.stringify({
          action: 'registerHarvest',
          lotId: trace.id,
          farm: trace.farm,
          product: trace.product,
          quantity: trace.quantity,
          timestamp: trace.harvestDate
        })}
      }
    }));
    
    console.log(`✓ Created blockchain record for ${trace.id}`);
  }
}

// Main execution
(async () => {
  console.log('=================================');
  console.log('Mock to Real Data Migration');
  console.log('=================================');
  console.log(`Region: ${process.env.AWS_REGION || 'eu-central-1'}`);
  console.log(`Starting at: ${new Date().toISOString()}`);
  console.log('---------------------------------');
  
  try {
    await migrateTraces();
    console.log('---------------------------------');
    await migrateEvents();
    console.log('---------------------------------');
    await createMetrics();
    console.log('---------------------------------');
    await createBlockchainRecords();
    console.log('=================================');
    console.log('✓ Migration completed successfully');
    console.log(`Finished at: ${new Date().toISOString()}`);
  } catch (error) {
    console.error('=================================');
    console.error('✗ Migration failed:', error);
    process.exit(1);
  }
})();
