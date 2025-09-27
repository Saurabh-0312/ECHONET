import { ethers } from 'ethers';
import { synapse } from '../index.js';
import RegisterABI from '../ABI/RegisterDevice.json' with { type: 'json' };

// --- IMPORTANT CONFIGURATION ---
// These should be in a .env file for security. See setup instructions below.
const RPC_URL = "https://rpc-amoy.polygon.technology";
const YOUR_PRIVATE_KEY = process.env.YOUR_PRIVATE_KEY;

// This is the core function that was causing errors. It is now fixed.
async function notifySmartContract(pieceCid, deviceId) {
    if (!RPC_URL || !YOUR_PRIVATE_KEY) {
        console.error("❌ RPC_URL or YOUR_PRIVATE_KEY is not set in the .env file.");
        throw new Error("Missing RPC or Private Key configuration.");
    }

    try {
        const CONTRACT_ADDRESS = "0xc40dFe3F5d21743275db79586F2880415e77fc9a";
        const CONTRACT_ABI = RegisterABI.output.abi;

        // 1. Connect to the blockchain network using the RPC URL
        const provider = new ethers.JsonRpcProvider(RPC_URL);

        // 2. Create a signer wallet from your private key to send transactions
        const signer = new ethers.Wallet(YOUR_PRIVATE_KEY, provider);
        
        // 3. Create the contract instance with the signer
        const contract = new ethers.Contract(CONTRACT_ADDRESS, CONTRACT_ABI, signer);

        // console.log("Piece id",pieceCid);
        const formattedPieceId = pieceCid.toString();

        // const formattedPieceId = pieceCid.startsWith('CID(') && pieceCid.endsWith(')')
        //     ? pieceCid.slice(4, -1)
        //     : pieceCid;
        
        // console.log("Piece id",formattedPieceId);
        console.log(deviceId);
        // console.log()
        // console.log(`[CONTRACT] Submitting reading to contract for device: ${deviceId}`);
        
        const tx = await contract.submitReading(deviceId,formattedPieceId);
        
        // console.log(`[CONTRACT] Transaction sent. Waiting for confirmation... Tx hash: ${tx.hash}`);
        await tx.wait(); // Wait for the transaction to be mined
        
        console.log(`[CONTRACT] Notified contract successfully.`);
        return true;
    } catch (err) {
        console.error('[CONTRACT] Error notifying contract:', err.message);
        return false;
    }
}


// --- Your existing application logic (unchanged) ---

// In-memory storage
const buffers = {};    // deviceId -> array of sensor data
const timers = {};     // deviceId -> flush timeout reference
const BATCH_INTERVAL = 1 * 60 * 1000; // 0.1 min, corrected from 1.5
const uploadQueue = [];
let isUploading = false;

async function processQueue() {
    if (isUploading || uploadQueue.length === 0) return;

    isUploading = true;
    const { deviceId, resolve, reject } = uploadQueue.shift();

    try {
        if (!buffers[deviceId] || buffers[deviceId].length === 0) {
            resolve(null);
            return;
        }

        const batch = [...buffers[deviceId]];
        const encoded = new TextEncoder().encode(JSON.stringify(batch));
        console.log(`📤 Uploading batch for ${deviceId} with ${batch.length} records...`);

        const uploadResult = await synapse.storage.upload(encoded, {
            maxFee: "1000000000000000000", // 1 FIL
            gasLimit: 500000000
        });
        console.log("Upload Gas Params Used ✅");
        console.log(`✅ Stored batch PieceCID: ${uploadResult.pieceCid}`);

        await notifySmartContract(uploadResult.pieceCid, deviceId);

        buffers[deviceId].splice(0, batch.length);
        resolve(uploadResult.pieceCid);
    } catch (err) {
        console.error(`❌ Error uploading batch for ${deviceId}:`, err.message);
        uploadQueue.push({ deviceId, resolve, reject });
        reject(err);
    } finally {
        isUploading = false;
        processQueue();
    }
}

function enqueueUpload(deviceId) {
    return new Promise((resolve, reject) => {
        uploadQueue.push({ deviceId, resolve, reject });
        processQueue();
    });
}

async function flushBuffer(deviceId) {
  if (!buffers[deviceId] || buffers[deviceId].length === 0) return;

  try {
    return await enqueueUpload(deviceId);
  } catch (err) {
    console.error("❌ Upload failed via queue:", err.message);
  } finally {
    clearTimeout(timers[deviceId]);
    delete timers[deviceId];
  }
}

export const bufferSensorData = async (req, res) => {
    try {
        const sensorData = req.body;
        if (!sensorData.deviceId) {
            return res.status(400).json({ error: "deviceId is required" });
        }
        const deviceId = sensorData.deviceId;
        if (!buffers[deviceId]) buffers[deviceId] = [];
        buffers[deviceId].push(sensorData);
        console.log(`📥 Received data from ${deviceId}. Buffer size: ${buffers[deviceId].length}`);
        if (!timers[deviceId]) {
            timers[deviceId] = setTimeout(() => flushBuffer(deviceId), BATCH_INTERVAL);
            console.log(`⏳ Started batch timer for ${deviceId}`);
        }
        res.json({ message: "Data buffered" });
    } catch (err) {
        console.error("❌ Error buffering sensor data:", err.message);
        res.status(500).json({ error: err.message });
    }
};

export const getSensorData = async (req, res) => {
    try {
        const { cid } = req.params;
        if (!cid) return res.status(400).json({ error: "PieceCID is required" });
        console.log(`📥 Retrieving data for PieceCID: ${cid}...`);
        const retrieved = await synapse.storage.download(cid);
        console.log("✅ Data retrieved successfully.");
        
        const decoded = new TextDecoder().decode(retrieved);
        res.json({ pieceCid: cid, data: JSON.parse(decoded) });
    } catch (err) {
        console.error("❌ Error retrieving sensor data:", err.message);
        res.status(500).json({ error: err.message });
    }
};