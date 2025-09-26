// routes/worldcoinRoutes.js
import express from "express";
import { verifyWorldcoin } from "../controller/wordCoinController.js";

const router = express.Router();

// POST /api/worldcoin/verify
router.post("/verify", verifyWorldcoin);

export default router;