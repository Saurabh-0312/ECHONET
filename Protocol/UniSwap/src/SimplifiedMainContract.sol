// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title SimplifiedMainContract
 * @author EchoNet Team
 * @notice Simplified version of MainContract for demo. No admin ownership — scores are publically settable.
 */
contract SimplifiedMainContract {
    /**
     * @notice Stores the contribution score for each user address.
     * The hook contract will read from this mapping.
     */
    mapping(address => uint256) public contributionScores;

    event ScoreUpdated(address indexed user, uint256 newScore);

    constructor() {}

    /**
     * @notice Allows the contract owner to set the contribution score for a specific user.
     * This is the primary function for demonstrating the dynamic fee hook.
     * @param user The address of the user whose score is being set.
     * @param score The new contribution score for the user.
     */
    function setContributionScore(address user, uint256 score) external {
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
