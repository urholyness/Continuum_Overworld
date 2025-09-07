import * as YAML from "yaml";
import fs from "node:fs/promises";
import path from "node:path";
import { runAcquire } from "./ingestors/fetch-esg-pdfs.js";
import { runParse } from "./parser/pdf-parse.js";
import { extractFor } from "./extractor/extract-kpi-context.js";
// import { callOpenAIJson } from "./extractor/llm-openai.js"; // <-- implement your real adapters
const ROOT = process.cwd();
const CFG_PATH = path.join(ROOT, "config", "providers.yaml");
async function main() {
    const t0 = Date.now();
    const cfg = YAML.parse(await fs.readFile(CFG_PATH, "utf8"));
    if (cfg.mode !== "real")
        throw new Error("Must run in REAL mode.");
    const companies = cfg.esg_docs.companies;
    const years = cfg.esg_docs.years;
    await runAcquire();
    await runParse(companies, years);
    // TODO: swap with your real consensus adapter (fanout across models)
    const llm = async ({ system, user }) => {
        throw new Error("Hook your real LLM adapters here (OpenAI/Claude/Gemini) and return JSON string.");
    };
    let kpiCount = 0, ctxCount = 0;
    for (const c of companies)
        for (const y of years) {
            const { kpis, contexts } = await extractFor(c, y, llm);
            kpiCount += kpis.length;
            ctxCount += contexts.length;
        }
    const dt = (Date.now() - t0) / 1000;
    console.log(JSON.stringify({ run_id: `real-${Date.now()}`, duration_s: dt, kpis: kpiCount, contexts: ctxCount }, null, 2));
    if (kpiCount === 0 || ctxCount === 0) {
        console.error("REAL run produced zero KPIs or zero ContextSpans — failing.");
        process.exit(1);
    }
}
main().catch(e => { console.error(e); process.exit(1); });
