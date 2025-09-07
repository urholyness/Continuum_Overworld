const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("SupplyChainChain", () => {
  it("prevents close until required steps complete", async () => {
    const [issuer, aegis] = await ethers.getSigners();
    const F = await ethers.getContractFactory("SupplyChainChain");
    const c = await F.connect(issuer).deploy(issuer.address, aegis.address);
    const id = ethers.keccak256(ethers.toUtf8Bytes("GSG-DE-5T-BEANS-2025W34"));
    await c.openContract(id, ethers.ZeroHash, { forge:true, atlas:true, ledger:true, aegis:false });
    // Only Forge done
    await c.completeStep(id, "Forge", 1, ethers.ZeroHash);
    await expect(c.closeContract(id, ethers.ZeroHash)).to.be.revertedWith("ATLAS_PENDING");
    // Finish Atlas + Ledger
    await c.completeStep(id, "Atlas", 2, ethers.ZeroHash);
    await c.completeStep(id, "Ledger", 3, ethers.ZeroHash);
    await expect(c.closeContract(id, ethers.ZeroHash)).to.emit(c, "ContractClosed");
  });
});