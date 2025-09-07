# GreenStem Global Web v1

Dynamic site for Buyers + Investors with mock traceability data and Sepolia on‑chain breadcrumbs.

## Quickstart

1) Install: `npm install`
2) Env: copy `.env.example` to `.env.local` and fill keys.
3) Dev: `npm run dev` → http://localhost:3000

## Deploy

- Connect repo in AWS Amplify (branches: main → prod, dev → stage)
- Set env vars in Amplify per branch
- Push to trigger CI

## Chain

- Deploy `LedgerCheckpoint.sol` to Sepolia → put address in secrets
- Use `/src/lib/ledger.ts` to read recent `Checkpoint` events (wire later to UI)

### Deploy Contract
```bash
cd chain
npm install
cp .env.example .env # add ETH_RPC_URL + PRIVATE_KEY (deployer)
npx hardhat compile
npx hardhat run scripts/deploy.ts --network sepolia
```

## Data Contracts

- `GET /api/trace/lots` → returns `/mocks/lots_sample.json`
- `GET /api/trace/funds` → returns `/mocks/funds_sample.json` (download via `?download=1`)

## Project Structure

```
Agora/Site--GreenStemGlobal__PROD@v1.0.0/
├── src/
│   ├── app/              # Next.js app router pages
│   │   ├── api/trace/    # API routes for trace data
│   │   ├── buyers/       # Buyers traceability page
│   │   ├── investors/    # Investors portal
│   │   └── trace/[id]/   # Trace detail page
│   ├── components/       # React components
│   └── lib/             # Utilities (ledger, config)
├── mocks/               # Sample JSON data
├── chain/               # Solidity contract & Hardhat
├── agents/              # C_O integration (MAR, MCP)
└── .github/workflows/   # CI/CD pipeline
```

## Environment Variables

Required for production:
- `NEXT_PUBLIC_BASE_URL` - Base URL for API calls
- `NEXT_PUBLIC_CHAIN_ID` - Ethereum chain ID (11155111 for Sepolia)
- `ETH_RPC_URL` - Ethereum RPC endpoint
- `LEDGER_CONTRACT_ADDRESS` - Deployed contract address
- `COGNITO_USER_POOL_ID` - AWS Cognito pool
- `COGNITO_CLIENT_ID` - AWS Cognito client

## Roadmap

- Replace mocks with C_O MCP calls
- Cognito‑gated investor downloads
- NDVI tiles per lot (image URLs)
- API Gateway + Lambda for ingest `/api/ingest/ledger`

## Punchlist (DoD for v1)

- [ ] Amplify apps created (prod/stage) + domain mapping
- [ ] Cognito pool + client IDs saved as secrets
- [ ] Sepolia contract deployed; address saved as LEDGER_CONTRACT_ADDRESS
- [ ] Pages render with mock data; download link works
- [ ] MAR registry committed under /agents/mar
- [ ] README covers run + deploy + keys

## Tech Stack

- **Frontend**: Next.js 14 (App Router) + TypeScript + Tailwind CSS
- **API**: Next.js Route Handlers (v1), upgrade path → API Gateway + Lambda
- **Auth**: AWS Cognito (Investors portal)
- **Storage**: S3 for static assets + JSON mocks
- **Hosting**: AWS Amplify Hosting (SSR-ready)
- **Blockchain**: ethers.js → Sepolia testnet
- **C_O Integration**: MAR registry + MCP topics