// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/// @title UnprotectedVault
/// @notice INTENTIONALLY VULNERABLE — for security audit demonstration purposes only.
/// @dev Critical administrative functions have no access control modifier,
///      allowing ANY address to call them — not just the intended owner.
contract UnprotectedVault {
    address public owner;
    mapping(address => uint256) public balances;

    constructor() {
        owner = msg.sender;
    }

    /// @dev VULNERABLE: no onlyOwner check — anyone can reassign ownership
    function setOwner(address newOwner) external {
        owner = newOwner;
    }

    /// @dev VULNERABLE: no access control — anyone can drain any user's funds
    function emergencyWithdraw(address user, uint256 amount) external {
        balances[user] -= amount;
        payable(msg.sender).transfer(amount);
    }

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }
}
