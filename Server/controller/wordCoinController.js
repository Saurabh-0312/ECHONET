// controllers/worldcoinController.js
import { verifyCloudProof } from "@worldcoin/idkit";

const verifyWorldcoin = async (req, res) => {
    try {
        const { proof,verification_level,action } = req.body;

        // Make sure these are set in your .env
        const app_id = process.env.WORLDCOIN_APP_ID; // e.g. "app_staging_xxx"
        console.log("App ID:", app_id);
        console.log("Action:", action);
        const verifyRes = await verifyCloudProof(proof, 
            app_id,
            action);
        

        console.log("Worldcoin verification result:", verifyRes);

        if (verifyRes.success) {
            return res.json({
                success: true,
                message: "Verification successful",
                data: verifyRes,
            });
        } else {
            return res.status(200).json({
                success: false,
                message: "Verification failed",
                data: verifyRes,
            });
        }
    } catch (err) {
        console.error("Worldcoin verification error:", err);
        return res.status(500).json({
            success: false,
            message: "Server error",
            error: err.message,
        });
    }
};

export { verifyWorldcoin };

