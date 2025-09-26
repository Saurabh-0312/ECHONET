import express from 'express';
import { getSensorData, bufferSensorData } from '../controller/sensorController.js';

const router = express.Router();

// Buffer sensor data
router.post('/sensor', bufferSensorData);
// Retrieve sensor data by PieceCID
router.get('/sensor/:cid', getSensorData);

export default router;
