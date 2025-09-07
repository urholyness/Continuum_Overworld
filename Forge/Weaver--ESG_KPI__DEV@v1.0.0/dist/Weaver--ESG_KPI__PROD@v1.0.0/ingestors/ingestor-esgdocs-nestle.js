import fs from "node:fs/promises";
import crypto from "node:crypto";
import fetch from "node-fetch";
export async function fetchNestlePDF(url, outPath) {
    const r = await fetch(url);
    if (!r.ok)
        throw new Error(`HTTP ${r.status}`);
    const buf = Buffer.from(await r.arrayBuffer());
    const sha256 = crypto.createHash("sha256").update(buf).digest("hex");
    await fs.mkdir(outPath, { recursive: true });
    const file = `${outPath}/Nestle-2023.pdf`;
    await fs.writeFile(file, buf);
    return { file, sha256, source_url: url, downloaded_at: new Date().toISOString() };
}
