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
  origin: '*',
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true
}));

// Trust proxy for domain setup
app.set('trust proxy', true);

export const synapse = await Synapse.create({
    privateKey: process.env.PROVIDER_PRIVATE_KEY, // replace with your private key
    rpcURL: RPC_URLS.calibration.websocket, // testnet
});

const PORT = process.env.PORT || 3001;

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
