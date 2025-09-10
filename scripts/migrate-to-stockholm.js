#!/usr/bin/env node

const { DynamoDBClient } = require('@aws-sdk/client-dynamodb');
const { DynamoDBDocumentClient, ScanCommand, PutCommand } = require('@aws-sdk/lib-dynamodb');

// Source: Frankfurt
const sourceClient = new DynamoDBClient({ region: 'eu-central-1' });
const sourceDocClient = DynamoDBDocumentClient.from(sourceClient);

// Target: Stockholm  
const targetClient = new DynamoDBClient({ region: 'eu-north-1' });
const targetDocClient = DynamoDBDocumentClient.from(targetClient);

async function migrateTable(tableName) {
  console.log(`🔄 Migrating ${tableName} from Frankfurt to Stockholm...`);
  
  try {
    // Scan all items from Frankfurt
    const scanCommand = new ScanCommand({
      TableName: tableName
    });
    
    const result = await sourceDocClient.send(scanCommand);
    console.log(`📊 Found ${result.Items?.length || 0} items in ${tableName}`);
    
    if (!result.Items || result.Items.length === 0) {
      console.log(`✅ No data to migrate for ${tableName}`);
      return;
    }
    
    // Put items into Stockholm
    for (const item of result.Items) {
      const putCommand = new PutCommand({
        TableName: tableName,
        Item: item
      });
      
      await targetDocClient.send(putCommand);
      console.log(`  ✓ Migrated item: ${item.farmId || item.connectionId || item.shipmentId}`);
    }
    
    console.log(`✅ Successfully migrated ${tableName} to Stockholm`);
    
  } catch (error) {
    console.error(`❌ Migration failed for ${tableName}:`, error.message);
    
    if (error.name === 'ResourceNotFoundException') {
      console.log(`⚠️  Table ${tableName} not found. Ensure tables exist in both regions.`);
    }
  }
}

async function main() {
  console.log('🚀 Starting Stockholm Migration');
  console.log('Source: eu-central-1 (Frankfurt)');
  console.log('Target: eu-north-1 (Stockholm)');
  console.log('');
  
  const tables = [
    'C_N-FarmMetrics-Live-PROD',
    'C_N-WebSocketConnections-PROD', 
    'C_N-ShipmentTracking-Active-PROD'
  ];
  
  for (const table of tables) {
    await migrateTable(table);
    console.log('');
  }
  
  console.log('🎉 Stockholm migration completed!');
  console.log('');
  console.log('Next steps:');
  console.log('1. Update Amplify environment: AWS_REGION=eu-north-1');
  console.log('2. Test API endpoints');
  console.log('3. Verify all services work');
  console.log('4. Clean up Frankfurt tables after verification');
}

main().catch(console.error);