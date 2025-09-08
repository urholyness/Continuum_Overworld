"use client";

import { useEffect, useState } from "react";
import { getRecentCheckpoints } from "@/lib/ledger";

interface Checkpoint {
  kind: string;
  ref: string;
  amount: string;
  currency: string;
  txHash: string;
  timestamp: string;
}

export default function BlockchainBreadcrumbs() {
  const [checkpoints, setCheckpoints] = useState<Checkpoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const contractAddress = process.env.NEXT_PUBLIC_LEDGER_CONTRACT_ADDRESS;

  useEffect(() => {
    async function fetchCheckpoints() {
      if (!contractAddress) {
        setError("Contract address not configured");
        setLoading(false);
        return;
      }

      try {
        const data = await getRecentCheckpoints(5);
        setCheckpoints(data);
      } catch (err) {
        setError("Failed to fetch blockchain data");
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    fetchCheckpoints();
  }, [contractAddress]);

  if (!contractAddress) {
    return (
      <div className="p-4 border rounded-xl bg-neutral-100">
        <h3 className="font-medium mb-2">⛓️ On-chain Breadcrumbs</h3>
        <p className="text-sm text-neutral-600">
          Blockchain integration will be available after smart contract deployment.
        </p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="p-4 border rounded-xl bg-white">
        <h3 className="font-medium mb-2">⛓️ On-chain Breadcrumbs</h3>
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
          <span className="text-sm text-neutral-600">Loading blockchain events...</span>
        </div>
      </div>
    );
  }

  if (error || checkpoints.length === 0) {
    return (
      <div className="p-4 border rounded-xl bg-white">
        <h3 className="font-medium mb-2">⛓️ On-chain Breadcrumbs</h3>
        <p className="text-sm text-neutral-600">
          {error || "No blockchain events found yet."}
        </p>
        <p className="text-xs text-neutral-500 mt-1">
          Contract: <code className="bg-neutral-100 px-1 rounded">{contractAddress}</code>
        </p>
      </div>
    );
  }

  return (
    <div className="p-4 border rounded-xl bg-white">
      <h3 className="font-medium mb-3">⛓️ On-chain Breadcrumbs</h3>
      <div className="space-y-2">
        {checkpoints.map((checkpoint, idx) => (
          <div key={idx} className="flex items-center justify-between text-sm border-l-2 border-blue-200 pl-3">
            <div>
              <span className="font-medium text-blue-600">{checkpoint.kind}</span>
              <span className="text-neutral-600 ml-2">{checkpoint.ref}</span>
            </div>
            <div className="text-right">
              <div className="font-medium">
                {parseInt(checkpoint.amount).toLocaleString()} {checkpoint.currency}
              </div>
              <div className="text-xs text-neutral-500">
                {new Date(checkpoint.timestamp).toLocaleDateString()}
              </div>
            </div>
          </div>
        ))}
      </div>
      <div className="mt-3 pt-3 border-t">
        <a
          href={`https://sepolia.etherscan.io/address/${contractAddress}`}
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-blue-600 hover:underline"
        >
          View on Etherscan →
        </a>
      </div>
    </div>
  );
}