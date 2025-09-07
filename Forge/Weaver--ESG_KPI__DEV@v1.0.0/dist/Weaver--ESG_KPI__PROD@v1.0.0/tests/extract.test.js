import fs from "node:fs/promises";
import path from "node:path";
test("output schema sanity (if present)", async () => {
    const outRoot = path.join(process.cwd(), "data", "out");
    const exists = await fs.readdir(outRoot).catch(() => []);
    if (!exists.length)
        return; // skip if not run yet
    const companyDir = path.join(outRoot, exists[0]);
    const files = await fs.readdir(companyDir);
    const k = files.find(f => /--kpis\.json$/.test(f));
    const c = files.find(f => /--context\.json$/.test(f));
    expect(Boolean(k && c)).toBe(true);
});
