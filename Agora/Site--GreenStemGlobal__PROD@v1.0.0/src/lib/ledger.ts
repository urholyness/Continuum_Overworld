import { ethers } from "ethers";
import { CONTRACT_ABI } from "../mocks/contractABI";

const RPC_URL = process.env.NEXT_PUBLIC_ETH_RPC_URL || "https://sepolia.infura.io/v3/YOUR_PROJECT_ID";
const CONTRACT_ADDRESS = process.env.NEXT_PUBLIC_LEDGER_CONTRACT_ADDRESS || "0x0000000000000000000000000000000000000000";

export async function getRecentCheckpoints(limit = 5) {
  try {
    const provider = new ethers.JsonRpcProvider(RPC_URL);
    const contract = new ethers.Contract(CONTRACT_ADDRESS, CONTRACT_ABI, provider);
    
    const filter = contract.filters.Checkpoint();
    const currentBlock = await provider.getBlockNumber();
    const fromBlock = Math.max(0, currentBlock - 10000); // Look back 10000 blocks
    
    const logs = await contract.queryFilter(filter, fromBlock, currentBlock);
    
    const checkpoints = [];
    
    // Take last 'limit' logs
    const recentLogs = logs.slice(-limit).reverse();
    
    for (const log of recentLogs) {
      // Type guard to ensure we have an EventLog with args
      if (!('args' in log)) continue;
      
      const block = await log.getBlock();
      const eventLog = log as ethers.EventLog;
      const kindHash = eventLog.args[0];
      let kindName = "UNKNOWN";
      
      // Decode common kinds
      if (kindHash === ethers.id("DEPOSIT")) kindName = "DEPOSIT";
      else if (kindHash === ethers.id("FX")) kindName = "FX";
      else if (kindHash === ethers.id("TRANSFER_KE")) kindName = "TRANSFER_KE";
      else if (kindHash === ethers.id("ALLOCATION")) kindName = "ALLOCATION";
      
      checkpoints.push({
        kind: kindName,
        ref: eventLog.args[1],
        amount: ethers.formatUnits(eventLog.args[2], 6), // Assuming 6 decimals for USDC
        currency: eventLog.args[3],
        timestamp: new Date(Number(block.timestamp) * 1000).toISOString(),
        txHash: log.transactionHash,
      });
    }
    
    return checkpoints;
  } catch (error) {
    console.error("Error fetching blockchain checkpoints:", error);
    // Return mock data as fallback
    return [
      {
        kind: "DEPOSIT",
        ref: "INV-2024-001",
        amount: "25000",
        currency: "USD",
        timestamp: new Date().toISOString(),
        txHash: "0x1234...mock",
      },
    ];
  }
}

export function getEtherscanUrl(txHash: string): string {
  return `https://sepolia.etherscan.io/tx/${txHash}`;
}