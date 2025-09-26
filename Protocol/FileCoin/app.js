
import express from "express";
import bodyParser from "body-parser";
import { Synapse, RPC_URLS, TOKENS } from "@filoz/synapse-sdk";
import dotenv from "dotenv";
import cors from "cors";
import sensorRoutes from "./Routes/SensorRoutes.js"


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

app.use('/api/sensor',sensorRoutes);
export default synapse;


// ------------------------
app.listen(PORT, () => {
  console.log(`🚀 Backend running on http://localhost:${PORT}`);
});
