import fs from "node:fs/promises";
import path from "node:path";

test("providers.yaml exists and is REAL", async () => {
  const cfg = await fs.readFile(path.join(process.cwd(), "config", "providers.yaml"), "utf8");
  expect(cfg).toMatch(/mode:\s*real/);
});