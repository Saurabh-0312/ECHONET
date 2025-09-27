// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Script} from "forge-std/Script.sol";
import {console} from "forge-std/console.sol";

// Uniswap V4 Core
import {IPoolManager} from "lib/v4-core/src/interfaces/IPoolManager.sol";
import {PoolKey} from "lib/v4-core/src/types/PoolKey.sol";
import {PoolId, PoolIdLibrary} from "lib/v4-core/src/types/PoolId.sol";
import {Currency, CurrencyLibrary} from "lib/v4-core/src/types/Currency.sol";

// Our Contracts
import {Token} from "../src/Token.sol";
import {BasicHook} from "../src/BasicHook.sol";
import {HookFactory} from "../src/HookFactory.sol";
import {SimplifiedMainContract} from "../src/SimplifiedMainContract.sol";

contract Deploy is Script {
    IPoolManager public constant POOL_MANAGER = IPoolManager(0xE03A1074c86CFeDd5C142C4F04F1a1536e203543);
    
    // Paste your deployed SimplifiedMainContract address here
    address public constant MAIN_CONTRACT_ADDRESS = 0x0000000000000000000000000000000000000000;

    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        address deployerAddress = vm.addr(deployerPrivateKey);

        vm.startBroadcast(deployerPrivateKey);

        // --- 1. Deploy Tokens (No changes here) ---
        console.log("Deploying Token A...");
        Token tokenA = new Token("ECHOTOKEN", "ECHO");
        console.log("Token A deployed at:", address(tokenA));

        console.log("Deploying Token B...");
        Token tokenB = new Token("USDC", "USDC");
        console.log("Token B deployed at:", address(tokenB));

        tokenA.mint(deployerAddress, 1_000_000 * 10 ** 18);
        tokenB.mint(deployerAddress, 1_000_000 * 10 ** 18);

        // --- 2. Deploy HookFactory and Hook ---
        console.log("Deploying HookFactory...");
        HookFactory hookFactory = new HookFactory();
        console.log("HookFactory deployed at:", address(hookFactory));

        console.log("Using main contract address:", MAIN_CONTRACT_ADDRESS);
        console.log("Deploying BasicHook via Factory...");
        BasicHook hook = hookFactory.deploy(MAIN_CONTRACT_ADDRESS);
        console.log("Hook deployed at:", address(hook));

        // --- 3. Create and Initialize the Pool ---
        (address token0, address token1) =
            address(tokenA) < address(tokenB) ? (address(tokenA), address(tokenB)) : (address(tokenB), address(tokenA));

        PoolKey memory key = PoolKey({
            currency0: Currency.wrap(token0),
            currency1: Currency.wrap(token1),
            fee: 3000,
            tickSpacing: 60,
            hooks: hook
        });

        uint160 initialPrice = 79228162514264337593543950336; // 1:1 price

        console.log("Initializing Uniswap v4 Pool...");
        POOL_MANAGER.initialize(key, initialPrice);

        PoolId poolId = PoolIdLibrary.toId(key);
        console.log("Successfully created pool with ID:");
        console.logBytes32(PoolId.unwrap(poolId));
        console.log("Pool tokens are:", Currency.unwrap(key.currency0), "and", Currency.unwrap(key.currency1));

        // --- 5. Check if Pool is Deployed ---
        // This check does not change the core deploy logic
        (bool poolExists,) = address(POOL_MANAGER).staticcall(
            abi.encodeWithSignature("extsload(bytes32)", keccak256(abi.encodePacked(PoolId.unwrap(poolId), uint256(6))))
        );
        if (poolExists) {
            console.log("[Check] Pool is deployed and initialized.");
        } else {
            console.log("[Check] Pool is NOT deployed or not initialized!");
        }

        vm.stopBroadcast();
    }
}
