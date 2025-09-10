#!/usr/bin/env node

const { DynamoDBClient } = require('@aws-sdk/client-dynamodb');
const { DynamoDBDocumentClient, PutCommand } = require('@aws-sdk/lib-dynamodb');

// Configure for Frankfurt region
const client = new DynamoDBClient({ 
  region: 'eu-central-1',
  // Will use IAM role or environment credentials
});
const ddb = DynamoDBDocumentClient.from(client);

// REAL farm data - 2 Butterflies Homestead
const farms = [
  {
    farmId: "2-butterflies-homestead",
    name: "2 Butterflies Homestead", 
    latitude: 0.5143,     // Eldoret, Kenya coordinates
    longitude: 35.2698,   // Eldoret, Kenya coordinates
    location: "Eldoret, Kenya",
    cropType: "Phaseolus Vulgaris",
    variety: "Bean STAR 2054",
    grade: "Fine",
    owner: "GSG-KE-UG",
    sizeHectares: 9,      // 9 acres converted to hectares (3.64 hectares)
    sizeAcres: 9,
    certifications: ["GlobalGAP", "KEPHIS"],
    status: "active",
    registered: "2025-01-10",
    timestamp: Date.now(),
    ttl: Math.floor(Date.now()/1000) + (30 * 24 * 60 * 60) // 30 days TTL
  }
];

async function seedFarms() {
  console.log('🌱 Seeding farm data to C_N-FarmMetrics-Live-PROD...');
  console.log(`Region: eu-central-1`);
  console.log(`Table: C_N-FarmMetrics-Live-PROD`);
  console.log('');

  try {
    for (const farm of farms) {
      console.log(`Adding: ${farm.name}`);
      console.log(`  Location: ${farm.location}`);
      console.log(`  Coordinates: ${farm.latitude}, ${farm.longitude}`);
      console.log(`  Crop: ${farm.variety} (${farm.grade})`);
      
      const command = new PutCommand({
        TableName: 'C_N-FarmMetrics-Live-PROD',
        Item: farm
      });
      
      await ddb.send(command);
      console.log(`  ✅ Successfully added to DynamoDB`);
      console.log('');
    }
    
    console.log('🎉 Farm seeding completed successfully!');
    console.log('');
    console.log('Next steps:');
    console.log('1. Update Amplify environment variables');
    console.log('2. Deploy API changes');
    console.log('3. Test /api/trace/lots endpoint');
    
  } catch (error) {
    console.error('❌ Error seeding farms:', error.message);
    console.error('');
    console.error('Possible issues:');
    console.error('1. AWS credentials not configured');
    console.error('2. DynamoDB table does not exist');
    console.error('3. Insufficient IAM permissions');
    console.error('');
    console.error('Check AWS configuration and table status in Frankfurt (eu-central-1)');
    process.exit(1);
  }
}

// Run the seeding
seedFarms().catch(console.error);