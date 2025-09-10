#!/usr/bin/env ts-node

import { DynamoDBClient, PutItemCommand } from '@aws-sdk/client-dynamodb';

const dynamodb = new DynamoDBClient({
    region: process.env.AWS_REGION || 'us-east-1'
});

const ENVIRONMENT = process.env.ENVIRONMENT || 'dev';
const ORG = process.env.TENANT_ID || 'org-main';
const AGENTS_TABLE = `C_N-Pantheon-Registry-${ENVIRONMENT}`;

interface Agent {
    id: string;
    name: string;
    role: string;
    tier: string;
    status: 'online' | 'degraded' | 'offline';
    version?: string;
    capabilities?: string[];
    metadata?: any;
}

const DEMO_AGENTS: Agent[] = [
    {
        id: 'agent_001',
        name: 'Satellite Data Processor',
        role: 'processor',
        tier: 'T1',
        status: 'online',
        version: '2.4.1',
        capabilities: ['ndvi', 'ndwi', 'sentinel-2', 'landsat-8'],
        metadata: {
            last_deployment: '2023-09-01T10:00:00Z',
            processing_capacity: '500GB/hour',
            supported_formats: ['GeoTIFF', 'NetCDF', 'HDF5'],
            geographic_coverage: 'East Africa'
        }
    },
    {
        id: 'agent_002',
        name: 'Quality Analyzer',
        role: 'analyzer',
        tier: 'T2',
        status: 'online',
        version: '1.8.3',
        capabilities: ['quality-assessment', 'defect-detection', 'grading'],
        metadata: {
            last_deployment: '2023-08-25T14:30:00Z',
            analysis_types: ['visual', 'spectral', 'physical'],
            accuracy_rate: '94.2%',
            throughput: '150 samples/hour'
        }
    },
    {
        id: 'agent_003',
        name: 'Weather Aggregator',
        role: 'aggregator',
        tier: 'T1',
        status: 'degraded',
        version: '3.1.0',
        capabilities: ['weather-data', 'climate-modeling', 'forecasting'],
        metadata: {
            last_deployment: '2023-08-30T09:15:00Z',
            data_sources: ['OpenWeather', 'NOAA', 'Kenya Met'],
            update_frequency: '15 minutes',
            forecast_range: '7 days',
            degraded_reason: 'Limited connectivity to external APIs'
        }
    },
    {
        id: 'agent_004',
        name: 'Blockchain Anchor',
        role: 'anchor',
        tier: 'T1',
        status: 'online',
        version: '4.2.1',
        capabilities: ['blockchain-write', 'hash-verification', 'smart-contracts'],
        metadata: {
            last_deployment: '2023-09-05T16:20:00Z',
            blockchain_network: 'Sepolia Testnet',
            contract_address: '0x742d35Cc6632C0532c718D28C0a3a7d3C6f4A25B',
            gas_optimization: 'enabled',
            transaction_rate: '5 tx/min'
        }
    },
    {
        id: 'agent_005',
        name: 'Farm Monitor',
        role: 'monitor',
        tier: 'T2',
        status: 'online',
        version: '2.1.7',
        capabilities: ['iot-sensors', 'alerts', 'anomaly-detection'],
        metadata: {
            last_deployment: '2023-08-28T11:45:00Z',
            sensor_types: ['temperature', 'humidity', 'soil-moisture', 'ph'],
            farms_monitored: 8,
            alert_threshold: '95th percentile',
            battery_status: 'good'
        }
    },
    {
        id: 'agent_006',
        name: 'Supply Chain Tracker',
        role: 'tracker',
        tier: 'T1',
        status: 'online',
        version: '3.3.2',
        capabilities: ['shipment-tracking', 'logistics', 'route-optimization'],
        metadata: {
            last_deployment: '2023-09-02T13:10:00Z',
            carriers_integrated: ['Maersk', 'DHL', 'Kenya Airways'],
            tracking_accuracy: '99.1%',
            route_optimization: 'ML-powered',
            api_rate_limit: '1000 calls/hour'
        }
    },
    {
        id: 'agent_007',
        name: 'Market Price Oracle',
        role: 'oracle',
        tier: 'T2',
        status: 'online',
        version: '1.9.4',
        capabilities: ['price-feeds', 'market-analysis', 'trend-prediction'],
        metadata: {
            last_deployment: '2023-08-31T08:30:00Z',
            data_sources: ['ICE Futures', 'NYBOT', 'Local Markets'],
            update_frequency: '1 hour',
            prediction_accuracy: '78.5%',
            currencies: ['USD', 'KES', 'EUR']
        }
    },
    {
        id: 'agent_008',
        name: 'Carbon Calculator',
        role: 'calculator',
        tier: 'T2',
        status: 'degraded',
        version: '2.7.1',
        capabilities: ['carbon-footprint', 'lifecycle-analysis', 'sustainability'],
        metadata: {
            last_deployment: '2023-08-27T15:45:00Z',
            calculation_standards: ['GHG Protocol', 'ISO 14067'],
            accuracy_level: '±5%',
            processing_time: '2.3 seconds/batch',
            degraded_reason: 'High computational load affecting performance'
        }
    },
    {
        id: 'agent_009',
        name: 'Document Processor',
        role: 'processor',
        tier: 'T3',
        status: 'online',
        version: '1.4.8',
        capabilities: ['ocr', 'document-parsing', 'data-extraction'],
        metadata: {
            last_deployment: '2023-09-03T12:00:00Z',
            supported_formats: ['PDF', 'PNG', 'JPEG', 'TIFF'],
            languages: ['en', 'sw', 'fr'],
            accuracy_rate: '96.7%',
            throughput: '50 documents/minute'
        }
    },
    {
        id: 'agent_010',
        name: 'Compliance Checker',
        role: 'validator',
        tier: 'T1',
        status: 'offline',
        version: '2.2.3',
        capabilities: ['regulation-compliance', 'certification-validation', 'audit-trails'],
        metadata: {
            last_deployment: '2023-08-20T10:15:00Z',
            compliance_standards: ['Fair Trade', 'Organic', 'Rainforest Alliance'],
            last_update: '2023-08-20T10:15:00Z',
            offline_reason: 'Scheduled maintenance for security updates',
            expected_online: '2023-09-10T09:00:00Z'
        }
    }
];

