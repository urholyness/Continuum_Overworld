import { ethers } from "hardhat";

async function main() {
  const contractAddress = process.env.CONTRACT;
  
  if (!contractAddress) {
    console.error("❌ CONTRACT environment variable not set");
    console.error("Usage: CONTRACT=0x123... npm run emit:deposit");
    process.exit(1);
  }

  console.log("⛓️ Emitting test deposit to LedgerCheckpoint...");
  console.log("📍 Contract Address:", contractAddress);

  // Get signer
  const [signer] = await ethers.getSigners();
  console.log("👤 Signer Address:", signer.address);

  // Attach to deployed contract
  const LedgerCheckpoint = await ethers.getContractFactory("LedgerCheckpoint");
  const contract = LedgerCheckpoint.attach(contractAddress);

  // Emit test deposit
  const ref = `TEST-DEPOSIT-${Date.now()}`;
  const amount = 25000; // $25,000 USD
  const currency = "USD";

  console.log("📝 Emitting deposit checkpoint:");
  console.log(`  Reference: ${ref}`);
  console.log(`  Amount: ${amount}`);
  console.log(`  Currency: ${currency}`);

  try {
    const tx = await contract.emitDeposit(ref, amount, currency);
    console.log("📡 Transaction submitted:", tx.hash);
    
    console.log("⏳ Waiting for confirmation...");
    const receipt = await tx.wait();
    
    console.log("✅ Deposit checkpoint emitted successfully!");
    console.log("🔍 Transaction Hash:", receipt.hash);
    console.log("⛽ Gas Used:", receipt.gasUsed.toString());
    console.log("🌐 View on Etherscan: https://sepolia.etherscan.io/tx/" + receipt.hash);
    
    // Parse events
    const events = receipt.logs.map((log: any) => {
      try {
        return contract.interface.parseLog(log);
      } catch (e) {
        return null;
      }
    }).filter(Boolean);
    
    events.forEach((event: any) => {
      if (event.name === 'Checkpoint') {
        console.log("📋 Event Details:");
        console.log(`  Kind: ${event.args.kind}`);
        console.log(`  Reference: ${event.args.ref}`);
        console.log(`  Amount: ${event.args.amount}`);
        console.log(`  Currency: ${event.args.currency}`);
      }
    });

  } catch (error) {
    console.error("❌ Failed to emit deposit:", error);
    process.exit(1);
  }
}

main().catch((error) => {
  console.error("💥 Script failed:", error);
  process.exit(1);
});