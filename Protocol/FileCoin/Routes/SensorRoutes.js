import express from "express";
import { updateSensorData,getSensorData } from "../Controller/SensorController.js";

const router = express.Router();

// POST route: collect sensor data
router.post("/", updateSensorData);
router.get("/:cid",getSensorData);


export default router;