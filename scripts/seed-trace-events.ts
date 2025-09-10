#!/usr/bin/env ts-node

import { DynamoDBClient, PutItemCommand } from '@aws-sdk/client-dynamodb';

const dynamodb = new DynamoDBClient({
    region: process.env.AWS_REGION || 'us-east-1'
});

const ENVIRONMENT = process.env.ENVIRONMENT || 'dev';
const ORG = process.env.TENANT_ID || 'org-main';
const EVENTS_TABLE = `C_N-Events-Trace-${ENVIRONMENT}`;

interface EventTemplate {
    type: string;
    weight: number; // Probability weight
    generatePayload: (batchId?: string, location?: string) => any;
}

const EVENT_TEMPLATES: EventTemplate[] = [
    {
        type: 'batch.created',
        weight: 0.15,
        generatePayload: (batchId, location) => ({
            batch_id: batchId,
            location: location || 'Central Processing',
            farm_ids: [generateFarmId(), generateFarmId()],
            initial_weight_kg: Math.floor(500 + Math.random() * 1000),
            quality_grade: ['A', 'AA', 'AB'][Math.floor(Math.random() * 3)]
        })
    },
    {
        type: 'shipment.scan',
        weight: 0.25,
        generatePayload: (batchId, location) => ({
            batch_id: batchId,
            location: location || randomLocation(),
            status: ['ok', 'ok', 'ok', 'warning'][Math.floor(Math.random() * 4)],
            temperature_c: Math.round((5 + Math.random() * 10) * 10) / 10,
            humidity_pct: Math.round((40 + Math.random() * 30) * 10) / 10
        })
    },
    {
        type: 'quality.check',
        weight: 0.20,
        generatePayload: (batchId, location) => ({
            batch_id: batchId,
            location: location || randomLocation(),
            inspector: randomInspector(),
            score: Math.round((75 + Math.random() * 20) * 10) / 10,
            attributes: {
                aroma: Math.round((7 + Math.random() * 2) * 10) / 10,
                body: Math.round((7 + Math.random() * 2) * 10) / 10,
                acidity: Math.round((6 + Math.random() * 3) * 10) / 10
            },
            passed: Math.random() > 0.1
        })
    },
    {
        type: 'sustainability.measured',
        weight: 0.10,
        generatePayload: (batchId, location) => ({
            batch_id: batchId,
            location: location || randomLocation(),
            carbon_footprint_kg: Math.round((50 + Math.random() * 100) * 100) / 100,
            water_usage_l: Math.floor(800 + Math.random() * 400),
            renewable_energy_pct: Math.round((60 + Math.random() * 35) * 10) / 10,
            certification: randomCertification()
        })
    },
    {
        type: 'farm.harvest',
        weight: 0.10,
        generatePayload: (batchId, location) => ({
            farm_id: generateFarmId(),
            location: location || randomFarmLocation(),
            harvest_date: randomRecentDate(),
            variety: randomCoffeeVariety(),
            yield_kg: Math.floor(100 + Math.random() * 500),
            moisture_pct: Math.round((10 + Math.random() * 5) * 10) / 10
        })
    },
    {
        type: 'shipment.departed',
        weight: 0.12,
        generatePayload: (batchId, location) => ({
            batch_id: batchId,
            origin: location || randomLocation(),
            destination: randomDestination(),
            carrier: randomCarrier(),
            estimated_arrival: futureDate(),
            containers: Math.floor(1 + Math.random() * 5)
        })
    },
    {
        type: 'processing.roasted',
        weight: 0.08,
        generatePayload: (batchId, location) => ({
            batch_id: batchId,
            location: location || 'Roastery',
            roast_profile: randomRoastProfile(),
            temperature_c: Math.floor(200 + Math.random() * 50),
            duration_min: Math.floor(8 + Math.random() * 7),
            output_kg: Math.floor(300 + Math.random() * 200)
        })
    }
];

const LOCATIONS = ['NBO', 'Nairobi', 'Kiambu', 'Uasin Gishu', 'Mombasa', 'Central Processing'];
const FARM_LOCATIONS = ['Uasin Gishu', 'Kiambu', 'Nyeri', 'Kirinyaga', 'Murang\'a'];
const DESTINATIONS = ['Amsterdam', 'Hamburg', 'New York', 'Los Angeles', 'Tokyo', 'London'];
const CARRIERS = ['Maersk', 'MSC', 'DHL', 'FedEx', 'Kenya Airways Cargo'];
const INSPECTORS = ['Inspector A', 'Inspector B', 'Inspector C', 'QA Team Lead'];
const CERTIFICATIONS = ['Fair Trade', 'Organic', 'Rainforest Alliance', 'UTZ Certified'];
const COFFEE_VARIETIES = ['SL28', 'SL34', 'Ruiru 11', 'Batian', 'K7'];
const ROAST_PROFILES = ['Light', 'Medium', 'Medium-Dark', 'Dark', 'City+', 'Full City'];

