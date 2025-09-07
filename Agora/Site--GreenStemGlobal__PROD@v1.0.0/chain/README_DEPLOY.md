# 🚀 LedgerCheckpoint Sepolia Deployment Guide

## Prerequisites
- Node.js 18+ installed
- MetaMask wallet with Sepolia ETH
- Infura or Alchemy account for RPC access

---

## ⚡ Quick Deploy

### 1. Setup Environment
```bash
cd chain

# Copy template and fill with your values
cp .env.example .env

# Edit .env file:
# ETH_RPC_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID
# PRIVATE_KEY=your_metamask_private_key_without_0x_prefix
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Compile Contract
```bash
npm run compile
```
Expected output: `Compiled 1 Solidity file successfully`

### 4. Deploy to Sepolia
```bash
npm run deploy:sepolia
```

**📝 IMPORTANT**: Save the printed contract address!
```
LedgerCheckpoint: 0x1234567890abcdef1234567890abcdef12345678
```

### 5. Verify Deployment
Visit: `https://sepolia.etherscan.io/address/YOUR_CONTRACT_ADDRESS`

You should see:
- Contract creation transaction
- Contract code verified (if using a known pattern)
- No transactions yet

---

## 🧪 Test Deployment (Optional)

### Emit Test Event
```bash
CONTRACT=0xYourContractAddress npm run emit:deposit
```

This will:
1. Emit a test DEPOSIT checkpoint
2. Print transaction hash
3. Show gas usage
4. Display event details

### Verify Event on Etherscan
1. Go to your contract on Sepolia Etherscan
2. Click "Events" tab
3. Look for `Checkpoint` event with:
   - `kind`: Hash of "DEPOSIT"
   - `ref`: Test reference string
   - `amount`: 25000
   - `currency`: "USD"

---

## 🔗 Next Steps

### For Frontend Integration:
1. Copy the contract address
2. Set `LEDGER_CONTRACT_ADDRESS=0xYourAddress` in:
   - Local: `.env.local`
   - Amplify: Environment variables
3. The website will automatically display recent checkpoints on the Investors page

### For Production Use:
1. **Fund the deployer wallet** with enough ETH for transactions
2. **Set up monitoring** for contract events
3. **Configure automatic event emission** when real deposits occur
4. **Consider upgrading to mainnet** when ready for production

---

## 🛠️ Troubleshooting

### "insufficient funds for intrinsic transaction cost"
- Your wallet needs more Sepolia ETH
- Get free Sepolia ETH from: https://sepoliafaucet.com

### "replacement transaction underpriced"
- Wait for previous transaction to confirm
- Or increase gas price in transaction

### "invalid private key"
- Ensure private key is exactly 64 characters (no 0x prefix)
- Double-check the private key from MetaMask

### "network does not exist"
- Verify `ETH_RPC_URL` is correct
- Test RPC endpoint manually: `curl -X POST -H "Content-Type: application/json" --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' YOUR_RPC_URL`

---

## 📋 Contract Functions

The deployed `LedgerCheckpoint` contract has these functions:

```solidity
function emitDeposit(string calldata ref, uint256 amount, string calldata currency) external
function emitFx(string calldata ref, uint256 amount, string calldata currency) external  
function emitTransferKE(string calldata ref, uint256 amount, string calldata currency) external
function emitAllocation(string calldata ref, uint256 amount, string calldata currency) external
```

All emit the same `Checkpoint` event with different `kind` values:
- DEPOSIT: `keccak256("DEPOSIT")`
- FX: `keccak256("FX")`
- TRANSFER_KE: `keccak256("TRANSFER_KE")`
- ALLOCATION: `keccak256("ALLOCATION")`

---

## 🔐 Security Notes

- ⚠️ **Never commit `.env` file to git**
- ⚠️ **Use a dedicated deployer wallet** (not your main wallet)
- ⚠️ **Keep private keys secure** and rotate regularly
- ✅ **Verify contract on Etherscan** if you modify the source
- ✅ **Test on Sepolia first** before mainnet deployment

---

**Contract deployed successfully! 🎉**

Your GreenStem Global website now has blockchain integration for transparent fund tracking.