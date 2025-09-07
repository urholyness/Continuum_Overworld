#!/bin/bash

# Deploy smart contracts for Continuum_Overworld
set -e

ENVIRONMENT=${1:-staging}
NETWORK=${2:-sepolia}
REGION=${AWS_REGION:-us-east-1}

echo "⛓️ Deploying smart contracts to $NETWORK for $ENVIRONMENT environment..."

cd Agora/Site--GreenStemGlobal__PROD@v1.0.0/chain

# Install dependencies if not present
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Get blockchain configuration from AWS Secrets Manager
SECRET_VALUE=$(aws secretsmanager get-secret-value \
    --secret-id "continuum/$ENVIRONMENT/blockchain" \
    --region $REGION \
    --query SecretString \
    --output text)

RPC_URL=$(echo $SECRET_VALUE | jq -r '.rpc_url')

# Create .env file for deployment
cat > .env << EOF
ETH_RPC_URL=$RPC_URL
PRIVATE_KEY=$METAMASK_PRIVATE_KEY
EOF

# Compile contracts
echo "🔨 Compiling contracts..."
npx hardhat compile

# Deploy LedgerCheckpoint contract
echo "🚀 Deploying LedgerCheckpoint contract..."
DEPLOY_OUTPUT=$(npx hardhat run scripts/deploy.ts --network $NETWORK)
CONTRACT_ADDRESS=$(echo "$DEPLOY_OUTPUT" | grep "LedgerCheckpoint:" | cut -d' ' -f2)

echo "✅ Contract deployed at: $CONTRACT_ADDRESS"

# Update blockchain secret with contract address
UPDATED_SECRET=$(echo $SECRET_VALUE | jq --arg addr "$CONTRACT_ADDRESS" '.contract_address = $addr')

aws secretsmanager update-secret \
    --secret-id "continuum/$ENVIRONMENT/blockchain" \
    --secret-string "$UPDATED_SECRET" \
    --region $REGION

# Verify contract on Etherscan (for Sepolia)
if [ "$NETWORK" = "sepolia" ]; then
    echo "🔍 Verifying contract on Etherscan..."
    npx hardhat verify --network sepolia $CONTRACT_ADDRESS || echo "Verification failed (contract might already be verified)"
fi

# Test contract functionality
echo "🧪 Testing contract functionality..."
cat > test-contract.js << 'EOF'
const { ethers } = require("hardhat");

async function main() {
    const contractAddress = process.env.CONTRACT_ADDRESS;
    const LedgerCheckpoint = await ethers.getContractFactory("LedgerCheckpoint");
    const contract = LedgerCheckpoint.attach(contractAddress);
    
    console.log("Testing deposit checkpoint...");
    const tx = await contract.emitDeposit("TEST-001", 25000, "USD");
    await tx.wait();
    
    console.log("✅ Contract test successful!");
    console.log("Transaction hash:", tx.hash);
}

main().catch((error) => {
    console.error(error);
    process.exit(1);
});
EOF

CONTRACT_ADDRESS=$CONTRACT_ADDRESS node test-contract.js

# Clean up
rm -f .env test-contract.js

# Update GitHub secrets
if command -v gh &> /dev/null; then
    echo $CONTRACT_ADDRESS | gh secret set LEDGER_CONTRACT_ADDRESS_${ENVIRONMENT^^} -R $(git remote get-url origin)
    echo "🔑 GitHub secret LEDGER_CONTRACT_ADDRESS_${ENVIRONMENT^^} updated"
fi

echo "🎯 Blockchain deployment complete!"
echo "📝 Contract Address: $CONTRACT_ADDRESS"
echo "🌐 Network: $NETWORK"
echo "🔍 View on Etherscan: https://${NETWORK}.etherscan.io/address/$CONTRACT_ADDRESS"

cd - > /dev/null