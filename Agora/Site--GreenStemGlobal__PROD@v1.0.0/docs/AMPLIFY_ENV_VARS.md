# 🔧 AWS Amplify Environment Variables

Configure these environment variables in AWS Amplify Console for proper deployment.

## Required Variables

### **Core Application**
```bash
NEXT_PUBLIC_SITE_ENV=prod|staging
NEXT_PUBLIC_BASE_URL=https://<amplify-domain>
NEXT_PUBLIC_CHAIN_ID=11155111
```

### **Blockchain Integration**
```bash
LEDGER_CONTRACT_ADDRESS=<set after deploy>
ETH_RPC_URL=<your Sepolia RPC>
NEXT_PUBLIC_LEDGER_CONTRACT_ADDRESS=<same as LEDGER_CONTRACT_ADDRESS>
```

### **Authentication (Optional)**
```bash
COGNITO_USER_POOL_ID=<optional>
COGNITO_CLIENT_ID=<optional>
```

---

## Environment-Specific Values

### **Staging Environment**
```bash
NEXT_PUBLIC_SITE_ENV=staging
NEXT_PUBLIC_BASE_URL=https://staging.greenstemglobal.com
NEXT_PUBLIC_CHAIN_ID=11155111
ETH_RPC_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID
LEDGER_CONTRACT_ADDRESS=0xYourContractAddress
NEXT_PUBLIC_LEDGER_CONTRACT_ADDRESS=0xYourContractAddress
```

### **Production Environment**
```bash
NEXT_PUBLIC_SITE_ENV=prod
NEXT_PUBLIC_BASE_URL=https://greenstemglobal.com
NEXT_PUBLIC_CHAIN_ID=11155111
ETH_RPC_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID
LEDGER_CONTRACT_ADDRESS=0xYourContractAddress
NEXT_PUBLIC_LEDGER_CONTRACT_ADDRESS=0xYourContractAddress
```

---

## How to Set in Amplify Console

### **Method 1: Amplify Console Web UI**
1. Go to AWS Amplify Console
2. Select your app
3. Go to **Environment variables** in left sidebar
4. Click **Manage variables**
5. Add each variable name and value
6. Save changes
7. Redeploy app

### **Method 2: Amplify CLI**
```bash
# Set environment variable
amplify env checkout staging
amplify env add

# Or update existing
amplify env update
```

### **Method 3: AWS CLI**
```bash
# List current variables
aws amplify get-app --app-id YOUR_APP_ID

# Update environment variables
aws amplify update-app \
  --app-id YOUR_APP_ID \
  --environment-variables NEXT_PUBLIC_SITE_ENV=prod,LEDGER_CONTRACT_ADDRESS=0x123...
```

---

## Variable Descriptions

| Variable | Purpose | Example |
|----------|---------|---------|
| `NEXT_PUBLIC_SITE_ENV` | Environment identifier | `staging`, `prod` |
| `NEXT_PUBLIC_BASE_URL` | Website base URL | `https://greenstemglobal.com` |
| `NEXT_PUBLIC_CHAIN_ID` | Ethereum network | `11155111` (Sepolia) |
| `ETH_RPC_URL` | Blockchain RPC endpoint | `https://sepolia.infura.io/v3/...` |
| `LEDGER_CONTRACT_ADDRESS` | Smart contract address | `0x1234...` |
| `NEXT_PUBLIC_LEDGER_CONTRACT_ADDRESS` | Contract address (client-side) | Same as above |
| `COGNITO_USER_POOL_ID` | AWS Cognito User Pool | `us-east-1_AbCdEfGhI` |
| `COGNITO_CLIENT_ID` | AWS Cognito App Client | `1234567890abcdef` |

---

## Important Notes

### **Public vs Private Variables**
- Variables starting with `NEXT_PUBLIC_` are exposed to the browser
- Other variables are only available server-side
- **Never put secrets in `NEXT_PUBLIC_` variables**

### **Contract Address Setup**
1. Deploy smart contract first: `npm run deploy:sepolia` in `/chain` folder
2. Copy the printed contract address
3. Set both `LEDGER_CONTRACT_ADDRESS` and `NEXT_PUBLIC_LEDGER_CONTRACT_ADDRESS` to the same value
4. Redeploy Amplify app

### **RPC Endpoint Options**
- **Infura**: `https://sepolia.infura.io/v3/YOUR_PROJECT_ID`
- **Alchemy**: `https://eth-sepolia.g.alchemy.com/v2/YOUR_API_KEY`
- **Ankr**: `https://rpc.ankr.com/eth_sepolia`

### **Testing Variables**
After setting variables, test with:
```bash
# Check if variables are loaded
curl https://your-amplify-domain.com/api/health

# Check blockchain integration
curl https://your-amplify-domain.com/investors
```

---

## Troubleshooting

### **"Contract address not configured"**
- Ensure `NEXT_PUBLIC_LEDGER_CONTRACT_ADDRESS` is set
- Check that the address is valid (starts with 0x, 42 characters)
- Redeploy app after setting variables

### **"Failed to fetch blockchain data"**
- Verify `ETH_RPC_URL` is working
- Test RPC endpoint: `curl -X POST -H "Content-Type: application/json" --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' YOUR_RPC_URL`
- Check if contract exists at the address

### **Build failures**
- Ensure all `NEXT_PUBLIC_` variables are set
- Check Amplify build logs for specific errors
- Verify no undefined environment variables in code

---

**Environment variables configured! ✅**

Your GreenStem Global website will now have proper configuration for each environment.