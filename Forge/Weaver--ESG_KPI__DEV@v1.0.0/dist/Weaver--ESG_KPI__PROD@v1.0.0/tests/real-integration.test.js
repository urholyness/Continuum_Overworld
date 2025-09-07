import fs from "node:fs/promises";
import path from "node:path";
import { loadProviders } from "../ingestors/fetch-esg-pdfs.js";
import { runsLatest } from "../api/runs-latest.js";
test("REAL mode enforced in providers.yaml", async () => {
    const config = await loadProviders();
    expect(config.mode).toBe("real");
    expect(config.esg_docs.companies.length).toBeGreaterThan(0);
    expect(config.esg_docs.years.length).toBeGreaterThan(0);
});
test("meta JSONs include source_url and sha256", async () => {
    const metaRoot = path.join(process.cwd(), "data", "meta");
    const companies = await fs.readdir(metaRoot).catch(() => []);
    if (companies.length === 0)
        return; // Skip if no data yet
    for (const company of companies) {
        const companyDir = path.join(metaRoot, company);
        const files = await fs.readdir(companyDir).catch(() => []);
        for (const file of files.filter(f => f.endsWith('.json'))) {
            const metaPath = path.join(companyDir, file);
            const meta = JSON.parse(await fs.readFile(metaPath, "utf8"));
            expect(meta).toHaveProperty("source_url");
            expect(meta).toHaveProperty("sha256");
            expect(meta).toHaveProperty("downloaded_at");
            expect(meta).toHaveProperty("content_length");
            expect(meta).toHaveProperty("content_type");
            expect(typeof meta.source_url).toBe("string");
            expect(typeof meta.sha256).toBe("string");
            expect(meta.source_url).toMatch(/^https?:\/\//);
            expect(meta.sha256).toMatch(/^[a-f0-9]{64}$/);
        }
    }
});
test("KPI output includes mandatory provenance fields", async () => {
    const outRoot = path.join(process.cwd(), "data", "out");
    const companies = await fs.readdir(outRoot).catch(() => []);
    if (companies.length === 0)
        return; // Skip if no extraction yet
    for (const company of companies) {
        const companyDir = path.join(outRoot, company);
        const files = await fs.readdir(companyDir).catch(() => []);
        const kpiFile = files.find(f => f.endsWith('--kpis.json'));
        if (kpiFile) {
            const kpiPath = path.join(companyDir, kpiFile);
            const kpis = JSON.parse(await fs.readFile(kpiPath, "utf8"));
            for (const kpi of kpis) {
                expect(kpi).toHaveProperty("company_name");
                expect(kpi).toHaveProperty("year");
                expect(kpi).toHaveProperty("kpi_id");
                expect(kpi).toHaveProperty("value");
                expect(kpi).toHaveProperty("unit");
                expect(kpi).toHaveProperty("confidence");
                expect(kpi).toHaveProperty("source_url");
                expect(kpi).toHaveProperty("source_hash");
                expect(kpi).toHaveProperty("page_refs");
                expect(typeof kpi.confidence).toBe("number");
                expect(kpi.confidence).toBeGreaterThanOrEqual(0);
                expect(kpi.confidence).toBeLessThanOrEqual(1);
                expect(Array.isArray(kpi.page_refs)).toBe(true);
            }
        }
    }
});
test("runs-latest API returns proper structure", async () => {
    const config = await loadProviders();
    const result = await runsLatest(config.esg_docs.companies, 2023);
    expect(result).toHaveProperty("RunSummary");
    expect(result).toHaveProperty("KPIs");
    expect(result).toHaveProperty("ContextSpans");
    expect(result).toHaveProperty("Sources");
    expect(Array.isArray(result.KPIs)).toBe(true);
    expect(Array.isArray(result.ContextSpans)).toBe(true);
    expect(Array.isArray(result.Sources)).toBe(true);
    expect(result.RunSummary).toHaveProperty("run_id");
    expect(result.RunSummary).toHaveProperty("changed_kpis");
    expect(result.RunSummary).toHaveProperty("changed_contexts");
});
