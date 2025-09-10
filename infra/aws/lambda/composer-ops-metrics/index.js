const { DynamoDBClient } = require('@aws-sdk/client-dynamodb');
const { DynamoDBDocumentClient, QueryCommand } = require('@aws-sdk/lib-dynamodb');

const dynamodb = DynamoDBDocumentClient.from(new DynamoDBClient({}));

exports.handler = async (event) => {
    console.log('Event:', JSON.stringify(event, null, 2));
    
    try {
        // Extract query parameters
        const queryParams = event.queryStringParameters || {};
        const org = queryParams.org || process.env.TENANT_ID || 'org-main';
        const from = queryParams.from ? new Date(queryParams.from) : new Date(Date.now() - 24 * 60 * 60 * 1000);
        const to = queryParams.to ? new Date(queryParams.to) : new Date();
        const kpis = queryParams.kpis ? queryParams.kpis.split(',') : null;

        // Validate JWT claims (passed from API Gateway)
        const claims = event.requestContext?.authorizer?.claims;
        const groups = claims?.['cognito:groups'] ? claims['cognito:groups'].split(',') : [];
        
        if (!groups.includes('ops') && !groups.includes('admin')) {
            return {
                statusCode: 403,
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                body: JSON.stringify({
                    error: 'FORBIDDEN',
                    message: 'Access denied - requires ops or admin role'
                })
            };
        }

        const metrics = [];
        const startDate = from.toISOString().slice(0, 10).replace(/-/g, '');
        const endDate = to.toISOString().slice(0, 10).replace(/-/g, '');

        // Query metrics for each date in the range
        const dates = getDateRange(startDate, endDate);
        
        for (const date of dates) {
            const PK = `org#${org}#date#${date}`;
            
            const params = {
                TableName: process.env.METRICS_TABLE,
                KeyConditionExpression: 'PK = :pk',
                ExpressionAttributeValues: {
                    ':pk': PK
                },
                ScanIndexForward: false,
                Limit: 1000
            };

            // Add KPI filter if specified
            if (kpis && kpis.length > 0) {
                params.FilterExpression = 'contains(:kpis, kpi)';
                params.ExpressionAttributeValues[':kpis'] = kpis.join(',');
            }

            // Add time range filter
            params.FilterExpression = params.FilterExpression 
                ? `${params.FilterExpression} AND #ts BETWEEN :from AND :to`
                : '#ts BETWEEN :from AND :to';
            params.ExpressionAttributeNames = { '#ts': 'ts' };
            params.ExpressionAttributeValues[':from'] = from.toISOString();
            params.ExpressionAttributeValues[':to'] = to.toISOString();

            const result = await dynamodb.send(new QueryCommand(params));
            
            if (result.Items) {
                metrics.push(...result.Items.map(item => ({
                    kpi: item.kpi,
                    value: parseFloat(item.value),
                    unit: item.unit,
                    ts: item.ts,
                    ...(item.metadata && { metadata: item.metadata })
                })));
            }
        }

        // Sort by timestamp descending
        metrics.sort((a, b) => new Date(b.ts) - new Date(a.ts));

        console.log(`Retrieved ${metrics.length} metrics for org: ${org}`);

        return {
            statusCode: 200,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Cache-Control': 'public, max-age=60' // 1 minute cache
            },
            body: JSON.stringify(metrics)
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

function getDateRange(startDate, endDate) {
    const dates = [];
    const current = new Date(
        parseInt(startDate.slice(0, 4)),
        parseInt(startDate.slice(4, 6)) - 1,
        parseInt(startDate.slice(6, 8))
    );
    const end = new Date(
        parseInt(endDate.slice(0, 4)),
        parseInt(endDate.slice(4, 6)) - 1,
        parseInt(endDate.slice(6, 8))
    );

    while (current <= end) {
        dates.push(current.toISOString().slice(0, 10).replace(/-/g, ''));
        current.setDate(current.getDate() + 1);
    }

    return dates;
}