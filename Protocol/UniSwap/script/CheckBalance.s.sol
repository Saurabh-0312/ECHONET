// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Script} from "forge-std/Script.sol";
import {console} from "forge-std/console.sol";

// Your Token contract
import {Token} from "../src/Token.sol";

contract CheckPoolBalance is Script {
    // Address of the Sepolia PoolManager
    address public constant POOL_MANAGER_ADDRESS = 0xE03A1074c86CFeDd5C142C4F04F1a1536e203543;

    // Your deployed token addresses
    Token public constant TOKEN_A = Token(0x75F3DD83b1eF86C381F3CA8BBe3515fa68252526);
    Token public constant TOKEN_B = Token(0x1fF1A03729203435BAE7a5B42583493Ee5b4682d);

    function run() external view {
        // Get the raw balance of each token held by the PoolManager
        uint256 balanceA = TOKEN_A.balanceOf(POOL_MANAGER_ADDRESS);
        uint256 balanceB = TOKEN_B.balanceOf(POOL_MANAGER_ADDRESS);

        console.log("--- Pool Balances ---");
        console.log("Raw Token A Balance:", balanceA);
        console.log("Raw Token B Balance:", balanceB);

        // Optional: Log the formatted balance (human-readable)
        console.log("\n--- Formatted Balances (18 Decimals) ---");
        console.log("Pool Balance (Token A):", balanceA / 1e18);
        console.log("Pool Balance (Token B):", balanceB / 1e18);
    }
}
