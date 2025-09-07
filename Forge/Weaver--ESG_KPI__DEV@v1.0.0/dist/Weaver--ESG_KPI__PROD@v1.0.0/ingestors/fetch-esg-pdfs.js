import fs from "node:fs/promises";
import path from "node:path";
import * as YAML from "yaml";
import * as cheerio from "cheerio";
import { getBuffer, getText } from "../lib/http.js";
import { sha256 } from "../lib/hash.js";
const ROOT = process.cwd();
const DATA = path.join(ROOT, "data");
const companySeeds = {
    "Lufthansa": ["https://investor-relations.lufthansagroup.com/en/publications/financial-reports.html", "https://www.lufthansagroup.com/en/company/responsibility.html"],
    "Air France-KLM": ["https://www.airfranceklm.com/en/finance/publications", "https://www.airfranceklm.com/en/sustainability"],
    "Maersk": ["https://www.maersk.com/news-and-advisories/sustainability", "https://www.maersk.com/investors/reports"],
    "Nestlé": ["https://www.nestle.com/investors/annual-report", "https://www.nestle.com/sustainability"],
    "Unilever": ["https://www.unilever.com/investors/annual-report-and-accounts/", "https://www.unilever.com/planet-and-society/"]
};
function yearRegex(y) {
    return new RegExp(`(?:^|[^\\d])${y}(?:[^\\d]|$)`);
}
function isPdfLink(href) {
    return !!href && /\.pdf($|\?)/i.test(href);
}
export async function loadProviders() {
    const cfg = await fs.readFile(path.join(ROOT, "config", "providers.yaml"), "utf8");
    const parsed = YAML.parse(cfg);
    if (parsed.mode !== "real")
        throw new Error("Weaver is not in REAL mode.");
    return parsed;
}
async function findPdfUrl(company, year) {
    const seeds = companySeeds[company] || [];
    for (const url of seeds) {
        try {
            const html = await getText(url);
            const $ = cheerio.load(html);
            const links = $("a[href]")
                .map((_, a) => ($(a).attr("href") || "").trim())
                .get()
                .filter(isPdfLink)
                .filter((h) => yearRegex(year).test(h));
            if (links.length) {
                // resolve relative links against seed url
                const resolved = new URL(links[0], url).toString();
                return resolved;
            }
        }
        catch { /* continue */ }
    }
    throw new Error(`PDF not found for ${company} ${year} on official seeds.`);
}
export async function fetchEsgPdf(company, year) {
    const pdfUrl = await findPdfUrl(company, year);
    const buf = await getBuffer(pdfUrl);
    const hash = sha256(buf);
    const outDir = path.join(DATA, "raw", company);
    await fs.mkdir(outDir, { recursive: true });
    const filePath = path.join(outDir, `${year}.pdf`);
    await fs.writeFile(filePath, buf);
    const metaDir = path.join(DATA, "meta", company);
    await fs.mkdir(metaDir, { recursive: true });
    const metaPath = path.join(metaDir, `${year}.json`);
    const meta = {
        source_url: pdfUrl,
        sha256: hash,
        downloaded_at: new Date().toISOString(),
        content_length: buf.length,
        content_type: "application/pdf"
    };
    await fs.writeFile(metaPath, JSON.stringify(meta, null, 2));
    return { filePath, metaPath, ...meta };
}
export async function runAcquire() {
    const cfg = await loadProviders();
    for (const c of cfg.esg_docs.companies) {
        for (const y of cfg.esg_docs.years) {
            console.log(`[acquire] ${c} ${y}`);
            await fetchEsgPdf(c, y);
        }
    }
}
if (process.argv[1]?.endsWith("fetch-esg-pdfs.ts")) {
    runAcquire().catch(e => { console.error(e); process.exit(1); });
}
