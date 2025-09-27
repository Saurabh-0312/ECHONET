// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "lib/openzeppelin-contracts/contracts/access/Ownable.sol";

/**
 * @title SimplifiedMainContract
 * @author EchoNet Team
 * @notice This is a simplified version of the MainContract for demonstration purposes on the Sepolia testnet.
 * It allows the contract owner to manually set contribution scores for any address,
 * which is then read by the ContributionFeeHook to determine trading fees in a Uniswap v4 pool.
 */
contract SimplifiedMainContract is Ownable {
    /**
     * @notice Stores the contribution score for each user address.
     * The hook contract will read from this mapping.
     */
    mapping(address => uint256) public contributionScores;

    event ScoreUpdated(address indexed user, uint256 newScore);

    constructor() Ownable(msg.sender) {}

    /**
     * @notice Allows the contract owner to set the contribution score for a specific user.
     * This is the primary function for demonstrating the dynamic fee hook.
     * @param user The address of the user whose score is being set.
     * @param score The new contribution score for the user.
     */
    function setContributionScore(address user, uint256 score) external onlyOwner {
        contributionScores[user] = score;
        emit ScoreUpdated(user, score);
    }

    /**
     * @notice A public view function to easily check the contribution score of any user.
     * @param user The address of the user to query.
     * @return The current contribution score.
     */
    function getContributionScore(address user) external view returns (uint256) {
        return contributionScores[user];
    }
}