async function seedAgents() {
    console.log(`Seeding agents for ${ENVIRONMENT} environment`);
    console.log(`Table: ${AGENTS_TABLE}`);
    console.log(`Organization: ${ORG}`);

    const now = new Date();
    let totalSeeded = 0;

    for (const agent of DEMO_AGENTS) {
        const PK = `org#${ORG}`;
        const SK = `agent#${agent.id}`;

        // Generate realistic lastHeartbeat based on status
        let lastHeartbeat: Date;
        switch (agent.status) {
            case 'online':
                lastHeartbeat = new Date(now.getTime() - Math.random() * 5 * 60 * 1000); // 0-5 minutes ago
                break;
            case 'degraded':
                lastHeartbeat = new Date(now.getTime() - (5 + Math.random() * 10) * 60 * 1000); // 5-15 minutes ago
                break;
            case 'offline':
                lastHeartbeat = new Date(now.getTime() - (30 + Math.random() * 120) * 60 * 1000); // 30-150 minutes ago
                break;
        }

        const item = {
            PK: { S: PK },
            SK: { S: SK },
            id: { S: agent.id },
            name: { S: agent.name },
            role: { S: agent.role },
            tier: { S: agent.tier },
            status: { S: agent.status },
            lastHeartbeat: { S: lastHeartbeat.toISOString() },
            createdAt: { S: now.toISOString() },
            updatedAt: { S: now.toISOString() }
        };

        // Add version if provided
        if (agent.version) {
            item.version = { S: agent.version };
        }

        // Add capabilities if provided
        if (agent.capabilities && agent.capabilities.length > 0) {
            item.capabilities = { SS: agent.capabilities };
        }

        // Add metadata if provided
        if (agent.metadata) {
            item.metadata = { S: JSON.stringify(agent.metadata) };
        }

        try {
            await dynamodb.send(new PutItemCommand({
                TableName: AGENTS_TABLE,
                Item: item
            }));
            
            totalSeeded++;
            console.log(`✓ Seeded agent: ${agent.name} (${agent.id}) - ${agent.status}`);

        } catch (error) {
            console.error(`✗ Failed to seed agent ${agent.id}:`, error);
        }
    }

    console.log(`✅ Successfully seeded ${totalSeeded}/${DEMO_AGENTS.length} agents`);
}

async function main() {
    try {
        await seedAgents();
        console.log('🎉 Agents seeding completed successfully');
    } catch (error) {
        console.error('❌ Error seeding agents:', error);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

export { seedAgents, DEMO_AGENTS };