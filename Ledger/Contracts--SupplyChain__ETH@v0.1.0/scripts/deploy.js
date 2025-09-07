const { ethers } = require("hardhat");

/**
 * Deployment script for SupplyChainRFP contract
 * Ledger/Contracts--SupplyChain__ETH@v0.1.0
 */
async function main() {
  console.log("🚀 Deploying SupplyChainRFP contract...");
  
  // Get the deployer account
  const [deployer] = await ethers.getSigners();
  console.log("Deploying from account:", deployer.address);
  
  // Get account balance
  const balance = await ethers.provider.getBalance(deployer.address);
  console.log("Account balance:", ethers.formatEther(balance), "ETH");
  
  // Deploy the contract
  const SupplyChainRFP = await ethers.getContractFactory("SupplyChainRFP");
  const supplyChainRFP = await SupplyChainRFP.deploy();
  
  await supplyChainRFP.waitForDeployment();
  const contractAddress = await supplyChainRFP.getAddress();
  
  console.log("✅ SupplyChainRFP deployed to:", contractAddress);
  
  // Verify deployment
  const nextRfpId = await supplyChainRFP.nextRfpId();
  console.log("Initial nextRfpId:", nextRfpId.toString());
  
  // Save deployment info
  const deploymentInfo = {
    network: hre.network.name,
    contractAddress: contractAddress,
    deployer: deployer.address,
    deploymentTime: new Date().toISOString(),
    blockNumber: await ethers.provider.getBlockNumber(),
    gasUsed: "TBD", // Would need to capture from deployment transaction
  };
  
  console.log("\n📊 Deployment Summary:");
  console.log("Network:", deploymentInfo.network);
  console.log("Contract Address:", deploymentInfo.contractAddress);
  console.log("Deployer:", deploymentInfo.deployer);
  console.log("Block Number:", deploymentInfo.blockNumber);
  console.log("Deployment Time:", deploymentInfo.deploymentTime);
  
  // Create a sample RFP for testing
  if (hre.network.name === "localhost" || hre.network.name === "hardhat") {
    console.log("\n🧪 Creating sample RFP for testing...");
    
    const tx = await supplyChainRFP.createRFP(
      "Sample Coffee Bean RFP",
      "QmSampleHash123456789",
      "https://ipfs.io/ipfs/QmSampleHash123456789",
      3600, // 1 hour bidding
      1800  // 30 min selection
    );
    
    const receipt = await tx.wait();
    console.log("Sample RFP created in transaction:", receipt.hash);
    
    const rfp = await supplyChainRFP.getRFP(1);
    console.log("Sample RFP title:", rfp.title);
    console.log("Sample RFP ID:", rfp.id.toString());
  }
  
  console.log("\n🎉 Deployment complete!");
  
  if (hre.network.name !== "localhost" && hre.network.name !== "hardhat") {
    console.log("\n📝 To verify the contract, run:");
    console.log(`npx hardhat verify --network ${hre.network.name} ${contractAddress}`);
  }
}

// Handle deployment errors
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Deployment failed:");
    console.error(error);
    process.exit(1);
  });