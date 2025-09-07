import { describe, test, expect } from '@jest/globals';
// Mock the ingestors for testing
const mockIngestors = {
    async ingestLufthansaCargo() {
        const hasApiKey = process.env.AEGIS_LUFTHANSA_API_KEY;
        if (hasApiKey) {
            // Simulate real API response
            return {
                mode: 'real',
                data: [
                    { route: 'FRA-NBO', cargo_capacity: 150, departure: '2025-01-15T08:00:00Z' },
                    { route: 'MUC-ELD', cargo_capacity: 120, departure: '2025-01-16T14:30:00Z' }
                ],
                source: 'lufthansa_api',
                timestamp: new Date().toISOString(),
                provenance: {
                    url: 'https://api.lufthansa.com/cargo/schedules',
                    hash: 'sha256:abc123def456'
                }
            };
        }
        else {
            // Fallback to simulation
            return {
                mode: 'sim',
                data: [
                    { route: 'SIM-FRA-NBO', cargo_capacity: 100, departure: '2025-01-15T08:00:00Z' }
                ],
                source: 'simulation',
                timestamp: new Date().toISOString()
            };
        }
    }
};
describe('Ingestor Pipeline Tests', () => {
    test('Lufthansa ingestor returns valid data structure', async () => {
        const result = await mockIngestors.ingestLufthansaCargo();
        // Validate structure
        expect(result).toHaveProperty('mode');
        expect(result).toHaveProperty('data');
        expect(result).toHaveProperty('source');
        expect(result).toHaveProperty('timestamp');
        expect(result.mode).toMatch(/^(real|sim)$/);
        expect(Array.isArray(result.data)).toBe(true);
        expect(result.data.length).toBeGreaterThan(0);
    });
    test('Real mode includes provenance data', async () => {
        // Set API key for real mode test
        process.env.AEGIS_LUFTHANSA_API_KEY = 'test_key_123';
        const result = await mockIngestors.ingestLufthansaCargo();
        expect(result.mode).toBe('real');
        expect(result).toHaveProperty('provenance');
        expect(result.provenance).toHaveProperty('url');
        expect(result.provenance).toHaveProperty('hash');
        // Clean up
        delete process.env.AEGIS_LUFTHANSA_API_KEY;
    });
    test('Sim mode fallback works without API key', async () => {
        // Ensure no API key
        delete process.env.AEGIS_LUFTHANSA_API_KEY;
        const result = await mockIngestors.ingestLufthansaCargo();
        expect(result.mode).toBe('sim');
        expect(result.source).toBe('simulation');
    });
    test('Data includes mandatory fields', async () => {
        const result = await mockIngestors.ingestLufthansaCargo();
        result.data.forEach((item) => {
            expect(item).toHaveProperty('route');
            expect(item).toHaveProperty('cargo_capacity');
            expect(item).toHaveProperty('departure');
            expect(typeof item.cargo_capacity).toBe('number');
        });
    });
});
