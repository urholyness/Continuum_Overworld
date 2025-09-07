import fs from "node:fs/promises";
import path from "node:path";
import pdf from "pdf-parse";

const ROOT = process.cwd();
const DATA = path.join(ROOT, "data");

export async function parsePdfToJsonl(company: string, year: number) {
  const pdfPath = path.join(DATA, "raw", company, `${year}.pdf`);
  const buf = await fs.readFile(pdfPath);
  const res = await pdf(buf); // flat text, but includes page breaks like \n\n
  // Basic page split heuristic — TODO: replace with a true page extractor if needed
  const pages = res.text.split(/\f|\n\s*\n/g).filter(Boolean);

  const outDir = path.join(DATA, "parsed", company);
  await fs.mkdir(outDir, { recursive: true });
  const outPath = path.join(outDir, `${year}.jsonl`);
  const lines = pages.map((text: string, i: number) => JSON.stringify({ page: i + 1, text }));
  await fs.writeFile(outPath, lines.join("\n"));
  return { outPath, pages: pages.length };
}

export async function runParse(companies: string[], years: number[]) {
  for (const c of companies) for (const y of years) {
    console.log(`[parse] ${c} ${y}`);
    await parsePdfToJsonl(c, y);
  }
}

if (process.argv[1]?.endsWith("pdf-parse.ts")) {
  const companies = process.argv.slice(2);
  if (!companies.length) throw new Error("Provide at least one company.");
  // default year 2023 for ad-hoc run
  runParse(companies, [2023]).catch(e => { console.error(e); process.exit(1); });
}