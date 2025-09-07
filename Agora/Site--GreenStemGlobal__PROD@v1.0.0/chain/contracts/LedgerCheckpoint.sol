// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract LedgerCheckpoint {
  event Checkpoint(bytes32 indexed kind, string ref, uint256 amount, string currency);

  function emitDeposit(string calldata ref, uint256 amount, string calldata currency) external {
    emit Checkpoint(keccak256("DEPOSIT"), ref, amount, currency);
  }
  
  function emitFx(string calldata ref, uint256 amount, string calldata currency) external {
    emit Checkpoint(keccak256("FX"), ref, amount, currency);
  }
  
  function emitTransferKE(string calldata ref, uint256 amount, string calldata currency) external {
    emit Checkpoint(keccak256("TRANSFER_KE"), ref, amount, currency);
  }
  
  function emitAllocation(string calldata ref, uint256 amount, string calldata currency) external {
    emit Checkpoint(keccak256("ALLOCATION"), ref, amount, currency);
  }
}