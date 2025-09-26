import express from "express";
import { uploadSensorData,getSensorData } from "../Controller/SensorController.js";

const router = express.Router();

// POST route: collect sensor data
router.post("/", uploadSensorData);
router.get("/:cid",getSensorData);


export default router;