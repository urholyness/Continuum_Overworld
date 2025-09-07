import fs from "node:fs/promises";
import path from "node:path";
const ROOT = process.cwd();
const DATA = path.join(ROOT, "data");
const SYSTEM_PROMPT = `You extract ESG KPIs and their context from page-segmented report text. 
Return strict JSON with two arrays: kpis[], contexts[].
- kpi_id are canonical (e.g., "tCO2e_Scope1", "SAF_%", "Offsets_t")
- Include unit and value; if value is a %, use "percent" or "%" accordingly.
- confidence is 0..1 from your self-estimate based on clarity and numeric certainty.
- contexts contain verbatim snippets (<= 500 chars), and classification ∈ {plan, pledge, progress, pr}.`;
function buildUserPrompt(company, year, pageText) {
    return `Company: ${company}\nYear: ${year}\nText:\n"""${pageText.substring(0, 5000)}"""\n\nExtract KPIs & Context now as JSON.`;
}
export async function extractFor(company, year, llm) {
    const parsedPath = path.join(DATA, "parsed", company, `${year}.jsonl`);
    const metaPath = path.join(DATA, "meta", company, `${year}.json`);
    const meta = JSON.parse(await fs.readFile(metaPath, "utf8"));
    const lines = (await fs.readFile(parsedPath, "utf8")).split("\n").filter(Boolean);
    const kpis = [];
    const contexts = [];
    for (const line of lines) {
        const { page, text } = JSON.parse(line);
        const user = buildUserPrompt(company, year, text);
        const raw = await llm({ system: SYSTEM_PROMPT, user });
        // Expect the model to output JSON; be defensive
        try {
            const parsed = JSON.parse(raw);
            for (const k of (parsed.kpis || [])) {
                if (!k.unit)
                    continue;
                k.company_name = company;
                k.year = year;
                k.source_url = meta.source_url;
                k.source_hash = meta.sha256;
                if (!k.page_refs)
                    k.page_refs = [page];
                kpis.push(k);
            }
            for (const c of (parsed.contexts || [])) {
                c.page_ref = page; // ensure page
                contexts.push(c);
            }
        }
        catch {
            // skip pages with parse errors; continue
        }
    }
    // dedupe simple
    const key = (k) => `${k.kpi_id}|${k.unit}|${k.value}`;
    const dedupKpis = Array.from(new Map(kpis.map(k => [key(k), k])).values());
    const outDir = path.join(DATA, "out", company);
    await fs.mkdir(outDir, { recursive: true });
    await fs.writeFile(path.join(outDir, `${year}--kpis.json`), JSON.stringify(dedupKpis, null, 2));
    await fs.writeFile(path.join(outDir, `${year}--context.json`), JSON.stringify(contexts, null, 2));
    return { kpis: dedupKpis, contexts };
}
