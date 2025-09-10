const { DynamoDBClient } = require('@aws-sdk/client-dynamodb');
const { DynamoDBDocumentClient, ScanCommand, PutCommand, BatchWriteCommand } = require('@aws-sdk/lib-dynamodb');

const dynamodb = DynamoDBDocumentClient.from(new DynamoDBClient({}));

exports.handler = async (event) => {
    console.log('Oracle Metrics Aggregator started:', JSON.stringify(event, null, 2));
    
    try {
        const org = process.env.TENANT_ID || 'org-main';
        const now = new Date();
        const date = now.toISOString().slice(0, 10).replace(/-/g, '');
        const timestamp = now.toISOString();

        // Read from Oracle tables and compute KPIs
        const metrics = [];

        // 1. Satellite Data Metrics
        try {
            const satelliteMetrics = await computeSatelliteMetrics(org);
            metrics.push(...satelliteMetrics);
        } catch (error) {
            console.error('Error computing satellite metrics:', error);
        }

        // 2. Weather Data Metrics  
        try {
            const weatherMetrics = await computeWeatherMetrics(org);
            metrics.push(...weatherMetrics);
        } catch (error) {
            console.error('Error computing weather metrics:', error);
        }

        // 3. Operational Metrics (synthetic for demo)
        const operationalMetrics = generateOperationalMetrics();
        metrics.push(...operationalMetrics);

        // Write metrics to the Metrics table
        if (metrics.length > 0) {
            await writeMetricsToTable(org, date, timestamp, metrics);
            console.log(`Successfully aggregated and stored ${metrics.length} metrics`);
        } else {
            console.log('No metrics to aggregate');
        }

        return {
            statusCode: 200,
            body: JSON.stringify({
                message: 'Metrics aggregation completed',
                metricsProcessed: metrics.length,
                timestamp: timestamp
            })
        };

    } catch (error) {
        console.error('Aggregation error:', error);
        
        // Don't throw - let Lambda handle the retry
        return {
            statusCode: 500,
            body: JSON.stringify({
                error: 'AGGREGATION_ERROR',
                message: error.message,
                timestamp: new Date().toISOString()
            })
        };
    }
};

async function computeSatelliteMetrics(org) {
    const metrics = [];
    
    try {
        // Try to read from satellite data table
        const satelliteTableName = `C_N-Oracle-SatelliteData-${process.env.ENVIRONMENT || 'dev'}`;
        
        const params = {
            TableName: satelliteTableName,
            FilterExpression: 'attribute_exists(ndvi) OR attribute_exists(ndwi)',
            Limit: 100 // Process recent entries only
        };

        const result = await dynamodb.send(new ScanCommand(params));
        const items = result.Items || [];

        if (items.length > 0) {
            // Compute average NDVI
            const ndviValues = items.filter(item => item.ndvi).map(item => parseFloat(item.ndvi));
            if (ndviValues.length > 0) {
                const avgNdvi = ndviValues.reduce((sum, val) => sum + val, 0) / ndviValues.length;
                metrics.push({
                    kpi: 'avg_ndvi',
                    value: Math.round(avgNdvi * 1000) / 1000,
                    unit: 'index'
                });
            }

            // Compute average NDWI
            const ndwiValues = items.filter(item => item.ndwi).map(item => parseFloat(item.ndwi));
            if (ndwiValues.length > 0) {
                const avgNdwi = ndwiValues.reduce((sum, val) => sum + val, 0) / ndwiValues.length;
                metrics.push({
                    kpi: 'avg_ndwi',
                    value: Math.round(avgNdwi * 1000) / 1000,
                    unit: 'index'
                });
            }

            // Health score based on NDVI
            if (ndviValues.length > 0) {
                const healthyPixels = ndviValues.filter(val => val > 0.6).length;
                const healthPercentage = (healthyPixels / ndviValues.length) * 100;
                metrics.push({
                    kpi: 'vegetation_health_pct',
                    value: Math.round(healthPercentage * 10) / 10,
                    unit: '%'
                });
            }
        }

    } catch (error) {
        console.log('Satellite data table not available, using synthetic data:', error.message);
        
        // Generate synthetic satellite metrics for demo
        metrics.push({
            kpi: 'avg_ndvi',
            value: Math.round((0.6 + Math.random() * 0.3) * 1000) / 1000,
            unit: 'index'
        });
        
        metrics.push({
            kpi: 'avg_ndwi',
            value: Math.round((0.2 + Math.random() * 0.2) * 1000) / 1000,
            unit: 'index'
        });
        
        metrics.push({
            kpi: 'vegetation_health_pct',
            value: Math.round((75 + Math.random() * 20) * 10) / 10,
            unit: '%'
        });
    }

    return metrics;
}

