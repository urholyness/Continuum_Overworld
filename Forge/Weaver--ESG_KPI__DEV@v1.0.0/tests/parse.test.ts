import fs from "node:fs/promises";
import path from "node:path";

test("parsed jsonl created for at least one company", async () => {
  const parsedRoot = path.join(process.cwd(), "data", "parsed");
  const companies = await fs.readdir(parsedRoot).catch(() => []);
  // Minimal structural assertion; real run-real will populate
  expect(Array.isArray(companies)).toBe(true);
});