import express from "express";
import {
  registerSensor,
  getAllSensors,
  getSensorById,
  deleteSensor,
} from "../controller/hyperGraphDevice.js";

const router = express.Router();
router.post("/", registerSensor);
router.get("/", getAllSensors);
router.get("/:id", getSensorById);
router.delete("/:id", deleteSensor);

export default router;