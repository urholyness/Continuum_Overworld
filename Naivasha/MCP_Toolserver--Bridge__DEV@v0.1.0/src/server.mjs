import fetch from "node-fetch";
import http from "http";
const API = process.env.BRIDGE_API_BASE || "http://127.0.0.1:3030/v1";
const TOKEN = process.env.BRIDGE_TOKEN || "devtoken";
async function call(path, body){
  const r = await fetch(`${API}${path}`, { method:"POST", headers:{ "content-type":"application/json", authorization:`Bearer ${TOKEN}` }, body: JSON.stringify(body||{}) });
  if(!r.ok) throw new Error(`${path} ${r.status}`);
  const etag=r.headers.get("etag"); const json = await r.json().catch(()=>({}));
  return { etag, ...json };
}
const tools = {
  "bridge.pull":          (input)=> call("/context/pull", input),
  "bridge.push":          (input)=> call("/context/push", input),
  "bridge.memory.search": (input)=> call("/memory/search", input),
  "bridge.events.log":    (input)=> call("/events/log", input)
};
const server = http.createServer(async (req,res)=>{
  if(req.method==="POST" && req.url.startsWith("/tool/")){
    try{
      const name = decodeURIComponent(req.url.replace("/tool/",""));
      let body=""; for await (const c of req){ body+=c; }
      const input = body? JSON.parse(body).input : {};
      if(!tools[name]) throw new Error(`unknown tool ${name}`);
      const out = await tools[name](input);
      res.writeHead(200,{"content-type":"application/json"}).end(JSON.stringify({ ok:true, result: out }));
    }catch(e){ res.writeHead(500,{"content-type":"application/json"}).end(JSON.stringify({ ok:false, error: String(e) })); }
    return;
  }
  res.writeHead(404).end();
});
const port = process.env.MCP_PORT || 7337;
server.listen(port, ()=> console.log(`Bridge MCP @ http://127.0.0.1:${port}`));
