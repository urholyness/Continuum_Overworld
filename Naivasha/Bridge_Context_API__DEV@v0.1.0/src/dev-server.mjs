// src/dev-server.mjs — Namespaces + Version History (backward-compatible)
import express from "express";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const app = express();
app.use(express.json());

const PORT  = process.env.BRIDGE_PORT   || 3031;
const TOKEN = process.env.BRIDGE_TOKEN  || "devtoken";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const STORE_FILE  = path.join(HERE, "bridge-store.json");   // current snapshot
const EVENTS_FILE = path.join(HERE, "bridge-events.jsonl"); // append-only log

// ---------- util ----------
function loadJSON(file, fallback) {
  try { return fs.existsSync(file) ? JSON.parse(fs.readFileSync(file, "utf8")) : fallback; }
  catch { return fallback; }
}
function saveJSON(file, obj) {
  fs.writeFileSync(file, JSON.stringify(obj, null, 2));
}
function appendJSONL(file, obj) {
  fs.appendFileSync(file, JSON.stringify(obj) + "\n");
}
function nowISO() { return new Date().toISOString(); }

// ---------- state ----------
// structure: { [ns]: { [project]: { version:number, state:object } } }
let memory = loadJSON(STORE_FILE, {});

// ---------- auth ----------
function auth(req, res, next) {
  const token = req.headers.authorization?.replace("Bearer ", "") || req.body.token;
  if (token !== TOKEN) return res.status(401).json({ error: "Invalid token" });
  next();
}

// ---------- routes ----------

// PUSH (compatible)
// body: { ns?, project, context }
// default ns = "Naivasha"
app.post("/v1/context/push", auth, (req, res) => {
  const { ns = "Naivasha", project, context } = req.body || {};
  if (!project) return res.status(400).json({ error: "Missing project" });

  // init lane
  memory[ns] ??= {};
  const cur = memory[ns][project] ?? { version: 0, state: {} };

  // version bump + new state
  const nextVersion = (cur.version || 0) + 1;
  const newState = context || {};

  memory[ns][project] = { version: nextVersion, state: newState };
  saveJSON(STORE_FILE, memory);

  // append event
  const evt = {
    ts: nowISO(),
    ns,
    project,
    version: nextVersion,
    actor: "Bridge",        // could be set by clients later
    kind: "context.push",
    diff_hint: Object.keys(newState), // cheap hint
  };
  appendJSONL(EVENTS_FILE, evt);

  res.json({ accepted: true, ns, project, version: nextVersion, stored: newState });
});

// PULL snapshot (compatible)
// body: { ns?, project }
app.post("/v1/context/pull", auth, (req, res) => {
  const { ns = "Naivasha", project } = req.body || {};
  if (!project) return res.status(400).json({ error: "Missing project" });

  const lane = memory[ns]?.[project] || { version: 0, state: {} };
  res.json({ ns, project, version: lane.version, items: lane.state });
});

// PULL since (delta/time-travel friendly, optional)
// body: { ns?, project, sinceVersion? }
// returns events >= sinceVersion for that ns/project
app.post("/v1/context/deltas", auth, (req, res) => {
  const { ns = "Naivasha", project, sinceVersion = 0 } = req.body || {};
  if (!project) return res.status(400).json({ error: "Missing project" });

  if (!fs.existsSync(EVENTS_FILE)) return res.json({ ns, project, events: [] });

  const lines = fs.readFileSync(EVENTS_FILE, "utf8").trim().split("\n").filter(Boolean);
  const events = lines
    .map(l => { try { return JSON.parse(l); } catch { return null; } })
    .filter(e => e && e.ns === ns && e.project === project && (e.version ?? 0) >= sinceVersion);

  res.json({ ns, project, events });
});

// Health
app.get("/v1/health", (_req, res) => {
  const namespaces = Object.keys(memory);
  res.json({ ok: true, namespaces, port: String(PORT) });
});

app.listen(PORT, () =>
  console.log(`Bridge_Context_API DEV @ http://127.0.0.1:${PORT}/v1`)
);
