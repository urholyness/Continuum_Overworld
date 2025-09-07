# Contracts--SupplyChain__ETH@v0.1.0

Ethereum smart contracts for supply chain step aggregation management with division-based completion tracking.

## Features

- **Contract Creation**: Create supply chain contracts with required division categories
- **Step Completion**: Track division-based step completion with immutable proof hashes
- **Aggregation Model**: Collect all required division steps before contract closure
- **Legacy Negotiation**: Support manual counterparty designation for private workflows
- **Event Logging**: Complete audit trail of all contract and step actions

## Contract Architecture

### SupplyChainChain.sol

Main contract implementing the step aggregation workflow:

1. **Contract Opening** → `openContract()`
2. **Step Completion** → `completeStep()` (per division)
3. **Category Management** → `addRequiredCategories()` (optional)
4. **Contract Closure** → `closeContract()` (when all steps complete)
5. **Legacy Negotiation** → `setCounterparty()` (for manual designation)

### Key Functions

```solidity
// Create new supply chain contract
function openContract(
    string memory metadataHash,     // IPFS hash of contract details
    string[] memory requiredCategories, // Division categories required
    address counterparty            // Optional counterparty for legacy mode
) external returns (uint256 contractId)

// Complete a division step
function completeStep(
    uint256 contractId,
    string memory category,  // Division name (Forge, Atlas, etc.)
    uint256 tokenId,        // Associated NFT/token ID
    string memory hash      // IPFS hash of completion proof
) external

// Close contract after all steps complete
function closeContract(
    uint256 contractId,
    string memory finalHash  // Final aggregated hash
) external

// Set counterparty for legacy negotiation
function setCounterparty(
    uint256 contractId,
    address counterparty
) external
```

## Events

```solidity
event ContractOpened(uint256 indexed contractId, address indexed issuer, string metadataHash);
event StepCompleted(uint256 indexed contractId, string indexed category, uint256 indexed tokenId, string hash);
event ContractClosed(uint256 indexed contractId, string finalHash);
```

## Installation

```bash
# Install dependencies
npm install

# Compile contracts
npm run compile

# Run tests
npm test

# Run tests with gas reporting
npm run test:gas

# Run coverage
npm run test:coverage
```

## Testing

Comprehensive test suite covering:

- ✅ Contract creation and validation
- ✅ Step completion with division categories
- ✅ Cannot close contract until all required categories complete
- ✅ Correct events emitted for all operations
- ✅ Legacy negotiation path (manual counterparty designation)
- ✅ Step hash immutability (cannot overwrite once submitted)
- ✅ Access control and permissions
- ✅ Category management and validation

```bash
# Run all tests
npm test

# Run specific test file
npx hardhat test test/SupplyChainChain.test.js

# Run with gas reporting
REPORT_GAS=true npm test
```

## Deployment

### Local Development

```bash
# Start local node
npm run node

# Deploy to local network
npm run deploy:local
```

### Testnets

```bash
# Deploy to Sepolia
npm run deploy:sepolia

# Deploy to Polygon Mumbai
npm run deploy:mumbai
```

### Environment Variables

Create `.env` file:

```env
# Private key for deployment
PRIVATE_KEY=your_private_key_here

# RPC URLs
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/your-project-id
POLYGON_RPC_URL=https://polygon-rpc.com/
MUMBAI_RPC_URL=https://rpc-mumbai.maticvigil.com/

# API Keys for verification
ETHERSCAN_API_KEY=your_etherscan_api_key
POLYGONSCAN_API_KEY=your_polygonscan_api_key
COINMARKETCAP_API_KEY=your_coinmarketcap_api_key
```

## Usage Example

```javascript
// Create supply chain contract
const tx1 = await contract.openContract(
  "QmCoffeeSupplyMetadata",  // IPFS metadata hash
  ["Forge", "Atlas", "Ledger", "Aegis"], // Required divisions
  ethers.ZeroAddress  // Open to anyone
);

// Complete Forge step (manufacturing)
const tx2 = await contract.connect(manufacturer).completeStep(
  1,  // contractId
  "Forge",  // division category
  101,  // tokenId
  "QmManufacturingComplete"  // completion proof hash
);

// Complete Atlas step (logistics)
const tx3 = await contract.connect(logistics).completeStep(
  1,  // contractId
  "Atlas",  // division category
  102,  // tokenId
  "QmLogisticsComplete"  // completion proof hash
);

// Complete remaining steps (Ledger, Aegis)...
await contract.completeStep(1, "Ledger", 103, "QmLedgerComplete");
await contract.completeStep(1, "Aegis", 104, "QmAegisComplete");

// Close contract with final aggregated hash
const tx4 = await contract.closeContract(
  1,  // contractId
  "QmFinalAggregatedHash"  // final proof
);
```

## Security Considerations

- **Access Control**: Only contract issuers can close contracts and manage counterparties
- **Step Validation**: Only required categories can be completed for each contract
- **Hash Immutability**: Step completion hashes cannot be overwritten once submitted
- **Authorization**: Steps can be completed by issuer, designated counterparty, or anyone if no counterparty set
- **Category Validation**: All division categories must be valid and pre-approved

## Gas Optimization

- Optimized for Ethereum mainnet deployment
- Uses Hardhat with 200 optimization runs
- Efficient storage patterns and minimal external calls

## Integration

This contract integrates with:
- **IPFS**: For storing contract metadata and step completion proofs off-chain
- **Event Indexing**: For building user interfaces and analytics dashboards
- **Division Systems**: Maps to Continuum_Overworld division structure (Forge, Atlas, Ledger, etc.)
- **NFT/Token Systems**: Associates completion proofs with token IDs for verification

## Version

**v0.1.0** - Initial implementation with core step aggregation and completion tracking

## License

MIT License - See LICENSE file for details