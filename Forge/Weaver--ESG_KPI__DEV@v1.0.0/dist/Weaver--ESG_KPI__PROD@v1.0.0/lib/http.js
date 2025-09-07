import fetch from "node-fetch";
export async function getBuffer(url) {
    const r = await fetch(url, { redirect: "follow" });
    if (!r.ok)
        throw new Error(`HTTP ${r.status} for ${url}`);
    const arr = await r.arrayBuffer();
    return Buffer.from(arr);
}
export async function getText(url) {
    const r = await fetch(url, { redirect: "follow" });
    if (!r.ok)
        throw new Error(`HTTP ${r.status} for ${url}`);
    return r.text();
}
