import fs from "fs";import readline from "readline";
const s=fs.createReadStream("Continuum_Overworld/Aegis/Audit/decision-packets.jsonl");
readline.createInterface({input:s}).on("line",l=>{try{const j=JSON.parse(l);console.log(`[${j.status}] ${j.actor} :: ${j.intent} ${j.company||""} ${j.year||""}`)}catch{}})