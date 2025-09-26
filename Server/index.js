import express from 'express';
import dotenv from 'dotenv';
import cors from 'cors';
import { Synapse, RPC_URLS, TOKENS } from "@filoz/synapse-sdk";

import worldcoinRoutes from './routes/wordCoinRoutes.js';
import ensRoutes from './routes/ensRoutes.js';
import stakeDataRoutes from './routes/stakeDataRoutes.js';
import CidRoutes from './routes/CidRoutes.js';
import sensorRoutes from './routes/sensorRoutes.js';
import hyperGraphSensorRoutes from './routes/hyperGraphSensor.js';

dotenv.config();

const app = express();
app.use(express.json());
app.use(cors({
  origin: [
    'http://localhost:3000',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'http://127.0.0.1:3000'
  ],
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

export const synapse = await Synapse.create({
    privateKey: "b41f796fa90a331fc1ba07b32d8009c61992222c80c74f475a1abcec911b3794", // replace with your private key
    rpcURL: RPC_URLS.calibration.websocket, // testnet
});

const PORT = process.env.PORT || 3000;

// Use worldcoinRoutes for all /api routes
app.use('/api/ens', ensRoutes);
app.use('/api', worldcoinRoutes);
app.use('/api', stakeDataRoutes);
app.use('/api', CidRoutes);
app.use('/api', sensorRoutes);
app.use('/api/hypergraph', hyperGraphSensorRoutes);

// Health and root endpoints for proxy/healthchecks
app.get('/healthz', (req, res) => {
  res.status(200).send('ok');
});

app.get('/', (req, res) => {
  res.status(200).json({ status: 'node backend running' });
});

app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});
