// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Script, console} from "forge-std/Script.sol";
import {MainContract} from "../src/MainContract.sol";

contract DeployMain is Script {
    function run() external {
        // --- Configuration ---
        // Address of the already deployed EchoNetToken
        address echoTokenAddress;

        // Set the required stake amount for sensors (50 ECHO)
        uint256 stakeAmount = 50 * 1e18;

        // --- Deployment ---
        vm.startBroadcast();

        console.log("Deploying MainContract...");
        MainContract mainContract = new MainContract(echoTokenAddress, stakeAmount);
        console.log("MainContract deployed at:", address(mainContract));

        vm.stopBroadcast();
    }
}
