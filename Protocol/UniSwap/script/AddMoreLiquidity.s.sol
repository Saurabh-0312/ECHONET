// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Script} from "forge-std/Script.sol";
import {console} from "forge-std/console.sol";

// Uniswap V4 Core
import {IPoolManager} from "lib/v4-core/src/interfaces/IPoolManager.sol";
import {PoolKey} from "lib/v4-core/src/types/PoolKey.sol";
import {Currency, CurrencyLibrary} from "lib/v4-core/src/types/Currency.sol";
import {BalanceDelta} from "lib/v4-core/src/types/BalanceDelta.sol";

// Our Contracts
import {Token} from "../src/Token.sol";
import {BasicHook} from "../src/BasicHook.sol";

// Test Router for Liquidity
import {PoolModifyLiquidityTest} from "lib/v4-core/src/test/PoolModifyLiquidityTest.sol";

contract AddMoreLiquidity is Script {
    IPoolManager public constant POOL_MANAGER = IPoolManager(0xE03A1074c86CFeDd5C142C4F04F1a1536e203543);

    // --- Your Deployed Contract Addresses ---
    Token public constant TOKEN_A = Token(0xc1d7ea2A94A0bdC8594cA2C485aB93e46e2a593e);
    Token public constant TOKEN_B = Token(0x1c2e5A8dB0e60eD3747b798e74e8940e4ce4de13);
    BasicHook public constant HOOK = BasicHook(0x3299D60A4fF3c4A7c554BB929CF59ee9d22b3ffe);

    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        address deployerAddress = vm.addr(deployerPrivateKey);

        vm.startBroadcast(deployerPrivateKey);

        // --- Step 1: Deploy Liquidity Router ---
        console.log("Deploying liquidity router...");
        PoolModifyLiquidityTest liquidityRouter = new PoolModifyLiquidityTest(POOL_MANAGER); //q i have my owne louquiodty router do not deploy again and agian
        console.log("Liquidity Router deployed at:", address(liquidityRouter));

        // --- Step 2: Approve Tokens ---
        console.log("Approving tokens for router...");
        TOKEN_A.approve(address(liquidityRouter), type(uint256).max);
        TOKEN_B.approve(address(liquidityRouter), type(uint256).max);

        // --- Step 3: Add Liquidity ---
        (address token0, address token1) = address(TOKEN_A) < address(TOKEN_B)
            ? (address(TOKEN_A), address(TOKEN_B))
            : (address(TOKEN_B), address(TOKEN_A));

        PoolKey memory key = PoolKey({
            currency0: Currency.wrap(token0),
            currency1: Currency.wrap(token1),
            fee: 3000,
            tickSpacing: 60,
            hooks: HOOK
        });

        // ***** THE FIX: Increased liquidityDelta to target ~10,000 tokens *****
        int256 liquidityToAdd = int256(2.5e23);

        console.log("Adding a large amount of liquidity to the pool...");
        IPoolManager.ModifyLiquidityParams memory params = IPoolManager.ModifyLiquidityParams({
            tickLower: -600,
            tickUpper: 600,
            liquidityDelta: liquidityToAdd,
            salt: 0
        });
        BalanceDelta delta = liquidityRouter.modifyLiquidity(key, params, "");
        console.log("Liquidity added successfully.");
        console.log("Tokens taken from your wallet (Token A):", delta.amount0());
        console.log("Tokens taken from your wallet (Token B):", delta.amount1());

        vm.stopBroadcast();
    }
}
