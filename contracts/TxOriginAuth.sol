// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/// @title PhishableWallet
/// @notice INTENTIONALLY VULNERABLE — for security audit demonstration purposes only.
/// @dev Uses tx.origin for authorization instead of msg.sender. An attacker can
///      trick the owner into calling a malicious contract, which then calls this
///      contract's transfer() — tx.origin still equals the real owner, bypassing auth.
contract PhishableWallet {
    address public owner;

    constructor() {
        owner = tx.origin;
    }

    /// @dev VULNERABLE: tx.origin can be manipulated via a phishing contract
    modifier onlyOwner() {
        require(tx.origin == owner, "Not owner");
        _;
    }

    function transfer(address payable to, uint256 amount) external onlyOwner {
        to.transfer(amount);
    }

    receive() external payable {}
}
