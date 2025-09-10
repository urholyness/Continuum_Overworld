const { DynamoDBClient } = require('@aws-sdk/client-dynamodb');
const { DynamoDBDocumentClient, QueryCommand } = require('@aws-sdk/lib-dynamodb');

const dynamodb = DynamoDBDocumentClient.from(new DynamoDBClient({}));

exports.handler = async (event) => {
    console.log('Event:', JSON.stringify(event, null, 2));
    
    try {
        // Public endpoint - no authentication required
        // Returns anonymized, delayed trace highlights for public consumption
        
        const queryParams = event.queryStringParameters || {};
        const limit = Math.min(parseInt(queryParams.limit) || 10, 50); // Max 50 highlights
        const org = process.env.TENANT_ID || 'org-main';

        // Get events from 24-48 hours ago (delayed for privacy)
        const now = new Date();
        const from = new Date(now.getTime() - 48 * 60 * 60 * 1000).toISOString(); // 48h ago
        const to = new Date(now.getTime() - 24 * 60 * 60 * 1000).toISOString();   // 24h ago

        const params = {
            TableName: process.env.EVENTS_TABLE,
            KeyConditionExpression: 'PK = :pk AND SK BETWEEN :from AND :to',
            ExpressionAttributeValues: {
                ':pk': `org#${org}`,
                ':from': `ts#${from}`,
                ':to': `ts#${to}`
            },
            ScanIndexForward: false, // Latest events first
            Limit: limit * 3 // Get more events to filter for highlights
        };

        const result = await dynamodb.send(new QueryCommand(params));
        const events = result.Items || [];

        // Filter and anonymize events for public consumption
        const highlights = events
            .filter(item => {
                // Only include certain event types for public highlights
                const publicEventTypes = [
                    'batch.created',
                    'shipment.departed', 
                    'quality.verified',
                    'sustainability.measured'
                ];
                return publicEventTypes.includes(item.type);
            })
            .slice(0, limit)
            .map(item => ({
                id: `highlight_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
                timestamp: item.SK.replace('ts#', ''),
                type: item.type,
                summary: generatePublicSummary(item.type, item.payload),
                metrics: extractPublicMetrics(item.payload),
                location: anonymizeLocation(item.payload?.location)
            }));

        // Add some synthetic highlights if we don't have enough real events
        while (highlights.length < Math.min(limit, 5)) {
            highlights.push(generateSyntheticHighlight(from, to));
        }

        const response = {
            items: highlights,
            count: highlights.length,
            period: {
                from,
                to
            },
            note: "Events are delayed 24-48 hours and anonymized for privacy"
        };

        console.log(`Retrieved ${highlights.length} public highlights`);

        return {
            statusCode: 200,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Cache-Control': 'public, max-age=3600' // 1 hour cache for public data
            },
            body: JSON.stringify(response)
        };

    } catch (error) {
        console.error('Error:', error);
        
        return {
            statusCode: 500,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            body: JSON.stringify({
                error: 'INTERNAL_ERROR',
                message: 'Unable to retrieve highlights at this time'
            })
        };
    }
};

function generatePublicSummary(eventType, payload) {
    const summaries = {
        'batch.created': 'New batch of premium coffee beans processed',
        'shipment.departed': 'Coffee shipment departed for international destination',
        'quality.verified': 'Quality inspection completed with excellent ratings',
        'sustainability.measured': 'Sustainability metrics updated for farm operations'
    };
    
    return summaries[eventType] || 'Agricultural operation completed successfully';
}

function extractPublicMetrics(payload) {
    if (!payload) return null;
    
    // Extract non-sensitive metrics for public display
    const publicMetrics = {};
    
    if (payload.quality_score) {
        publicMetrics.qualityRating = payload.quality_score > 85 ? 'Excellent' : 
                                     payload.quality_score > 70 ? 'Good' : 'Standard';
    }
    
    if (payload.sustainability_score) {
        publicMetrics.sustainabilityRating = payload.sustainability_score > 80 ? 'High' :
                                           payload.sustainability_score > 60 ? 'Medium' : 'Standard';
    }
    
    if (payload.volume && payload.unit) {
        // Round volumes for anonymization
        const volume = Math.round(payload.volume / 100) * 100;
        publicMetrics.approximateVolume = `~${volume} ${payload.unit}`;
    }
    
    return Object.keys(publicMetrics).length > 0 ? publicMetrics : null;
}

function anonymizeLocation(location) {
    if (!location) return 'East Africa';
    
    // Map specific locations to general regions
    const locationMap = {
        'NBO': 'Kenya',
        'Nairobi': 'Kenya', 
        'Uasin Gishu': 'Kenya Highlands',
        'Central Kenya': 'Kenya Highlands',
        'Kiambu': 'Kenya Highlands'
    };
    
    return locationMap[location] || 'East Africa';
}

function generateSyntheticHighlight(from, to) {
    const eventTypes = ['batch.created', 'quality.verified', 'sustainability.measured'];
    const eventType = eventTypes[Math.floor(Math.random() * eventTypes.length)];
    
    const randomTime = new Date(
        new Date(from).getTime() + 
        Math.random() * (new Date(to).getTime() - new Date(from).getTime())
    ).toISOString();
    
    return {
        id: `highlight_synthetic_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        timestamp: randomTime,
        type: eventType,
        summary: generatePublicSummary(eventType, null),
        metrics: {
            qualityRating: Math.random() > 0.3 ? 'Excellent' : 'Good',
            sustainabilityRating: Math.random() > 0.4 ? 'High' : 'Medium'
        },
        location: 'Kenya Highlands'
    };
}