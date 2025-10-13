EchoNet - Hedera deployment

This folder contains a minimal Hardhat project and a Solidity contract adapted for deployment to Hedera using hethers.

Getting started:

1. Install dependencies:

   npm install

2. Create a `.env` file based on `.env.example` and set your Hedera operator private key and RPC URL.

3. Compile:

   npm run compile

4. Deploy to Hedera testnet (ensure env vars are set):

   npm run deploy

Files:
- `src/EchoNetToken.sol` - ERC20 token with owner-only mint/burn.
- `scripts/deploy.js` - deployment script using Hardhat.
- `hardhat.config.js` - Hardhat configuration.
