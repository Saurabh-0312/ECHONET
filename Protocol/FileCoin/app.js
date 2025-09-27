
import express from "express";
import bodyParser from "body-parser";
import { Synapse, RPC_URLS, TOKENS } from "@filoz/synapse-sdk";
import dotenv from "dotenv";
import cors from "cors";
import sensorRoutes from "./Routes/SensorRoutes.js"
import { ethers } from "ethers";

dotenv.config();
const app = express();
app.use(bodyParser.json());
app.use(cors());

const PORT = 3001;

console.log("🔑 Initializing Synapse SDK...");
const synapse = await Synapse.create({
  privateKey: process.env.PRIVATE_KEY, // replace with your private key
  rpcURL: RPC_URLS.calibration.websocket, // testnet
});
console.log("✅ Synapse initialized!");

const balance = await synapse.payments.balance(TOKENS.USDFC);
console.log("USDFC Balance:", balance.toString());

  //  const depositAmount = ethers.parseUnits("50", 18); // 50 USDFC
  // console.log("💰 Depositing", depositAmount.toString(), "USDFC...");

  // const depositTx = await synapse.payments.deposit(depositAmount, TOKENS.USDFC);
  // await depositTx.wait();
  // console.log("✅ Deposit confirmed! Hash:", depositTx.hash);

  // // -------------------------------------------------
  // // Step 2: Approve Warm Storage service
  // // -------------------------------------------------
  // console.log("🔎 Fetching Warm Storage contract address...");
  // const warmStorageAddress = await synapse.getWarmStorageAddress();
  // console.log("📍 Warm Storage Address:", warmStorageAddress);

  // console.log("📝 Approving Warm Storage for payment usage...");
  // const approveTx = await synapse.payments.approveService(
  //   warmStorageAddress,
  //   ethers.parseUnits("5", 18),    // Rate allowance: 5 USDFC/epoch
  //   ethers.parseUnits("500", 18),  // Lockup: 500 USDFC
  //   86400n                         // Max lockup = 30 days (in epochs)
  // );

  // await approveTx.wait();
  // console.log("✅ Service approved! Hash:", approveTx.hash);


app.use('/api/sensor',sensorRoutes);
export default synapse;


// ------------------------
app.listen(PORT, () => {
  console.log(`🚀 Backend running on http://localhost:${PORT}`);
});
