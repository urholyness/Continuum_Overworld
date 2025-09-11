import fetch from 'node-fetch';

interface TestResult {
    name: string;
    passed: boolean;
    error?: string;
    response?: any;
}

class ContractTestRunner {
    private baseUrl: string;
    private adminJWT: string;
    private opsJWT: string;
    private traceJWT: string;
    private results: TestResult[] = [];

    constructor(baseUrl: string, tokens: { admin: string; ops: string; trace: string }) {
        this.baseUrl = baseUrl;
        this.adminJWT = tokens.admin;
        this.opsJWT = tokens.ops;
        this.traceJWT = tokens.trace;
    }

    private async runTest(name: string, testFn: () => Promise<void>): Promise<void> {
        console.log(`🧪 Testing: ${name}`);
        try {
            await testFn();
            this.results.push({ name, passed: true });
            console.log(`✅ PASS: ${name}`);
        } catch (error) {
            this.results.push({ 
                name, 
                passed: false, 
                error: error instanceof Error ? error.message : String(error) 
            });
            console.log(`❌ FAIL: ${name} - ${error}`);
        }
    }

    private async apiRequest(endpoint: string, options: any = {}): Promise<any> {
        const url = `${this.baseUrl}${endpoint}`;
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
        });

        const text = await response.text();
        let data;
        try {
            data = JSON.parse(text);
        } catch {
            data = text;
        }

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${text}`);
        }

        return { status: response.status, data };
    }

    async runAllTests(): Promise<void> {
        console.log(`🚀 Starting contract tests against ${this.baseUrl}\n`);

        // Health and basic connectivity tests
        await this.runTest('Health endpoint responds', async () => {
            const { status } = await this.apiRequest('/health');
            if (status !== 200) throw new Error(`Expected 200, got ${status}`);
        });

        // Composer API tests
        await this.runTest('Ops metrics endpoint (admin auth)', async () => {
            const { data } = await this.apiRequest('/composer/ops/metrics?org=org-main', {
                headers: { Authorization: `Bearer ${this.adminJWT}` }
            });
            
            if (!Array.isArray(data)) throw new Error('Response is not an array');
            if (data.length === 0) throw new Error('No metrics returned');
            
            const metric = data[0];
            const requiredFields = ['kpi', 'value', 'unit', 'ts'];
            for (const field of requiredFields) {
                if (!(field in metric)) throw new Error(`Missing required field: ${field}`);
            }
            
            if (typeof metric.value !== 'number') throw new Error('Value is not a number');
        });

        await this.runTest('Ops metrics endpoint (ops auth)', async () => {
            const { data } = await this.apiRequest('/composer/ops/metrics?org=org-main', {
                headers: { Authorization: `Bearer ${this.opsJWT}` }
            });
            
            if (!Array.isArray(data)) throw new Error('Response is not an array');
        });

        await this.runTest('Trace events endpoint (admin auth)', async () => {
            const { data } = await this.apiRequest('/composer/trace/events?org=org-main&limit=10', {
                headers: { Authorization: `Bearer ${this.adminJWT}` }
            });
            
            if (!data.items || !Array.isArray(data.items)) {
                throw new Error('Response missing items array');
            }
            
            if (data.items.length > 0) {
                const event = data.items[0];
                const requiredFields = ['id', 'ts', 'type', 'payload'];
                for (const field of requiredFields) {
                    if (!(field in event)) throw new Error(`Missing required field: ${field}`);
                }
            }
        });

        await this.runTest('Trace events endpoint (trace auth)', async () => {
            const { data } = await this.apiRequest('/composer/trace/events?org=org-main&limit=5', {
                headers: { Authorization: `Bearer ${this.traceJWT}` }
            });
            
            if (!data.items) throw new Error('Response missing items');
        });

        // Admin API tests
        await this.runTest('Farms list endpoint', async () => {
            const { data } = await this.apiRequest('/admin/farms', {
                headers: { Authorization: `Bearer ${this.adminJWT}` }
            });
            
            if (!Array.isArray(data)) throw new Error('Response is not an array');
            
            if (data.length > 0) {
                const farm = data[0];
                const requiredFields = ['id', 'name', 'region', 'hectares', 'status'];
                for (const field of requiredFields) {
                    if (!(field in farm)) throw new Error(`Missing required field: ${field}`);
                }
                
                if (typeof farm.hectares !== 'number') throw new Error('Hectares is not a number');
                if (!['active', 'paused'].includes(farm.status)) {
                    throw new Error(`Invalid status: ${farm.status}`);
                }
            }
        });

        await this.runTest('Farm creation endpoint', async () => {
            const testFarm = {
                id: `TEST_${Date.now()}`,
                name: 'Contract Test Farm',
                region: 'Test Region',
                hectares: 1.5,
                status: 'active'
            };

            const { data } = await this.apiRequest('/admin/farms', {
                method: 'POST',
                headers: { Authorization: `Bearer ${this.adminJWT}` },
                body: JSON.stringify(testFarm)
            });
            
            if (data.id !== testFarm.id) throw new Error('Created farm ID mismatch');
            if (data.name !== testFarm.name) throw new Error('Created farm name mismatch');
        });

        await this.runTest('Agents list endpoint', async () => {
            const { data } = await this.apiRequest('/admin/agents', {
                headers: { Authorization: `Bearer ${this.adminJWT}` }
            });
            
            if (!Array.isArray(data)) throw new Error('Response is not an array');
            
            if (data.length > 0) {
                const agent = data[0];
                const requiredFields = ['id', 'name', 'role', 'tier', 'status'];
                for (const field of requiredFields) {
                    if (!(field in agent)) throw new Error(`Missing required field: ${field}`);
                }
                
                if (!['online', 'degraded', 'offline'].includes(agent.status)) {
                    throw new Error(`Invalid agent status: ${agent.status}`);
                }
            }
        });

        // Public API tests
        await this.runTest('Public highlights endpoint', async () => {
            const { data } = await this.apiRequest('/public/trace/highlights');
            
            if (!data.items || !Array.isArray(data.items)) {
                throw new Error('Response missing items array');
            }
            
            if (!data.note || !data.note.includes('anonymized')) {
                throw new Error('Missing anonymization notice');
            }
            
            if (data.items.length > 0) {
                const highlight = data.items[0];
                const requiredFields = ['id', 'timestamp', 'type', 'summary'];
                for (const field of requiredFields) {
                    if (!(field in highlight)) throw new Error(`Missing required field: ${field}`);
                }
            }
        });

        // Authorization tests
        await this.runTest('Ops user denied admin access', async () => {
            try {
                await this.apiRequest('/admin/farms', {
                    headers: { Authorization: `Bearer ${this.opsJWT}` }
                });
                throw new Error('Expected 403 but request succeeded');
            } catch (error) {
                if (!error.message.includes('403')) {
                    throw new Error(`Expected 403, got: ${error.message}`);
                }
            }
        });

        await this.runTest('Trace user denied admin access', async () => {
            try {
                await this.apiRequest('/admin/agents', {
                    headers: { Authorization: `Bearer ${this.traceJWT}` }
                });
                throw new Error('Expected 403 but request succeeded');
            } catch (error) {
                if (!error.message.includes('403')) {
                    throw new Error(`Expected 403, got: ${error.message}`);
                }
            }
        });

        await this.runTest('Unauthenticated access denied', async () => {
            try {
                await this.apiRequest('/admin/farms');
                throw new Error('Expected 401 but request succeeded');
            } catch (error) {
                if (!error.message.includes('401')) {
                    throw new Error(`Expected 401, got: ${error.message}`);
                }
            }
        });

        // Error handling tests
        await this.runTest('Invalid endpoint returns 404', async () => {
            try {
                await this.apiRequest('/invalid/endpoint');
                throw new Error('Expected 404 but request succeeded');
            } catch (error) {
                if (!error.message.includes('404')) {
                    throw new Error(`Expected 404, got: ${error.message}`);
                }
            }
        });

        await this.runTest('Malformed JSON returns 400', async () => {
            try {
                await this.apiRequest('/admin/farms', {
                    method: 'POST',
                    headers: { 
                        Authorization: `Bearer ${this.adminJWT}`,
                        'Content-Type': 'application/json'
                    },
                    body: '{invalid json}'
                });
                throw new Error('Expected 400 but request succeeded');
            } catch (error) {
                if (!error.message.includes('400')) {
                    throw new Error(`Expected 400, got: ${error.message}`);
                }
            }
        });

        this.printSummary();
    }

    private printSummary(): void {
        const passed = this.results.filter(r => r.passed).length;
        const total = this.results.length;
        
        console.log('\n📊 CONTRACT TEST SUMMARY');
        console.log('========================');
        console.log(`Total tests: ${total}`);
        console.log(`Passed: ${passed}`);
        console.log(`Failed: ${total - passed}`);
        
        if (passed === total) {
            console.log('\n🎉 ALL CONTRACT TESTS PASSED!');
        } else {
            console.log('\n❌ SOME CONTRACT TESTS FAILED:');
            this.results.filter(r => !r.passed).forEach(result => {
                console.log(`  - ${result.name}: ${result.error}`);
            });
        }
    }

    getResults(): TestResult[] {
        return this.results;
    }
}

// Main execution
async function main() {
    const environment = process.env.ENVIRONMENT || 'dev';
    const rootDomain = process.env.ROOT_DOMAIN || 'greenstemglobal.com';
    const baseUrl = process.env.API_BASE_URL || `https://cn-${environment}-api.${rootDomain}`;
    
    const tokens = {
        admin: process.env.ADMIN_JWT || '',
        ops: process.env.OPS_JWT || '',
        trace: process.env.TRACE_JWT || ''
    };

    if (!tokens.admin || !tokens.ops || !tokens.trace) {
        console.error('❌ Missing required JWT tokens. Please set:');
        console.error('  ADMIN_JWT, OPS_JWT, TRACE_JWT environment variables');
        process.exit(1);
    }

    const runner = new ContractTestRunner(baseUrl, tokens);
    await runner.runAllTests();
    
    const results = runner.getResults();
    const allPassed = results.every(r => r.passed);
    
    process.exit(allPassed ? 0 : 1);
}

if (require.main === module) {
    main().catch(error => {
        console.error('Contract test runner error:', error);
        process.exit(1);
    });
}

export { ContractTestRunner };