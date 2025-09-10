const { DynamoDBClient } = require('@aws-sdk/client-dynamodb');
const { DynamoDBDocumentClient, QueryCommand } = require('@aws-sdk/lib-dynamodb');

const dynamodb = DynamoDBDocumentClient.from(new DynamoDBClient({}));

exports.handler = async (event) => {
    console.log('Event:', JSON.stringify(event, null, 2));
    
    try {
        // Validate JWT claims - admin required for agent management
        const claims = event.requestContext?.authorizer?.claims;
        const groups = claims?.['cognito:groups'] ? claims['cognito:groups'].split(',') : [];
        
        if (!groups.includes('admin')) {
            return {
                statusCode: 403,
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                body: JSON.stringify({
                    error: 'FORBIDDEN',
                    message: 'Access denied - requires admin role'
                })
            };
        }

        const queryParams = event.queryStringParameters || {};
        const org = queryParams.org || process.env.TENANT_ID || 'org-main';
        const status = queryParams.status;
        const tier = queryParams.tier;
        const role = queryParams.role;

        const params = {
            TableName: process.env.AGENTS_TABLE,
            KeyConditionExpression: 'PK = :pk',
            ExpressionAttributeValues: {
                ':pk': `org#${org}`
            }
        };

        // Add filters
        const filterExpressions = [];
        if (status) {
            filterExpressions.push('#status = :status');
            params.ExpressionAttributeNames = { ...params.ExpressionAttributeNames, '#status': 'status' };
            params.ExpressionAttributeValues[':status'] = status;
        }
        if (tier) {
            filterExpressions.push('tier = :tier');
            params.ExpressionAttributeValues[':tier'] = tier;
        }
        if (role) {
            filterExpressions.push('#role = :role');
            params.ExpressionAttributeNames = { ...params.ExpressionAttributeNames, '#role': 'role' };
            params.ExpressionAttributeValues[':role'] = role;
        }
        
        if (filterExpressions.length > 0) {
            params.FilterExpression = filterExpressions.join(' AND ');
        }

        const result = await dynamodb.send(new QueryCommand(params));

        const agents = (result.Items || []).map(item => ({
            id: item.id,
            name: item.name,
            role: item.role || 'processor',
            tier: item.tier || 'T1',
            status: item.status || 'offline',
            ...(item.lastHeartbeat && { lastHeartbeat: item.lastHeartbeat }),
            ...(item.version && { version: item.version }),
            ...(item.capabilities && { capabilities: item.capabilities }),
            ...(item.metadata && { metadata: item.metadata })
        }));

        // Add synthetic heartbeat and status if missing (for demo purposes)
        agents.forEach(agent => {
            if (!agent.lastHeartbeat) {
                const randomMinutesAgo = Math.floor(Math.random() * 60);
                agent.lastHeartbeat = new Date(Date.now() - randomMinutesAgo * 60000).toISOString();
            }
            
            if (!agent.status || agent.status === 'offline') {
                const now = new Date();
                const heartbeat = new Date(agent.lastHeartbeat);
                const minutesSinceHeartbeat = (now - heartbeat) / (1000 * 60);
                
                if (minutesSinceHeartbeat < 5) {
                    agent.status = 'online';
                } else if (minutesSinceHeartbeat < 15) {
                    agent.status = 'degraded';
                } else {
                    agent.status = 'offline';
                }
            }
        });

        console.log(`Retrieved ${agents.length} agents for org: ${org}`);

        return {
            statusCode: 200,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Cache-Control': 'public, max-age=30' // 30 second cache for agent status
            },
            body: JSON.stringify(agents)
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
                message: 'Internal server error',
                requestId: event.requestContext?.requestId
            })
        };
    }
};