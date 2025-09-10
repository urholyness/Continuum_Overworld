const { DynamoDBClient } = require('@aws-sdk/client-dynamodb');
const { DynamoDBDocumentClient, QueryCommand } = require('@aws-sdk/lib-dynamodb');

const dynamodb = DynamoDBDocumentClient.from(new DynamoDBClient({}));

exports.handler = async (event) => {
    console.log('Event:', JSON.stringify(event, null, 2));
    
    try {
        // Extract query parameters
        const queryParams = event.queryStringParameters || {};
        const org = queryParams.org || process.env.TENANT_ID || 'org-main';
        const from = queryParams.from || new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
        const to = queryParams.to || new Date().toISOString();
        const limit = Math.min(parseInt(queryParams.limit) || 100, 500);
        const cursor = queryParams.cursor;
        const type = queryParams.type;
        const actor = queryParams.actor;

        // Validate JWT claims
        const claims = event.requestContext?.authorizer?.claims;
        const groups = claims?.['cognito:groups'] ? claims['cognito:groups'].split(',') : [];
        
        if (!groups.includes('trace') && !groups.includes('admin')) {
            return {
                statusCode: 403,
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                body: JSON.stringify({
                    error: 'FORBIDDEN',
                    message: 'Access denied - requires trace or admin role'
                })
            };
        }

        const params = {
            TableName: process.env.EVENTS_TABLE,
            KeyConditionExpression: 'PK = :pk AND SK BETWEEN :from AND :to',
            ExpressionAttributeValues: {
                ':pk': `org#${org}`,
                ':from': `ts#${from}`,
                ':to': `ts#${to}`
            },
            ScanIndexForward: false, // Latest events first
            Limit: limit
        };

        // Handle pagination cursor
        if (cursor) {
            try {
                params.ExclusiveStartKey = JSON.parse(Buffer.from(cursor, 'base64').toString('utf8'));
            } catch (error) {
                console.error('Invalid cursor:', error);
                return {
                    statusCode: 400,
                    headers: {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    body: JSON.stringify({
                        error: 'BAD_REQUEST',
                        message: 'Invalid cursor parameter'
                    })
                };
            }
        }

        // Add filters
        const filterExpressions = [];
        if (type) {
            filterExpressions.push('#type = :type');
            params.ExpressionAttributeNames = { ...params.ExpressionAttributeNames, '#type': 'type' };
            params.ExpressionAttributeValues[':type'] = type;
        }
        if (actor) {
            filterExpressions.push('actor = :actor');
            params.ExpressionAttributeValues[':actor'] = actor;
        }
        
        if (filterExpressions.length > 0) {
            params.FilterExpression = filterExpressions.join(' AND ');
        }

        const result = await dynamodb.send(new QueryCommand(params));

        const events = (result.Items || []).map(item => ({
            id: item.SK.replace('ts#', 'evt_' + Date.now() + '_'),
            ts: item.SK.replace('ts#', ''),
            type: item.type || 'event',
            actor: item.actor || null,
            payload: typeof item.payload === 'string' ? JSON.parse(item.payload) : item.payload || {}
        }));

        // Generate next cursor if more results available
        const nextCursor = result.LastEvaluatedKey
            ? Buffer.from(JSON.stringify(result.LastEvaluatedKey)).toString('base64')
            : null;

        const response = {
            items: events,
            nextCursor
        };

        console.log(`Retrieved ${events.length} events for org: ${org}`);

        return {
            statusCode: 200,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
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
                message: 'Internal server error',
                requestId: event.requestContext?.requestId
            })
        };
    }
};