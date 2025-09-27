// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Script} from "forge-std/Script.sol";
import {console} from "forge-std/console.sol";

// Uniswap V4 Core
import {IPoolManager} from "lib/v4-core/src/interfaces/IPoolManager.sol";
import {PoolKey} from "lib/v4-core/src/types/PoolKey.sol";
import {PoolId, PoolIdLibrary} from "lib/v4-core/src/types/PoolId.sol";
import {Currency, CurrencyLibrary} from "lib/v4-core/src/types/Currency.sol";
import {BalanceDelta} from "lib/v4-core/src/types/BalanceDelta.sol";
// We no longer need to import TickMath

// Our Contracts
import {Token} from "../src/Token.sol";
import {BasicHook} from "../src/BasicHook.sol";

// Test Routers
import {PoolModifyLiquidityTest} from "lib/v4-core/src/test/PoolModifyLiquidityTest.sol";
import {PoolSwapTest} from "lib/v4-core/src/test/PoolSwapTest.sol";

contract PoolInteraction is Script {
    IPoolManager public constant POOL_MANAGER = IPoolManager(0xE03A1074c86CFeDd5C142C4F04F1a1536e203543);

    // --- Your Deployed Contract Addresses ---
    Token public constant TOKEN_A = Token(0xc1d7ea2A94A0bdC8594cA2C485aB93e46e2a593e);
    Token public constant TOKEN_B = Token(0x1c2e5A8dB0e60eD3747b798e74e8940e4ce4de13);
    BasicHook public constant HOOK = BasicHook(0x3299D60A4fF3c4A7c554BB929CF59ee9d22b3ffe);
    bytes32 public constant POOL_ID = 0x3705883abe58aeb96aa8ba232a80fbc7a4b2e770dc43f8ec8f29f271d058fa9f;

    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        address deployerAddress = vm.addr(deployerPrivateKey);

        vm.startBroadcast(deployerPrivateKey);

        console.log("Deploying test routers...");
        PoolModifyLiquidityTest liquidityRouter = new PoolModifyLiquidityTest(POOL_MANAGER);
        PoolSwapTest swapRouter = new PoolSwapTest(POOL_MANAGER);
        console.log("Liquidity Router deployed at:", address(liquidityRouter));
        console.log("Swap Router deployed at:", address(swapRouter));

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

        PoolId poolId = PoolIdLibrary.toId(key);
        require(PoolId.unwrap(poolId) == POOL_ID, "Pool ID mismatch");
        console.log("Pool ID verified successfully!");

        console.log("Approving tokens for routers...");
        TOKEN_A.approve(address(liquidityRouter), type(uint256).max);
        TOKEN_B.approve(address(liquidityRouter), type(uint256).max);
        TOKEN_A.approve(address(swapRouter), type(uint256).max);
        TOKEN_B.approve(address(swapRouter), type(uint256).max);

        console.log("Adding liquidity to pool...");
        IPoolManager.ModifyLiquidityParams memory params =
            IPoolManager.ModifyLiquidityParams({tickLower: -600, tickUpper: 600, liquidityDelta: 1e18, salt: 0});
        BalanceDelta delta = liquidityRouter.modifyLiquidity(key, params, "");
        console.log("Liquidity added successfully");
        console.log("Tokens taken from wallet (Amount0):", delta.amount0());
        console.log("Tokens taken from wallet (Amount1):", delta.amount1());

        console.log("Performing a swap (selling Token A for Token B)...");
        IPoolManager.SwapParams memory swapParams = IPoolManager.SwapParams({
            zeroForOne: true,
            amountSpecified: 1e16,
            // ***** THE FIX: Use the literal value of MIN_SQRT_RATIO *****
            sqrtPriceLimitX96: 4295128739 + 1
        });

        BalanceDelta swapDelta =
            swapRouter.swap(key, swapParams, PoolSwapTest.TestSettings({settleUsingBurn: false, takeClaims: false}), "");
        console.log("Swap completed successfully");
        console.log("Swap delta amount0:", swapDelta.amount0());
        console.log("Swap delta amount1:", swapDelta.amount1());

        console.log("Final Token A balance:", TOKEN_A.balanceOf(deployerAddress));
        console.log("Final Token B balance:", TOKEN_B.balanceOf(deployerAddress));

        vm.stopBroadcast();
    }
}
