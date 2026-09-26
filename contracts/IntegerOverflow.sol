// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/// @title UncheckedToken
/// @notice INTENTIONALLY VULNERABLE — for security audit demonstration purposes only.
/// @dev Uses an `unchecked` block for balance arithmetic, disabling Solidity 0.8's
///      built-in overflow/underflow protection. A malicious transfer amount can
///      underflow a balance to a huge number.
contract UncheckedToken {
    mapping(address => uint256) public balances;

    function mint(address to, uint256 amount) external {
        balances[to] += amount;
    }

    /// @dev VULNERABLE: unchecked block removes overflow/underflow protection
    function transfer(address to, uint256 amount) external {
        unchecked {
            require(balances[msg.sender] >= amount, "Insufficient balance");
            balances[msg.sender] -= amount;
            balances[to] += amount; // can silently overflow if `to` balance is near max uint256
        }
    }
}