function randomLocation(): string {
    return LOCATIONS[Math.floor(Math.random() * LOCATIONS.length)];
}

function randomFarmLocation(): string {
    return FARM_LOCATIONS[Math.floor(Math.random() * FARM_LOCATIONS.length)];
}

function randomDestination(): string {
    return DESTINATIONS[Math.floor(Math.random() * DESTINATIONS.length)];
}

function randomCarrier(): string {
    return CARRIERS[Math.floor(Math.random() * CARRIERS.length)];
}

function randomInspector(): string {
    return INSPECTORS[Math.floor(Math.random() * INSPECTORS.length)];
}

function randomCertification(): string {
    return CERTIFICATIONS[Math.floor(Math.random() * CERTIFICATIONS.length)];
}

function randomCoffeeVariety(): string {
    return COFFEE_VARIETIES[Math.floor(Math.random() * COFFEE_VARIETIES.length)];
}

function randomRoastProfile(): string {
    return ROAST_PROFILES[Math.floor(Math.random() * ROAST_PROFILES.length)];
}

function generateFarmId(): string {
    const prefixes = ['2BH', 'NJY', 'KMU', 'NYR', 'ABC', 'DEF'];
    return prefixes[Math.floor(Math.random() * prefixes.length)];
}

function generateBatchId(): string {
    const year = new Date().getFullYear().toString().slice(-2);
    const month = String(new Date().getMonth() + 1).padStart(2, '0');
    const day = String(new Date().getDate()).padStart(2, '0');
    const suffix = Math.random().toString(36).substr(2, 3).toUpperCase();
    return `${year}-${month}${day}-${suffix}`;
}

function randomRecentDate(): string {
    const daysAgo = Math.floor(Math.random() * 30);
    const date = new Date(Date.now() - daysAgo * 24 * 60 * 60 * 1000);
    return date.toISOString().slice(0, 10);
}

function futureDate(): string {
    const daysFromNow = Math.floor(Math.random() * 30) + 5;
    const date = new Date(Date.now() + daysFromNow * 24 * 60 * 60 * 1000);
    return date.toISOString();
}

function selectEventTemplate(): EventTemplate {
    const totalWeight = EVENT_TEMPLATES.reduce((sum, template) => sum + template.weight, 0);
    let random = Math.random() * totalWeight;
    
    for (const template of EVENT_TEMPLATES) {
        random -= template.weight;
        if (random <= 0) {
            return template;
        }
    }
    
    return EVENT_TEMPLATES[0]; // Fallback
}

async function seedTraceEvents() {
    console.log(`Seeding trace events for ${ENVIRONMENT} environment`);
    console.log(`Table: ${EVENTS_TABLE}`);
    console.log(`Organization: ${ORG}`);

    const now = new Date();
    let totalSeeded = 0;

    // Generate events for the last 3 days
    const eventsToGenerate = 500; // Total events across 3 days
    const batchIds = Array.from({ length: 50 }, () => generateBatchId());

    for (let i = 0; i < eventsToGenerate; i++) {
        // Random timestamp within the last 3 days
        const hoursAgo = Math.random() * 72;
        const eventTime = new Date(now.getTime() - hoursAgo * 60 * 60 * 1000);
        const ts = eventTime.toISOString();

        const template = selectEventTemplate();
        const batchId = batchIds[Math.floor(Math.random() * batchIds.length)];
        const payload = template.generatePayload(batchId);

        const PK = `org#${ORG}`;
        const SK = `ts#${ts}`;

        // Add TTL (30 days from now)
        const ttl = Math.floor((Date.now() + 30 * 24 * 60 * 60 * 1000) / 1000);

        const item = {
            PK: { S: PK },
            SK: { S: SK },
            type: { S: template.type },
            actor: { S: `agent_${Math.floor(Math.random() * 10) + 1}` },
            payload: { S: JSON.stringify(payload) },
            ttl: { N: ttl.toString() },
            createdAt: { S: new Date().toISOString() }
        };

        try {
            await dynamodb.send(new PutItemCommand({
                TableName: EVENTS_TABLE,
                Item: item
            }));
            totalSeeded++;

            if (totalSeeded % 50 === 0) {
                console.log(`Seeded ${totalSeeded} events...`);
            }
        } catch (error) {
            console.error(`Failed to seed event ${template.type} at ${ts}:`, error);
        }

        // Small delay to avoid rate limiting
        if (i % 10 === 0) {
            await new Promise(resolve => setTimeout(resolve, 100));
        }
    }

    console.log(`✅ Successfully seeded ${totalSeeded} trace events`);
}

async function main() {
    try {
        await seedTraceEvents();
        console.log('🎉 Trace events seeding completed successfully');
    } catch (error) {
        console.error('❌ Error seeding trace events:', error);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

export { seedTraceEvents };