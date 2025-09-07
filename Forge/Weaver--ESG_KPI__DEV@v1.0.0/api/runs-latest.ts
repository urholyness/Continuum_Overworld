import fs from "node:fs/promises";
import path from "node:path";

const ROOT = process.cwd();
const DATA = path.join(ROOT, "data");

export async function runsLatest(companies: string[], year: number) {
  const KPIs = [];
  const ContextSpans = [];
  const Sources = [];

  for (const c of companies) {
    const kPath = path.join(DATA, "out", c, `${year}--kpis.json`);
    const cPath = path.join(DATA, "out", c, `${year}--context.json`);
    try {
      const k = JSON.parse(await fs.readFile(kPath, "utf8"));
      const ctx = JSON.parse(await fs.readFile(cPath, "utf8"));
      KPIs.push(...k); ContextSpans.push(...ctx);
      const meta = JSON.parse(await fs.readFile(path.join(DATA, "meta", c, `${year}.json`), "utf8"));
      Sources.push({ company: c, year, ...meta });
    } catch { /* missing is ok; continue */ }
  }

  const RunSummary = {
    run_id: `real-${Date.now()}`,
    started_at: new Date().toISOString(),
    duration_s: 0, // fill in from orchestrator
    cost_eur: 0,
    changed_kpis: KPIs.length,
    changed_contexts: ContextSpans.length
  };

  return { RunSummary, KPIs, ContextSpans, Sources };
}