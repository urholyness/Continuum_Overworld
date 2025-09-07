// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// Aggregation/Chain Completion contract (no bidding)
contract SupplyChainChain {
  address public issuer;    // GSG division wallet
  address public aegis;     // admin for pause/emergency
  bool public paused;

  event ContractOpened(bytes32 indexed contractId, address indexed issuer, bytes32 metadataHash);
  event StepCompleted(bytes32 indexed contractId, string category, uint256 tokenId, bytes32 payloadHash);
  event ContractClosed(bytes32 indexed contractId, bytes32 finalHash);

  modifier onlyIssuer(){ require(msg.sender==issuer, "ONLY_ISSUER"); _; }
  modifier onlyAegis(){ require(msg.sender==aegis, "ONLY_AEGIS"); _; }
  modifier notPaused(){ require(!paused, "PAUSED"); _; }

  constructor(address _issuer, address _aegis){ issuer=_issuer; aegis=_aegis; }

  struct ChainReq { bool forge; bool atlas; bool ledger; bool aegis; }
  struct ChainState { bool forge; bool atlas; bool ledger; bool aegis; bool closed; }

  mapping(bytes32 => ChainReq)   public requiredSteps;   // contractId => requirements
  mapping(bytes32 => ChainState) public completedSteps;  // contractId => completions
  mapping(bytes32 => bool) public opened;

  function setPaused(bool on) external onlyAegis { paused=on; }

  function openContract(bytes32 contractId, bytes32 metadataHash, ChainReq calldata req) external onlyIssuer notPaused {
    require(!opened[contractId], "ALREADY_OPEN");
    opened[contractId]=true;
    requiredSteps[contractId]=req;
    emit ContractOpened(contractId, issuer, metadataHash);
  }

  function completeStep(bytes32 contractId, string calldata category, uint256 tokenId, bytes32 payloadHash) external onlyIssuer notPaused {
    require(opened[contractId], "NOT_OPEN");
    bytes32 cat = keccak256(bytes(category));
    if (cat==keccak256("Forge"))  completedSteps[contractId].forge = true;
    else if (cat==keccak256("Atlas"))  completedSteps[contractId].atlas = true;
    else if (cat==keccak256("Ledger")) completedSteps[contractId].ledger = true;
    else if (cat==keccak256("Aegis"))  completedSteps[contractId].aegis = true;
    else revert("UNKNOWN_CATEGORY");
    emit StepCompleted(contractId, category, tokenId, payloadHash);
  }

  function closeContract(bytes32 contractId, bytes32 finalHash) external onlyIssuer notPaused {
    require(opened[contractId], "NOT_OPEN");
    require(!completedSteps[contractId].closed, "ALREADY_CLOSED");
    ChainReq memory req = requiredSteps[contractId];
    ChainState memory st = completedSteps[contractId];
    require(!req.forge  || st.forge,  "FORGE_PENDING");
    require(!req.atlas  || st.atlas,  "ATLAS_PENDING");
    require(!req.ledger || st.ledger, "LEDGER_PENDING");
    require(!req.aegis  || st.aegis,  "AEGIS_PENDING");
    completedSteps[contractId].closed = true;
    emit ContractClosed(contractId, finalHash);
  }
}