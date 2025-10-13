require("dotenv").config();
require("@nomicfoundation/hardhat-toolbox");

module.exports = {
  solidity: {
    version: "0.8.20",
    settings: { optimizer: { enabled: true, runs: 200 } }
  },
  networks: {
    hedera: {
      url: process.env.HEDERA_RPC_URL || "https://testnet.hashio.io/api",
      // hethers will use the private key from env in the deploy script
    }
  }
};
