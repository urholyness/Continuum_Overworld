import { describe, test, expect, beforeEach, afterEach } from '@jest/globals';
import fs from 'node:fs/promises';
import path from 'node:path';
import { ingestLufthansaCargo } from '../../../Forge/Ingestor--Cargo__Lufthansa@v0.1.0.js';
import { exportToExcel } from '../api/export-excel.js';
describe('Lufthansa Query → Excel Pipeline', () => {
    let testOutputDir;
    beforeEach(async () => {
        testOutputDir = `/tmp/weaver_test_${Date.now()}`;
        await fs.mkdir(testOutputDir, { recursive: true });
    });
    afterEach(async () => {
        try {
            await fs.rm(testOutputDir, { recursive: true, force: true });
        }
        catch (e) {
            // Ignore cleanup errors
        }
    });
    test('Complete pipeline: Lufthansa ingest → Excel export (sim mode)', async () => {
        // Ensure sim mode (no API key)
        delete process.env.AEGIS_LUFTHANSA_API_KEY;
        // Step 1: Ingest data
        const ingestResult = await ingestLufthansaCargo();
        expect(ingestResult.mode).toBe('sim');
        expect(ingestResult.data.length).toBeGreaterThan(0);
        expect(ingestResult).toHaveProperty('timestamp');
        // Step 2: Prepare export data
        const exportData = {
            run_id: `test_${Date.now()}`,
            timestamp: ingestResult.timestamp,
            mode: ingestResult.mode,
            data: ingestResult.data,
            ...(ingestResult.provenance && { provenance: ingestResult.provenance })
        };
        // Step 3: Export to Excel
        const outputPath = path.join(testOutputDir, 'lufthansa_test.xlsx');
        const exportedFile = await exportToExcel(exportData, outputPath);
        // Step 4: Verify Excel file was created
        expect(exportedFile).toBe(outputPath);
        const fileStats = await fs.stat(exportedFile);
        expect(fileStats.isFile()).toBe(true);
        expect(fileStats.size).toBeGreaterThan(0);
    });
    test('Complete pipeline: Lufthansa ingest → Excel export (real mode)', async () => {
        // Set API key for real mode
        process.env.AEGIS_LUFTHANSA_API_KEY = 'test_key_for_jest';
        // Step 1: Ingest data
        const ingestResult = await ingestLufthansaCargo();
        expect(ingestResult.mode).toBe('real');
        expect(ingestResult.data.length).toBeGreaterThan(0);
        expect(ingestResult).toHaveProperty('provenance');
        expect(ingestResult.provenance).toHaveProperty('url');
        expect(ingestResult.provenance).toHaveProperty('hash');
        // Step 2: Prepare export data
        const exportData = {
            run_id: `real_test_${Date.now()}`,
            timestamp: ingestResult.timestamp,
            mode: ingestResult.mode,
            data: ingestResult.data,
            provenance: ingestResult.provenance
        };
        // Step 3: Export to Excel
        const outputPath = path.join(testOutputDir, 'lufthansa_real_test.xlsx');
        const exportedFile = await exportToExcel(exportData, outputPath);
        // Step 4: Verify Excel file and provenance
        expect(exportedFile).toBe(outputPath);
        const fileStats = await fs.stat(exportedFile);
        expect(fileStats.isFile()).toBe(true);
        expect(fileStats.size).toBeGreaterThan(0);
        // Clean up environment
        delete process.env.AEGIS_LUFTHANSA_API_KEY;
    });
    test('Data validation: mandatory fields present', async () => {
        const ingestResult = await ingestLufthansaCargo();
        // Validate each data record has required fields
        ingestResult.data.forEach((record) => {
            expect(record).toHaveProperty('route');
            expect(record).toHaveProperty('cargo_capacity_tons');
            expect(record).toHaveProperty('departure');
            expect(record).toHaveProperty('arrival');
            expect(record).toHaveProperty('aircraft_type');
            expect(record).toHaveProperty('cargo_available');
            // Type validation
            expect(typeof record.cargo_capacity_tons).toBe('number');
            expect(typeof record.cargo_available).toBe('number');
            expect(typeof record.route).toBe('string');
        });
    });
    test('Provenance auditing: hash uniqueness', async () => {
        // Set API key for real mode
        process.env.AEGIS_LUFTHANSA_API_KEY = 'test_audit_key';
        const result1 = await ingestLufthansaCargo();
        // Wait a bit to ensure different timestamp
        await new Promise(resolve => setTimeout(resolve, 10));
        const result2 = await ingestLufthansaCargo();
        // Different timestamps should produce different hashes
        expect(result1.provenance?.hash).not.toBe(result2.provenance?.hash);
        expect(result1.timestamp).not.toBe(result2.timestamp);
        // Clean up
        delete process.env.AEGIS_LUFTHANSA_API_KEY;
    });
});
