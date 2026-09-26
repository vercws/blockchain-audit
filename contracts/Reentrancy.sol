// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/// @title VulnerableBank
/// @notice INTENTIONALLY VULNERABLE — for security audit demonstration purposes only.
/// @dev Classic reentrancy pattern (as in the 2016 DAO hack): external call happens
///      BEFORE the internal state (balance) is updated, allowing a malicious
///      contract to recursively call withdraw() and drain funds.
contract VulnerableBank {
    mapping(address => uint256) public balances;

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    /// @dev VULNERABLE: external call before state update (violates checks-effects-interactions)
    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount, "Insufficient balance");

        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");

        balances[msg.sender] -= amount; // state updated AFTER external call
    }

    function getBalance(address user) external view returns (uint256) {
        return balances[user];
    }
}
