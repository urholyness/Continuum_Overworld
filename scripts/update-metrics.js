#!/usr/bin/env node

const { DynamoDBClient } = require('@aws-sdk/client-dynamodb');
const { DynamoDBDocumentClient, UpdateCommand } = require('@aws-sdk/lib-dynamodb');

const client = new DynamoDBClient({ region: 'eu-central-1' });
const ddb = DynamoDBDocumentClient.from(client);

async function updateMetrics() {
  console.log('📊 Updating farm metrics for 2 Butterflies Homestead (Eldoret, Kenya)...');
  
  try {
    // REAL location: Eldoret, Kenya (elevation 2100m, highland equatorial climate)
    // Remove fake data generation - use actual current conditions or manual input
    
    const timestamp = Date.now();
    const ttl = Math.floor(timestamp/1000) + (30 * 24 * 60 * 60); // 30 days
    
    const command = new UpdateCommand({
      TableName: 'C_N-FarmMetrics-Live-PROD',
      Key: { 
        farmId: '2-butterflies-homestead',
        timestamp: timestamp
      },
      UpdateExpression: 'SET temperature = :t, humidity = :h, ndvi = :n, soilMoisture = :s, #ttl = :ttl',
      ExpressionAttributeNames: {
        '#ttl': 'ttl'
      },
      ExpressionAttributeValues: {
        ':t': parseFloat(temperature.toFixed(1)),
        ':h': parseFloat(humidity.toFixed(0)),
        ':n': parseFloat(ndvi.toFixed(2)),
        ':s': parseFloat(soilMoisture.toFixed(0)),
        ':ttl': ttl
      }
    });
    
    await ddb.send(command);
    
    console.log(`✅ Metrics updated successfully:`);
    console.log(`  Temperature: ${temperature.toFixed(1)}°C`);
    console.log(`  Humidity: ${humidity.toFixed(0)}%`);
    console.log(`  NDVI: ${ndvi.toFixed(2)}`);
    console.log(`  Soil Moisture: ${soilMoisture.toFixed(0)}%`);
    console.log(`  Timestamp: ${new Date(timestamp).toISOString()}`);
    console.log('');
    console.log('📡 Data available via /api/trace/lots endpoint');
    
  } catch (error) {
    console.error('❌ Error updating metrics:', error.message);
    process.exit(1);
  }
}

updateMetrics().catch(console.error);