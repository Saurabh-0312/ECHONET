// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {BasicHook} from "./BasicHook.sol";
import {Hooks} from "lib/v4-core/src/libraries/Hooks.sol";

contract HookFactory {
    /**
     * @notice Deploys the BasicHook using CREATE2 with a mined salt.
     * @return hook The address of the newly deployed hook.
     */
    // Deploy the BasicHook and forward the required constructor argument (main contract address)
    function deploy(address mainContractAddress) external returns (BasicHook hook) {
        // Mine for a valid salt that produces a hook address with correct flags
        bytes32 salt = mineValidSalt(mainContractAddress);

        // Deploy the hook using the mined salt and the required constructor argument
        hook = new BasicHook{salt: salt}(mainContractAddress);
    }

    /**
     * @notice Mines for a salt that produces a valid hook address.
     * @return salt The salt that produces a valid hook address.
     */
    function mineValidSalt(address mainContractAddress) internal view returns (bytes32 salt) {
        // Get the required hook flags from BasicHook
        uint160 flags = uint160(
            Hooks.BEFORE_INITIALIZE_FLAG | Hooks.AFTER_INITIALIZE_FLAG | Hooks.BEFORE_ADD_LIQUIDITY_FLAG
                | Hooks.AFTER_ADD_LIQUIDITY_FLAG | Hooks.BEFORE_REMOVE_LIQUIDITY_FLAG | Hooks.AFTER_REMOVE_LIQUIDITY_FLAG
                | Hooks.BEFORE_SWAP_FLAG | Hooks.AFTER_SWAP_FLAG | Hooks.BEFORE_DONATE_FLAG | Hooks.AFTER_DONATE_FLAG
        );

        // Try different salts until we find one that produces a valid address
        // Reduced from 100,000 to 1,000 to avoid gas limit issues
        for (uint256 i = 0; i < 10000; i++) {
            bytes32 testSalt = bytes32(i);
            address predictedAddress = computeAddress(testSalt, mainContractAddress);

            // Check if the address has the required flags
            if ((uint160(predictedAddress) & flags) == flags) {
                return testSalt;
            }
        }

        // If no valid salt found, revert
        revert("No valid salt found");
    }

    /**
     * @notice Computes the CREATE2 address for BasicHook.
     * @param salt The salt to use for CREATE2.
     * @return The computed address.
     */
    function computeAddress(bytes32 salt, address mainContractAddress) internal view returns (address) {
        // Include the constructor argument encoding in the bytecode hash so the predicted CREATE2 address matches the actual deployment
        bytes memory creation = abi.encodePacked(type(BasicHook).creationCode, abi.encode(mainContractAddress));
        bytes32 bytecodeHash = keccak256(creation);

        return address(uint160(uint256(keccak256(abi.encodePacked(bytes1(0xff), address(this), salt, bytecodeHash)))));
    }
}
