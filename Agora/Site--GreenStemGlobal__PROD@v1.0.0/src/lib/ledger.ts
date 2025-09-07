import { ethers } from "ethers";

const abi = [
  "event Checkpoint(bytes32 indexed kind, string ref, uint256 amount, string currency)",
];

export async function getRecentCheckpoints(address: string) {
  if (!process.env.ETH_RPC_URL) {
    console.warn("ETH_RPC_URL not configured");
    return [];
  }

  try {
    const provider = new ethers.JsonRpcProvider(process.env.ETH_RPC_URL);
    const contract = new ethers.Contract(address, abi, provider);
    const filter = contract.filters.Checkpoint();
    const fromBlock = -5000; // last ~5000 blocks
    const logs = await contract.queryFilter(filter, fromBlock);
    
    // hydrate block timestamps and decode kind
    const out = [];
    for (const l of logs) {
      const block = await l.getBlock();
      const kindHash = l.args[0];
      let kindName = "UNKNOWN";
      
      // Decode common kinds
      if (kindHash === ethers.keccak256(ethers.toUtf8Bytes("DEPOSIT"))) kindName = "DEPOSIT";
      else if (kindHash === ethers.keccak256(ethers.toUtf8Bytes("FX"))) kindName = "FX";
      else if (kindHash === ethers.keccak256(ethers.toUtf8Bytes("TRANSFER_KE"))) kindName = "TRANSFER_KE";
      else if (kindHash === ethers.keccak256(ethers.toUtf8Bytes("ALLOCATION"))) kindName = "ALLOCATION";
      
      out.push({
        kind: kindName,
        kindHash: kindHash,
        ref: l.args[1],
        amount: l.args[2].toString(),
        currency: l.args[3],
        tx: l.transactionHash,
        blockNumber: l.blockNumber,
        ts: new Date(Number(block.timestamp) * 1000).toISOString(),
      });
    }
    
    // Sort by block number (newest first)
    return out.sort((a, b) => b.blockNumber - a.blockNumber).slice(0, 5);
  } catch (error) {
    console.error("Failed to fetch checkpoints:", error);
    return [];
  }
}