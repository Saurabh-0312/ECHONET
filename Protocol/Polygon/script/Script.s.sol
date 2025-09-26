// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Script, console} from "forge-std/Script.sol";
import {EchoNetToken} from "../src/EchoNetToken.sol";
import {MainContract} from "../src/MainContract.sol";

contract Deploy is Script {
    function run() external {
        // --- Configuration ---
        // Set the required stake amount for sensors.
        // Let's say it's 50 ECHO tokens. (50 * 10^18)
        uint256 stakeAmount = 50;

        // --- Deployment Process ---
        vm.startBroadcast();

        // Step 1: Deploy the EchoNetToken contract.
        // The deployer's address (your wallet) will be the initial owner.
        console.log("Deploying EchoNetToken...");
        EchoNetToken echoToken = new EchoNetToken("EchoNetToken", "ECHO");
        console.log("EchoNetToken deployed at:", address(echoToken));

        // Step 2: Deploy the MainContract.
        // Pass the address of the token contract and the stake amount into the constructor.
        console.log("Deploying MainContract...");
        MainContract mainContract = new MainContract(address(echoToken), stakeAmount);
        console.log("MainContract deployed at:", address(mainContract));

        // Step 3: Transfer ownership of the EchoNetToken to the MainContract.
        // This is the most critical step for the system to work.
        // Now, only MainContract can mint new tokens.
        console.log("Transferring EchoNetToken ownership to MainContract...");
        echoToken.transferOwnership(address(mainContract));
        console.log("Ownership transferred successfully.");

        vm.stopBroadcast();
    }
}
