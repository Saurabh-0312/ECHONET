// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "lib/openzeppelin-contracts/contracts/token/ERC20/IERC20.sol";
import "lib/openzeppelin-contracts/contracts/utils/ReentrancyGuard.sol";

/**
 * @title IEchoToken
 * @dev Interface for the EchoToken contract, extending IERC20 with a mint function.
 * This contract (MainContract) needs to have the MINTER_ROLE in the EchoToken contract.
 */
interface IEchoToken is IERC20 {
    function mint(address to, uint256 amount) external;
}

contract MainContract is ReentrancyGuard {
    // --- State Variables ---

    IEchoToken public immutable echoToken;
    uint256 public immutable stakeAmount;
    address public owner;

    struct Sensor {
        address deviceOwner;
        bool isVerified;
        string deviceId;
    }

    // Struct to store each reading
    struct Reading {
        string ipfsCID;
        uint256 timestamp;
    }

    mapping(address => Sensor) public sensors;
    mapping(address => uint256) public stakes;

    // Mapping to ensure deviceId is unique
    mapping(string => bool) private usedDeviceIds;
    // Mapping from deviceId to the owner's address
    mapping(string => address) public deviceIdToOwner;

    // Mapping from deviceId to an array of reading entries
    mapping(string => Reading[]) public deviceReadings;

    // --- NEW: Added for Uniswap v4 Hook Integration ---
    /**
     * @notice A public mapping to track the contribution score of each sensor owner.
     * The Uniswap v4 hook will read this value to determine the swap fee.
     */
    mapping(address => uint256) public contributionScores;
    // --- END NEW ---

    // --- Events ---
    event SensorRegistered(address indexed owner, string deviceId, uint256 stakeAmount);
    event SensorDeregistered(address indexed owner);
    event ReadingSubmitted(address indexed owner, string ipfsCID, uint256 rewardAmount);
    event StakeSlashed(address indexed sensorAddress, uint256 userStake);
    event RewardMinted(address indexed to, uint256 amount);

    // --- Errors ---
    error AlreadyRegistered();
    error NotRegistered();
    error IncorrectStakeAmount();
    error DeviceIdAlreadyUsed();
    error TransferFailed();
    error OnlyOwner();
    error DeviceIdNotFound();

    // --- Functions ---

    constructor(address _echoTokenAddress, uint256 _stakeAmount) {
        echoToken = IEchoToken(_echoTokenAddress);
        stakeAmount = _stakeAmount * (10 ** 18);
        owner = msg.sender; // Initialize the contract owner
    }

    /**
     * @dev Registers a sensor. The user must first approve this contract
     * to spend `stakeAmount` of their ECHO tokens.
     */
    function registerSensor(string calldata _deviceId) external nonReentrant {
        if (sensors[msg.sender].deviceOwner != address(0)) revert AlreadyRegistered();
        if (usedDeviceIds[_deviceId]) revert DeviceIdAlreadyUsed();

        // TODO: Add Worldcoin verification logic here

        // Pull the stake amount from the user's wallet to this contract
        stakes[msg.sender] = stakeAmount;
        bool success = echoToken.transferFrom(msg.sender, address(this), stakeAmount);
        if (!success) revert TransferFailed();

        sensors[msg.sender] = Sensor({
            deviceOwner: msg.sender,
            isVerified: true, // Assume verified for now
            deviceId: _deviceId
        });

        // Mark the device ID as used and map it to the owner
        usedDeviceIds[_deviceId] = true;
        deviceIdToOwner[_deviceId] = msg.sender;

        emit SensorRegistered(msg.sender, _deviceId, stakeAmount);
    }

    /**
     * @notice Submits a new data reading for a specific device.
     * @dev The reading is stored on-chain, and the device owner is rewarded with ECHO tokens.
     * @param _deviceId The unique identifier of the device submitting the reading.
     * @param ipfsCID The IPFS CID pointing to the reading data stored off-chain.
     * Requirements:
     * - The device ID must be registered and associated with a sensor owner.
     * - The function rewards the sensor owner, not necessarily the caller.
     * Emits a {ReadingSubmitted} event with details of the submission.
     */
    function submitReading(string calldata _deviceId, string calldata ipfsCID) external {
        address sensorAddress = deviceIdToOwner[_deviceId];
        if (sensorAddress == address(0)) revert DeviceIdNotFound();

        uint256 rewardAmount = 1 * (10 ** 17); // 0.1 ECHO per reading

        // Store the reading in the device's reading array
        deviceReadings[_deviceId].push(Reading({ipfsCID: ipfsCID, timestamp: block.timestamp}));

        contributionScores[sensorAddress]++;

        // Mint new tokens to the sensor owner as a reward
        _mintToUser(sensorAddress, rewardAmount);

        emit ReadingSubmitted(sensorAddress, ipfsCID, rewardAmount);
    }

    /**
     * @dev Internal function to mint tokens to a specified user.
     * This function is called by `submitReading`.
     * NOTE: This contract's address must have the MINTER_ROLE on the EchoToken contract.
     * @param _to The address to mint the tokens to.
     * @param _amount The amount of tokens to mint.
     */
    function _mintToUser(address _to, uint256 _amount) internal {
        echoToken.mint(_to, _amount);
        emit RewardMinted(_to, _amount);
    }

    /**
     * @dev Allows a sensor owner to unstake their tokens and leave the network.
     */
    function unstakeAndDeregister() external nonReentrant {
        if (sensors[msg.sender].deviceOwner == address(0)) revert NotRegistered();

        uint256 userStake = stakes[msg.sender];
        string memory deviceId = sensors[msg.sender].deviceId;

        // Clear the user's sensor data and stake record
        delete sensors[msg.sender];
        delete stakes[msg.sender];
        delete deviceIdToOwner[deviceId];

        // Mark the device ID as available again if you want to allow reuse after deregistration
        usedDeviceIds[deviceId] = false;

        bool success = echoToken.transfer(msg.sender, userStake);
        if (!success) revert TransferFailed();

        emit SensorDeregistered(msg.sender);
    }

    /**
     * @dev Slash the stake of a sensor and send it to the contract owner.
     * Can only be called by the contract owner (server).
     * The server identifies a faulty device by its ID.
     */
    function slashStake(string calldata _deviceId) external nonReentrant {
        if (msg.sender != owner) revert OnlyOwner();

        address sensorAddress = deviceIdToOwner[_deviceId];
        if (sensorAddress == address(0)) revert DeviceIdNotFound();

        uint256 userStake = stakes[sensorAddress];

        // Delete sensor data
        delete sensors[sensorAddress];
        delete stakes[sensorAddress];
        delete deviceIdToOwner[_deviceId];
        usedDeviceIds[_deviceId] = false; // Or keep true to block reuse permanently

        // Transfer the stake to the contract owner
        bool success = echoToken.transfer(owner, userStake);
        if (!success) revert TransferFailed();

        emit StakeSlashed(sensorAddress, userStake);
    }
}
