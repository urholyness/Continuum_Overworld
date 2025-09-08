export const CONTRACT_ABI = [
  "event Checkpoint(bytes32 indexed kind, string ref, uint256 amount, string currency)",
  "function emitDeposit(string calldata ref, uint256 amount, string calldata currency) external",
  "function emitFx(string calldata ref, uint256 amount, string calldata currency) external", 
  "function emitTransferKE(string calldata ref, uint256 amount, string calldata currency) external",
  "function emitAllocation(string calldata ref, uint256 amount, string calldata currency) external"
];