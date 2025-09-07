import * as YAML from "yaml";
import fs from "node:fs/promises";
import path from "node:path";
import { runAcquire } from "./ingestors/fetch-esg-pdfs.js";
import { runParse } from "./parser/pdf-parse.js";
import { extractFor } from "./extractor/extract-kpi-context.js";
import { callConsensus } from "./extractor/llm-consensus.js";

const ROOT = process.cwd();
const CFG_PATH = path.join(ROOT, "config", "providers.yaml");
const AUDIT_LOG = path.join(ROOT, "Aegis", "Audit", "decision-packets.jsonl");

async function emitDecisionPacket(data: any) {
  await fs.mkdir(path.dirname(AUDIT_LOG), { recursive: true });
  const packet = JSON.stringify(data);
  await fs.appendFile(AUDIT_LOG, packet + "\n");
}

async function main() {
  const t0 = Date.now();
  const cfg = YAML.parse(await fs.readFile(CFG_PATH, "utf8")) as { mode: string; esg_docs: { companies: string[]; years: number[] } };
  if (cfg.mode !== "real") throw new Error("Must run in REAL mode.");
  const companies = cfg.esg_docs.companies;
  const years = cfg.esg_docs.years;

  console.log(`[run-real] Starting REAL extraction for ${companies.length} companies, ${years.length} years`);
  console.log(`[run-real] Companies: ${companies.join(", ")}`);
  console.log(`[run-real] Years: ${years.join(", ")}`);

  // Phase 1: Acquire PDFs from official sources
  console.log("\n=== Phase 1: Acquiring PDFs ===");
  await runAcquire();

  // Phase 2: Parse PDFs to JSONL
  console.log("\n=== Phase 2: Parsing PDFs ===");
  await runParse(companies, years);

  // Phase 3: Extract KPIs and Context using real LLMs with consensus
  console.log("\n=== Phase 3: Extracting KPIs & Context ===");
  let kpiCount = 0, ctxCount = 0;
  for (const c of companies) {
    for (const y of years) {
      console.log(`[extract] ${c} ${y}`);
      try {
        const { kpis, contexts } = await extractFor(c, y, callConsensus);
        kpiCount += kpis.length; 
        ctxCount += contexts.length;
        console.log(`  → ${kpis.length} KPIs, ${contexts.length} contexts`);

        // Emit decision packet
        await emitDecisionPacket({
          actor: "Weaver__ESG_KPI",
          intent: "extract_esg_data",
          company: c,
          year: y,
          status: "completed",
          kpis: kpis.length,
          contexts: contexts.length,
          provenance: { sha256: kpis[0]?.source_hash || "none" },
          pages: kpis.reduce((sum, k) => sum + (k.page_refs?.length || 0), 0),
          ts: new Date().toISOString()
        });
      } catch (error) {
        console.error(`[extract] Failed for ${c} ${y}:`, error);
        await emitDecisionPacket({
          actor: "Weaver__ESG_KPI",
          intent: "extract_esg_data",
          company: c,
          year: y,
          status: "failed",
          error: String(error),
          ts: new Date().toISOString()
        });
      }
    }
  }

  const dt = (Date.now() - t0) / 1000;
  const summary = { 
    run_id: `real-${Date.now()}`, 
    duration_s: dt, 
    kpis: kpiCount, 
    contexts: ctxCount,
    companies_processed: companies.length,
    years_processed: years.length
  };

  console.log("\n=== Extraction Complete ===");
  console.log(JSON.stringify(summary, null, 2));

  // Validation: Fail if no KPIs or contexts extracted
  if (kpiCount === 0 || ctxCount === 0) {
    console.error(`\n❌ REAL run validation FAILED:`);
    console.error(`   KPIs extracted: ${kpiCount}`);
    console.error(`   Contexts extracted: ${ctxCount}`);
    console.error(`   Both must be > 0 for successful extraction`);
    process.exit(1);
  }

  console.log(`\n✅ REAL extraction successful:`);
  console.log(`   KPIs extracted: ${kpiCount}`);
  console.log(`   Contexts extracted: ${ctxCount}`);
  console.log(`   Duration: ${dt.toFixed(1)}s`);

  // Write final summary
  const summaryPath = path.join(ROOT, "data", "run-summary.json");
  await fs.mkdir(path.dirname(summaryPath), { recursive: true });
  await fs.writeFile(summaryPath, JSON.stringify(summary, null, 2));
  console.log(`\n📊 Summary written to: ${summaryPath}`);
}

main().catch(e => { 
  console.error("\n❌ REAL extraction failed:", e); 
  process.exit(1); 
});