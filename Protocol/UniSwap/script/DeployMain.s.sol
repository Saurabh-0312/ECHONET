// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Script} from "forge-std/Script.sol";
import {console} from "forge-std/console.sol";

import {SimplifiedMainContract} from "../src/SimplifiedMainContract.sol";

contract DeployMain is Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        vm.startBroadcast(deployerPrivateKey);

        console.log("Deploying SimplifiedMainContract...");
        SimplifiedMainContract main = new SimplifiedMainContract();
        console.log("SimplifiedMainContract deployed at:", address(main));

        vm.stopBroadcast();
    }
}