async function computeWeatherMetrics(org) {
    const metrics = [];
    
    try {
        // Try to read from weather data table
        const weatherTableName = `C_N-Oracle-WeatherData-${process.env.ENVIRONMENT || 'dev'}`;
        
        const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
        
        const params = {
            TableName: weatherTableName,
            FilterExpression: '#ts >= :oneDayAgo AND (attribute_exists(rainfall) OR attribute_exists(temperature))',
            ExpressionAttributeNames: {
                '#ts': 'timestamp'
            },
            ExpressionAttributeValues: {
                ':oneDayAgo': oneDayAgo
            },
            Limit: 100
        };

        const result = await dynamodb.send(new ScanCommand(params));
        const items = result.Items || [];

        if (items.length > 0) {
            // Compute 24h rainfall
            const rainfallValues = items.filter(item => item.rainfall).map(item => parseFloat(item.rainfall));
            if (rainfallValues.length > 0) {
                const totalRainfall = rainfallValues.reduce((sum, val) => sum + val, 0);
                metrics.push({
                    kpi: 'rainfall_mm_24h',
                    value: Math.round(totalRainfall * 10) / 10,
                    unit: 'mm'
                });
            }

            // Compute average temperature
            const tempValues = items.filter(item => item.temperature).map(item => parseFloat(item.temperature));
            if (tempValues.length > 0) {
                const avgTemp = tempValues.reduce((sum, val) => sum + val, 0) / tempValues.length;
                metrics.push({
                    kpi: 'avg_temp_24h',
                    value: Math.round(avgTemp * 10) / 10,
                    unit: '°C'
                });
            }
        }

    } catch (error) {
        console.log('Weather data table not available, using synthetic data:', error.message);
        
        // Generate synthetic weather metrics for demo
        metrics.push({
            kpi: 'rainfall_mm_24h',
            value: Math.round(Math.random() * 15 * 10) / 10,
            unit: 'mm'
        });
        
        metrics.push({
            kpi: 'avg_temp_24h',
            value: Math.round((20 + Math.random() * 10) * 10) / 10,
            unit: '°C'
        });
    }

    return metrics;
}

function generateOperationalMetrics() {
    const baseMetrics = [
        {
            kpi: 'throughput_tph',
            value: Math.round((1.5 + Math.random() * 0.8) * 10) / 10,
            unit: 't/h'
        },
        {
            kpi: 'orders_open',
            value: Math.floor(8 + Math.random() * 12),
            unit: 'count'
        },
        {
            kpi: 'temp_packhouse',
            value: Math.round((4 + Math.random() * 4) * 10) / 10,
            unit: '°C'
        },
        {
            kpi: 'lots_processed_24h',
            value: Math.floor(15 + Math.random() * 25),
            unit: 'count'
        },
        {
            kpi: 'quality_pass_rate',
            value: Math.round((85 + Math.random() * 12) * 10) / 10,
            unit: '%'
        }
    ];

    return baseMetrics;
}

async function writeMetricsToTable(org, date, timestamp, metrics) {
    const writeRequests = [];
    
    for (const metric of metrics) {
        const PK = `org#${org}#date#${date}`;
        const SK = `kpi#${metric.kpi}#ts#${timestamp}`;
        
        const item = {
            PK,
            SK,
            kpi: metric.kpi,
            value: metric.value,
            unit: metric.unit,
            ts: timestamp,
            computedAt: timestamp
        };

        writeRequests.push({
            PutRequest: {
                Item: item
            }
        });
    }

    // Write metrics in batches of 25
    for (let i = 0; i < writeRequests.length; i += 25) {
        const batch = writeRequests.slice(i, i + 25);
        
        await dynamodb.send(new BatchWriteCommand({
            RequestItems: {
                [process.env.METRICS_TABLE]: batch
            }
        }));
    }

    console.log(`Wrote ${metrics.length} metrics to ${process.env.METRICS_TABLE}`);
}