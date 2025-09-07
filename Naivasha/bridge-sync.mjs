import http from "http";
import fs from "fs";
import path from "path";

const BRIDGE_PORT = process.env.BRIDGE_PORT || 3031;
const BRIDGE_TOKEN = process.env.BRIDGE_TOKEN || "devtoken";
const PROJECT = process.env.BRIDGE_PROJECT || "Continuum_Overworld";

// where engineers read from (adjust if you want a different path)
const OUT_FILE = path.resolve("C:\\Users\\Password\\Continuum_Overworld\\context.json");

function pull(project){
  const body = JSON.stringify({ project });
  const opts = {
    hostname: "127.0.0.1",
    port: BRIDGE_PORT,
    path: "/v1/context/pull",
    method: "POST",
    headers: {
      "content-type": "application/json",
      "content-length": Buffer.byteLength(body),
      authorization: `Bearer ${BRIDGE_TOKEN}`
    }
  };
  return new Promise((resolve, reject)=>{
    const req = http.request(opts, res=>{
      let data=""; res.on("data", c=> data+=c);
      res.on("end", ()=> { try{ resolve(JSON.parse(data)); } catch(e){ reject(e); }});
    });
    req.on("error", reject);
    req.write(body); req.end();
  });
}

let last = "";
async function tick(){
  try{
    const res = await pull(PROJECT);
    const now = JSON.stringify(res.items ?? {});
    if (now !== last) {
      fs.writeFileSync(OUT_FILE, JSON.stringify(res, null, 2));
      console.log(`[bridge-sync] updated ${OUT_FILE} @ ${new Date().toISOString()}`);
      last = now;
    }
  }catch(e){
    console.error("[bridge-sync] error:", e.message);
  }
}

console.log(`[bridge-sync] watching project=${PROJECT} ? ${OUT_FILE}`);
setInterval(tick, 3000);
tick();
