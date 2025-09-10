#!/usr/bin/env ts-node

import { DynamoDBClient, PutItemCommand } from '@aws-sdk/client-dynamodb';

const dynamodb = new DynamoDBClient({
    region: process.env.AWS_REGION || 'us-east-1'
});

const ENVIRONMENT = process.env.ENVIRONMENT || 'dev';
const ORG = process.env.TENANT_ID || 'org-main';
const FARMS_TABLE = `C_N-Registry-Farms-${ENVIRONMENT}`;

interface Farm {
    id: string;
    name: string;
    region: string;
    hectares: number;
    status: 'active' | 'paused';
    geometry?: any;
    metadata?: any;
}

const DEMO_FARMS: Farm[] = [
    {
        id: '2BH',
        name: 'Two Butterflies Homestead',
        region: 'Uasin Gishu',
        hectares: 1.2,
        status: 'active',
        geometry: {
            type: 'Feature',
            geometry: {
                type: 'Polygon',
                coordinates: [[[35.5, -1.2], [35.6, -1.2], [35.6, -1.1], [35.5, -1.1], [35.5, -1.2]]]
            },
            properties: {
                elevation_m: 2100,
                slope_deg: 5.2
            }
        },
        metadata: {
            established_year: 2018,
            coffee_varieties: ['SL28', 'SL34'],
            certification: 'Fair Trade',
            processing_method: 'washed',
            harvest_season: 'October-December'
        }
    },
    {
        id: 'NJY',
        name: "Noah's Joy Coffee Farm",
        region: 'Kiambu',
        hectares: 0.8,
        status: 'active',
        geometry: {
            type: 'Feature',
            geometry: {
                type: 'Polygon',
                coordinates: [[[36.8, -1.0], [36.9, -1.0], [36.9, -0.9], [36.8, -0.9], [36.8, -1.0]]]
            },
            properties: {
                elevation_m: 1800,
                slope_deg: 8.1
            }
        },
        metadata: {
            established_year: 2015,
            coffee_varieties: ['Ruiru 11', 'Batian'],
            certification: 'Organic',
            processing_method: 'natural',
            harvest_season: 'November-January'
        }
    },
    {
        id: 'KMU',
        name: 'Kiambu Model Farm',
        region: 'Kiambu',
        hectares: 2.5,
        status: 'active',
        geometry: {
            type: 'Feature',
            geometry: {
                type: 'Polygon',
                coordinates: [[[36.7, -1.1], [36.8, -1.1], [36.8, -1.0], [36.7, -1.0], [36.7, -1.1]]]
            },
            properties: {
                elevation_m: 1900,
                slope_deg: 3.8
            }
        },
        metadata: {
            established_year: 2012,
            coffee_varieties: ['SL28', 'K7'],
            certification: 'Rainforest Alliance',
            processing_method: 'honey',
            harvest_season: 'October-January'
        }
    },
    {
        id: 'NYR',
        name: 'Nyeri Highlands Cooperative',
        region: 'Nyeri',
        hectares: 5.2,
        status: 'active',
        geometry: {
            type: 'Feature',
            geometry: {
                type: 'Polygon',
                coordinates: [[[37.0, -0.5], [37.1, -0.5], [37.1, -0.4], [37.0, -0.4], [37.0, -0.5]]]
            },
            properties: {
                elevation_m: 2200,
                slope_deg: 12.5
            }
        },
        metadata: {
            established_year: 2008,
            coffee_varieties: ['SL34', 'Ruiru 11'],
            certification: 'UTZ Certified',
            processing_method: 'washed',
            harvest_season: 'November-December'
        }
    },
    {
        id: 'MRG',
        name: 'Murang\'a Valley Estate',
        region: 'Murang\'a',
        hectares: 3.1,
        status: 'active',
        geometry: {
            type: 'Feature',
            geometry: {
                type: 'Polygon',
                coordinates: [[[37.2, -0.8], [37.3, -0.8], [37.3, -0.7], [37.2, -0.7], [37.2, -0.8]]]
            },
            properties: {
                elevation_m: 1950,
                slope_deg: 6.7
            }
        },
        metadata: {
            established_year: 2010,
            coffee_varieties: ['SL28', 'Batian'],
            certification: 'C.A.F.E. Practices',
            processing_method: 'semi-washed',
            harvest_season: 'October-December'
        }
    },
    {
        id: 'KRC',
        name: 'Kirinyaga Central Farm',
        region: 'Kirinyaga',
        hectares: 1.9,
        status: 'active',
        geometry: {
            type: 'Feature',
            geometry: {
                type: 'Polygon',
                coordinates: [[[37.4, -0.6], [37.5, -0.6], [37.5, -0.5], [37.4, -0.5], [37.4, -0.6]]]
            },
            properties: {
                elevation_m: 1850,
                slope_deg: 9.2
            }
        },
        metadata: {
            established_year: 2016,
            coffee_varieties: ['SL34', 'K7'],
            certification: 'Organic',
            processing_method: 'washed',
            harvest_season: 'November-January'
        }
    },
    {
        id: 'EMB',
        name: 'Embu Sunrise Farm',
        region: 'Embu',
        hectares: 1.4,
        status: 'paused',
        geometry: {
            type: 'Feature',
            geometry: {
                type: 'Polygon',
                coordinates: [[[37.6, -0.4], [37.7, -0.4], [37.7, -0.3], [37.6, -0.3], [37.6, -0.4]]]
            },
            properties: {
                elevation_m: 1750,
                slope_deg: 7.9
            }
        },
        metadata: {
            established_year: 2019,
            coffee_varieties: ['Ruiru 11'],
            certification: 'Fair Trade',
            processing_method: 'natural',
            harvest_season: 'November-December',
            pause_reason: 'Soil rehabilitation program'
        }
    },
    {
        id: 'THK',
        name: 'Thika Experimental Station',
        region: 'Kiambu',
        hectares: 4.6,
        status: 'active',
        geometry: {
            type: 'Feature',
            geometry: {
                type: 'Polygon',
                coordinates: [[[37.1, -1.2], [37.2, -1.2], [37.2, -1.1], [37.1, -1.1], [37.1, -1.2]]]
            },
            properties: {
                elevation_m: 1650,
                slope_deg: 4.3
            }
        },
        metadata: {
            established_year: 2005,
            coffee_varieties: ['SL28', 'SL34', 'Ruiru 11', 'Batian'],
            certification: 'Research Station',
            processing_method: 'various',
            harvest_season: 'October-January',
            research_focus: 'Climate resilient varieties'
        }
    }
];

