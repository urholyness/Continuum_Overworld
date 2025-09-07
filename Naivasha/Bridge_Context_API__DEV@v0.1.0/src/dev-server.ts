import express from "express";
import crypto from "crypto";

const app = express();
app.use(express.json());

// in-memory context store (DEV only)
type ContextItem = { id:string; path:string; kind?:string; tags?:string[]; content?:string; content_hash:string; updated_at:string; };
const ctx: Record<string, ContextItem> = {};
const events: any[] = [];
let etag = () => crypto.createHash("sha256").update(Object.values(ctx).map(i=>i.content_hash).join("|")).digest("hex");

function auth(req:any,res:any,next:any){
  const ok = (req.headers.authorization||"").includes(process.env.BRIDGE_TOKEN||"");
  if(!ok) return res.status(401).send("nope");
  next();
}

app.post("/v1/context/pull", auth, (req,res)=>{
  const items = Object.values(ctx);
  res.set("ETag", etag());
  res.json({ items });
});

app.post("/v1/context/push", auth, (req,res)=>{
  const now = new Date().toISOString();
  (req.body.items||[]).forEach((i:any)=>{
    ctx[i.path] = {
      id: i.id || i.path,
      path: i.path,
      kind: i.kind || "doc",
      tags: i.tags || [],
      content: i.content || "",
      content_hash: i.content_hash || crypto.createHash("sha256").update((i.content||"")+i.path).digest("hex"),
      updated_at: i.updated_at || now
    };
  });
  res.json({ accepted: (req.body.items||[]).map((i:any)=>i.id||i.path) });
});

app.post("/v1/memory/search", auth, (req,res)=>{
  const { query="", tags=[] } = req.body||{};
  const items = Object.values(ctx).filter(i=>{
    const t = (i.tags||[]).some(t=>tags.includes(t));
    const q = query ? (i.content||"").toLowerCase().includes(query.toLowerCase()) : true;
    return t || q;
  }).slice(0,5).map((i,ix)=>({ id:`hit-${ix}`, path:i.path, score:0.5, snippet:(i.content||"").slice(0,120), tags:i.tags||[] }));
  res.json({ results: items });
});

app.post("/v1/events/log", auth, (req,res)=>{ events.push(req.body); res.status(202).end(); });

const port = process.env.PORT || 3030;
app.listen(port, ()=>console.log(`Bridge_Context_API DEV up on http://127.0.0.1:${port}/v1`));
