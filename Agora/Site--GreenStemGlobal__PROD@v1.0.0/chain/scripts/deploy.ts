import { ethers } from "hardhat";

async function main() {
  const F = await ethers.getContractFactory("LedgerCheckpoint");
  const c = await F.deploy();
  await c.waitForDeployment();
  console.log("LedgerCheckpoint:", await c.getAddress());
}

main().catch((e) => { 
  console.error(e); 
  process.exit(1); 
});