async function seedFarms() {
    console.log(`Seeding farms for ${ENVIRONMENT} environment`);
    console.log(`Table: ${FARMS_TABLE}`);
    console.log(`Organization: ${ORG}`);

    const now = new Date().toISOString();
    let totalSeeded = 0;

    for (const farm of DEMO_FARMS) {
        const PK = `org#${ORG}`;
        const SK = `farm#${farm.id}`;

        const item = {
            PK: { S: PK },
            SK: { S: SK },
            id: { S: farm.id },
            name: { S: farm.name },
            region: { S: farm.region },
            hectares: { N: farm.hectares.toString() },
            status: { S: farm.status },
            createdAt: { S: now },
            updatedAt: { S: now }
        };

        // Add geometry if provided
        if (farm.geometry) {
            item.geometry = { S: JSON.stringify(farm.geometry) };
        }

        // Add metadata if provided
        if (farm.metadata) {
            item.metadata = { S: JSON.stringify(farm.metadata) };
        }

        try {
            await dynamodb.send(new PutItemCommand({
                TableName: FARMS_TABLE,
                Item: item
            }));
            
            totalSeeded++;
            console.log(`✓ Seeded farm: ${farm.name} (${farm.id}) - ${farm.hectares}ha`);

        } catch (error) {
            console.error(`✗ Failed to seed farm ${farm.id}:`, error);
        }
    }

    console.log(`✅ Successfully seeded ${totalSeeded}/${DEMO_FARMS.length} farms`);
}

async function main() {
    try {
        await seedFarms();
        console.log('🎉 Farms seeding completed successfully');
    } catch (error) {
        console.error('❌ Error seeding farms:', error);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

export { seedFarms, DEMO_FARMS };