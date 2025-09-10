#!/usr/bin/env ts-node

import { DynamoDBClient, PutItemCommand } from '@aws-sdk/client-dynamodb';

const dynamodb = new DynamoDBClient({
    region: process.env.AWS_REGION || 'us-east-1'
});

const ENVIRONMENT = process.env.ENVIRONMENT || 'dev';
const ORG = process.env.TENANT_ID || 'org-main';
const METRICS_TABLE = `C_N-Metrics-Operational-${ENVIRONMENT}`;

interface MetricDef {
    kpi: string;
    unit: string;
    baseValue: number;
    variance: number;
}

const METRIC_DEFINITIONS: MetricDef[] = [
    { kpi: 'throughput_tph', unit: 't/h', baseValue: 1.8, variance: 0.3 },
    { kpi: 'orders_open', unit: 'count', baseValue: 12, variance: 8 },
    { kpi: 'temp_packhouse', unit: '°C', baseValue: 6.1, variance: 2.0 },
    { kpi: 'lots_processed_24h', unit: 'count', baseValue: 22, variance: 10 },
    { kpi: 'quality_pass_rate', unit: '%', baseValue: 89.5, variance: 7 },
    { kpi: 'avg_ndvi', unit: 'index', baseValue: 0.75, variance: 0.15 },
    { kpi: 'avg_ndwi', unit: 'index', baseValue: 0.25, variance: 0.1 },
    { kpi: 'vegetation_health_pct', unit: '%', baseValue: 82, variance: 12 },
    { kpi: 'rainfall_mm_24h', unit: 'mm', baseValue: 3.2, variance: 8 },
    { kpi: 'avg_temp_24h', unit: '°C', baseValue: 23.5, variance: 4 }
];

async function seedOperationalMetrics() {
    console.log(`Seeding operational metrics for ${ENVIRONMENT} environment`);
    console.log(`Table: ${METRICS_TABLE}`);
    console.log(`Organization: ${ORG}`);

    const now = new Date();
    let totalSeeded = 0;

    // Seed data for the last 7 days
    for (let daysAgo = 0; daysAgo < 7; daysAgo++) {
        const targetDate = new Date(now.getTime() - daysAgo * 24 * 60 * 60 * 1000);
        const dateStr = targetDate.toISOString().slice(0, 10).replace(/-/g, '');
        
        console.log(`Seeding metrics for date: ${dateStr}`);

        // Generate metrics every hour for this day
        for (let hour = 0; hour < 24; hour++) {
            const timestamp = new Date(targetDate);
            timestamp.setHours(hour, 0, 0, 0);
            const ts = timestamp.toISOString();

            for (const metric of METRIC_DEFINITIONS) {
                const PK = `org#${ORG}#date#${dateStr}`;
                const SK = `kpi#${metric.kpi}#ts#${ts}`;

                // Generate realistic value with some variance
                const variance = (Math.random() - 0.5) * metric.variance;
                let value = metric.baseValue + variance;
                
                // Ensure percentage values stay within bounds
                if (metric.unit === '%') {
                    value = Math.max(0, Math.min(100, value));
                }
                
                // Ensure non-negative values for counts and measurements
                if (metric.unit === 'count' || metric.kpi.includes('rainfall')) {
                    value = Math.max(0, value);
                }

                // Round to appropriate precision
                if (metric.unit === 'count') {
                    value = Math.floor(value);
                } else {
                    value = Math.round(value * 100) / 100;
                }

                const item = {
                    PK: { S: PK },
                    SK: { S: SK },
                    kpi: { S: metric.kpi },
                    value: { N: value.toString() },
                    unit: { S: metric.unit },
                    ts: { S: ts },
                    computedAt: { S: new Date().toISOString() }
                };

                try {
                    await dynamodb.send(new PutItemCommand({
                        TableName: METRICS_TABLE,
                        Item: item
                    }));
                    totalSeeded++;
                } catch (error) {
                    console.error(`Failed to seed metric ${metric.kpi} at ${ts}:`, error);
                }
            }
        }
    }

    console.log(`✅ Successfully seeded ${totalSeeded} operational metrics`);
}

async function main() {
    try {
        await seedOperationalMetrics();
        console.log('🎉 Operational metrics seeding completed successfully');
    } catch (error) {
        console.error('❌ Error seeding operational metrics:', error);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

export { seedOperationalMetrics };