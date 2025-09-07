export const cfg = {
  env: process.env.NEXT_PUBLIC_SITE_ENV || "staging",
  base: process.env.NEXT_PUBLIC_BASE_URL || "",
  chainId: Number(process.env.NEXT_PUBLIC_CHAIN_ID || 11155111),
  ledgerAddress: process.env.LEDGER_CONTRACT_ADDRESS || "",
};