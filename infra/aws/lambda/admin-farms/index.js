const { DynamoDBClient } = require('@aws-sdk/client-dynamodb');
const { DynamoDBDocumentClient, QueryCommand, PutCommand, BatchWriteCommand } = require('@aws-sdk/lib-dynamodb');

const dynamodb = DynamoDBDocumentClient.from(new DynamoDBClient({}));

exports.handler = async (event) => {
    console.log('Event:', JSON.stringify(event, null, 2));
    
    try {
        // Validate JWT claims - admin required
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

        const method = event.requestContext?.http?.method || event.httpMethod;
        const path = event.requestContext?.http?.path || event.path;

        if (method === 'GET') {
            return await handleGetFarms(event);
        } else if (method === 'POST' && path.includes(':batch')) {
            return await handleBatchUpsertFarms(event);
        } else if (method === 'POST') {
            return await handleUpsertFarm(event);
        } else {
            return {
                statusCode: 405,
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                body: JSON.stringify({
                    error: 'METHOD_NOT_ALLOWED',
                    message: 'Method not allowed'
                })
            };
        }

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

async function handleGetFarms(event) {
    const queryParams = event.queryStringParameters || {};
    const org = queryParams.org || process.env.TENANT_ID || 'org-main';
    const status = queryParams.status;
    const region = queryParams.region;

    const params = {
        TableName: process.env.FARMS_TABLE,
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
    if (region) {
        filterExpressions.push('region = :region');
        params.ExpressionAttributeValues[':region'] = region;
    }
    
    if (filterExpressions.length > 0) {
        params.FilterExpression = filterExpressions.join(' AND ');
    }

    const result = await dynamodb.send(new QueryCommand(params));

    const farms = (result.Items || []).map(item => ({
        id: item.id,
        name: item.name,
        region: item.region || 'Unknown',
        hectares: parseFloat(item.hectares) || 0,
        status: item.status || 'active',
        ...(item.geometry && { geometry: item.geometry }),
        ...(item.metadata && { metadata: item.metadata }),
        ...(item.createdAt && { createdAt: item.createdAt }),
        ...(item.updatedAt && { updatedAt: item.updatedAt })
    }));

    console.log(`Retrieved ${farms.length} farms for org: ${org}`);

    return {
        statusCode: 200,
        headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Cache-Control': 'public, max-age=120' // 2 minute cache
        },
        body: JSON.stringify(farms)
    };
}

async function handleUpsertFarm(event) {
    const body = JSON.parse(event.body || '{}');
    const org = process.env.TENANT_ID || 'org-main';
    
    // Validate required fields
    if (!body.id || !body.name) {
        return {
            statusCode: 400,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            body: JSON.stringify({
                error: 'VALIDATION_ERROR',
                message: 'id and name are required fields',
                validationErrors: [
                    ...(body.id ? [] : [{ field: 'id', message: 'Required field', code: 'REQUIRED' }]),
                    ...(body.name ? [] : [{ field: 'name', message: 'Required field', code: 'REQUIRED' }])
                ]
            })
        };
    }

    const now = new Date().toISOString();
    const farmData = {
        PK: `org#${org}`,
        SK: `farm#${body.id}`,
        id: body.id,
        name: body.name,
        region: body.region || 'Unknown',
        hectares: parseFloat(body.hectares) || 1.0,
        status: body.status || 'active',
        updatedAt: now,
        ...(body.geometry && { geometry: body.geometry }),
        ...(body.metadata && { metadata: body.metadata })
    };

    // Add createdAt only for new records
    try {
        const existingResult = await dynamodb.send(new QueryCommand({
            TableName: process.env.FARMS_TABLE,
            KeyConditionExpression: 'PK = :pk AND SK = :sk',
            ExpressionAttributeValues: {
                ':pk': farmData.PK,
                ':sk': farmData.SK
            }
        }));

        if (!existingResult.Items || existingResult.Items.length === 0) {
            farmData.createdAt = now;
        }
    } catch (error) {
        console.warn('Could not check existing farm, assuming new:', error);
        farmData.createdAt = now;
    }

    await dynamodb.send(new PutCommand({
        TableName: process.env.FARMS_TABLE,
        Item: farmData
    }));

    const responseFarm = {
        id: farmData.id,
        name: farmData.name,
        region: farmData.region,
        hectares: farmData.hectares,
        status: farmData.status,
        ...(farmData.geometry && { geometry: farmData.geometry }),
        ...(farmData.metadata && { metadata: farmData.metadata }),
        ...(farmData.createdAt && { createdAt: farmData.createdAt }),
        updatedAt: farmData.updatedAt
    };

    console.log(`Upserted farm: ${farmData.id} for org: ${org}`);

    return {
        statusCode: 201,
        headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        body: JSON.stringify(responseFarm)
    };
}

async function handleBatchUpsertFarms(event) {
    const body = JSON.parse(event.body || '{}');
    const farms = body.farms || [];
    const org = process.env.TENANT_ID || 'org-main';

    if (!Array.isArray(farms) || farms.length === 0) {
        return {
            statusCode: 400,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            body: JSON.stringify({
                error: 'VALIDATION_ERROR',
                message: 'farms array is required and cannot be empty'
            })
        };
    }

    if (farms.length > 100) {
        return {
            statusCode: 413,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            body: JSON.stringify({
                error: 'PAYLOAD_TOO_LARGE',
                message: 'Maximum 100 farms per batch request'
            })
        };
    }

    const results = [];
    const now = new Date().toISOString();
    
    // Process farms in batches of 25 (DynamoDB BatchWrite limit)
    for (let i = 0; i < farms.length; i += 25) {
        const batch = farms.slice(i, i + 25);
        const writeRequests = [];

        for (const farm of batch) {
            try {
                if (!farm.id || !farm.name) {
                    results.push({
                        id: farm.id || 'unknown',
                        status: 'error',
                        error: 'id and name are required fields'
                    });
                    continue;
                }

                const farmData = {
                    PK: `org#${org}`,
                    SK: `farm#${farm.id}`,
                    id: farm.id,
                    name: farm.name,
                    region: farm.region || 'Unknown',
                    hectares: parseFloat(farm.hectares) || 1.0,
                    status: farm.status || 'active',
                    createdAt: now,
                    updatedAt: now,
                    ...(farm.geometry && { geometry: farm.geometry }),
                    ...(farm.metadata && { metadata: farm.metadata })
                };

                writeRequests.push({
                    PutRequest: {
                        Item: farmData
                    }
                });

                results.push({
                    id: farm.id,
                    status: 'created', // Simplified - treating all as creates in batch
                    farm: {
                        id: farmData.id,
                        name: farmData.name,
                        region: farmData.region,
                        hectares: farmData.hectares,
                        status: farmData.status,
                        ...(farmData.geometry && { geometry: farmData.geometry }),
                        createdAt: farmData.createdAt,
                        updatedAt: farmData.updatedAt
                    }
                });

            } catch (error) {
                results.push({
                    id: farm.id || 'unknown',
                    status: 'error',
                    error: error.message
                });
            }
        }

        if (writeRequests.length > 0) {
            try {
                await dynamodb.send(new BatchWriteCommand({
                    RequestItems: {
                        [process.env.FARMS_TABLE]: writeRequests
                    }
                }));
            } catch (error) {
                console.error('Batch write error:', error);
                // Mark all items in this batch as error
                for (const request of writeRequests) {
                    const farmId = request.PutRequest.Item.id;
                    const resultIndex = results.findIndex(r => r.id === farmId && r.status === 'created');
                    if (resultIndex >= 0) {
                        results[resultIndex].status = 'error';
                        results[resultIndex].error = 'Database write failed';
                        delete results[resultIndex].farm;
                    }
                }
            }
        }
    }

    const successCount = results.filter(r => r.status !== 'error').length;
    const errorCount = results.filter(r => r.status === 'error').length;

    console.log(`Batch upsert completed: ${successCount} success, ${errorCount} errors`);

    return {
        statusCode: 201,
        headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        body: JSON.stringify({
            results,
            successCount,
            errorCount
        })
    };
}