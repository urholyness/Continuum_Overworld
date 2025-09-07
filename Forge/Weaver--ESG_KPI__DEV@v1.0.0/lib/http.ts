import fetch from "node-fetch";

export async function getBuffer(url: string): Promise<Buffer> {
  const r = await fetch(url, { redirect: "follow" as any });
  if (!r.ok) throw new Error(`HTTP ${r.status} for ${url}`);
  const arr = await r.arrayBuffer();
  return Buffer.from(arr);
}

export async function getText(url: string): Promise<string> {
  const r = await fetch(url, { redirect: "follow" as any });
  if (!r.ok) throw new Error(`HTTP ${r.status} for ${url}`);
  return r.text();
}