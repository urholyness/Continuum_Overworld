# The_Bridge/WorkOrders/WORK_ORDER--Deploy__Sepolia@v1.0.0
Owner: ENV (Claude Code)  |  Authority: BRIDGE (Naivasha)  |  Division: Agora ↔ Pantheon  
Scope: Prepare, verify, and document Sepolia deployment pipeline for GreenStemGlobal site, wire read‑only on‑chain events into Investors page. **No secrets handled.**

---

## 0) Context
Artifact under execution: `Continuum_Overworld/Agora/Site--GreenStemGlobal__PROD@v1.0.0`
Relevant subpaths:
- `chain/` → Hardhat project (contracts, scripts, config)
- `src/` → Next.js 14 app with Buyers/Investors pages
- `src/lib/ledger.ts` → ethers helper (to be finalized)

Agents: `ledger_agent` (MAR), `buyer_trace_agent` (read-only linkage).

---

## 1) Tasks (Claude)
1. **Sanity check the Hardhat workspace**
   - Confirm presence of: `contracts/LedgerCheckpoint.sol`, `hardhat.config.ts`, `scripts/deploy.ts`, `package.json`, `.env.example`.
   - Ensure `dotenv` import + `dotenv.config()` is present in `hardhat.config.ts`.
   - Ensure network `sepolia` reads `ETH_RPC_URL` & `PRIVATE_KEY` from env.

2. **Package hygiene**
   - Dev deps must include: `hardhat`, `@nomicfoundation/hardhat-toolbox`, `typescript`, `ts-node`, `dotenv`.
   - Add NPM scripts to `chain/package.json`:
     ```json
     {
       "scripts": {
         "compile": "hardhat compile",
         "deploy:sepolia": "hardhat run scripts/deploy.ts --network sepolia",
         "emit:deposit": "hardhat run scripts/emit.ts --network sepolia"
       }
     }
     ```

3. **Emit script** (no secrets)
   - Create `chain/scripts/emit.ts`:
     - Reads `process.env.CONTRACT`.
     - Calls `emitDeposit(ref, amount, currency)` on the deployed `LedgerCheckpoint`.
     - Prints tx hash and waits for confirmation.
   - Fail gracefully if `CONTRACT` is missing.

4. **.env template**
   - Update `chain/.env.example` (placeholders only, no values):
     ```env
     ETH_RPC_URL=https://sepolia.infura.io/v3/<YOUR_PROJECT_ID>
     PRIVATE_KEY=<YOUR_METAMASK_PRIVATE_KEY>
     ```
   - Ensure `.env` is in `.gitignore`.

5. **Docs for operator**
   - Add `chain/README_DEPLOY.md` with exact operator steps:
     - Copy `.env.example` → `.env` and fill two fields.
     - `npm install` → `npm run compile` → `npm run deploy:sepolia`.
     - Save printed contract address.
     - Optional: `CONTRACT=<addr> npm run emit:deposit` (creates a DEPOSIT checkpoint).
     - Link to `https://sepolia.etherscan.io/address/<addr>` for verification.

6. **Front‑end wire‑up (read‑only)**
   - Finalize `src/lib/ledger.ts` helper `getRecentCheckpoints(address: string)` using ethers v6.
   - In `src/app/investors/page.tsx`, under the existing FundsTimeline, render a small panel labeled **“On‑chain breadcrumbs”** that lists the last 5 `Checkpoint` events (kind/ref/amount/currency/ts).
   - If `process.env.LEDGER_CONTRACT_ADDRESS` is missing, render a friendly placeholder.

7. **Amplify env reference (no values)**
   - Add `/docs/AMPLIFY_ENV_VARS.md` with **names only**:
     ```
     NEXT_PUBLIC_SITE_ENV=prod|staging
     NEXT_PUBLIC_BASE_URL=https://<amplify-domain>
     NEXT_PUBLIC_CHAIN_ID=11155111
     LEDGER_CONTRACT_ADDRESS=<set after deploy>
     ETH_RPC_URL=<your Sepolia RPC>
     COGNITO_USER_POOL_ID=<optional>
     COGNITO_CLIENT_ID=<optional>
     ```

8. **PR creation**
   - Open PR: `Agora/Site v1 — Sepolia deploy & on‑chain readback (no secrets)`.
   - Include test notes and confirm local compile.

---

## 2) Constraints (Aegis)
- Do **not** request, read, or store secrets. Operator will provide `.env` locally.
- `.env` files must remain ignored by Git.
- Contract address (public) is allowed in docs and env placeholders.

---

## 3) Inputs & Outputs
**Inputs:** current repo tree, mocks under `/mocks`, existing Next.js app.  
**Outputs:**
- Updated `chain/package.json` scripts.
- New `chain/scripts/emit.ts`.
- Updated `chain/.env.example`.
- New `chain/README_DEPLOY.md`.
- Updated `src/lib/ledger.ts` and Investors page panel.
- `/docs/AMPLIFY_ENV_VARS.md`.
- Pull Request with changes.

---

## 4) Definition of Done (DoD)
- `npx hardhat compile` passes with only the two env vars required at runtime.
- `emit.ts` runs when `CONTRACT=<addr>` is provided.
- Investors page shows recent checkpoints when `LEDGER_CONTRACT_ADDRESS` is set.
- PR created with clear operator instructions and without secrets.

---

## 5) Handoff Notes for Operator (George/Naivasha)
1. Fill `chain/.env` locally with:
   ```
   ETH_RPC_URL=https://sepolia.infura.io/v3/<YOUR_PROJECT_ID>
   PRIVATE_KEY=<your MetaMask private key>
   ```
2. Deploy:
   ```
   cd chain
   npm install
   npm run compile
   npm run deploy:sepolia
   ```
3. Copy contract address → set `LEDGER_CONTRACT_ADDRESS` in web `.env.local` and Amplify env.
4. (Optional) Emit a test event:
   ```
   CONTRACT=<addr> npm run emit:deposit
   ```

---

## 6) Routing (MCP)
Topic: `ops.traceability.v1`  
Agent: `Claude Code`  
Priority: High  
SLA: EOD next business day  

