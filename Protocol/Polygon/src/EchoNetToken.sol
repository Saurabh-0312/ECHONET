// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "lib/openzeppelin-contracts/contracts/token/ERC20/ERC20.sol";
import "lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "lib/openzeppelin-contracts/contracts/access/Ownable.sol";

/// @title EchoNetToken - ERC20 token where only the owner can mint and burn tokens
contract EchoNetToken is ERC20, ERC20Burnable, Ownable {
    constructor(string memory name, string memory symbol) ERC20(name, symbol) Ownable(msg.sender) {
        // Optionally, mint initial tokens to owner
        // _mint(msg.sender, 1000 * 10 ** decimals());
    }

    /// @notice Mint tokens, only callable by owner
    /// @param to Address to receive tokens
    /// @param amount Amount of tokens to mint
    function mint(address to, uint256 amount) external {
        _mint(to, amount);
    }

    /// @notice Burn tokens from an account, only callable by owner
    /// @param from Address whose tokens will be burned
    /// @param amount Amount of tokens to burn
    function burnFromAccount(address from, uint256 amount) external {
        _burn(from, amount);
    }

    // Transfer functionality is already inherited from ERC20 and is available to all users.
}
