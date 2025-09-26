import express from "express";
import synapse from "../app";

const buffers = {};    // deviceId -> array of sensor data
const timers = {};     // deviceId -> flush timeout reference

const BATCH_INTERVAL = 1.5*60 * 1000; // 6 seconds (adjust to 2 min in prod)

// ------------------------
// Upload Queue (mutex style)
// ------------------------
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

    // Snapshot current buffer (but don’t clear yet)
    const batch = [...buffers[deviceId]];
    const encoded = new TextEncoder().encode(JSON.stringify(batch));
    console.log(`📤 Uploading batch for ${deviceId} with ${batch.length} records...`);

    const uploadResult = await synapse.storage.upload(encoded, {
      maxFee: "1000000000000000000", // 1 FIL
      gasLimit: 500000000
    });
    console.log("Upload Gas Params Used ✅");
    console.log(`✅ Stored batch PieceCID: ${uploadResult.pieceCid}`);

    // Only clear buffer on success
    buffers[deviceId].splice(0, batch.length);

    // Store in memory

    resolve(uploadResult.pieceCid);
  } catch (err) {
    console.error(`❌ Error uploading batch for ${deviceId}:`, err.message);

    // Requeue same deviceId (data is still in buffer, not lost)
    uploadQueue.push({ deviceId, resolve, reject });
    reject(err);
  } finally {
    isUploading = false;
    processQueue(); // continue with next queued device
  }
}

function enqueueUpload(deviceId) {
  return new Promise((resolve, reject) => {
    uploadQueue.push({ deviceId, resolve, reject });
    processQueue();
  });
}

// ------------------------
// Function to flush buffer
// ------------------------
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

const updateSensorData=async(req,res)=>{
     try {
    const sensorData = req.body;

    if (!sensorData.deviceId) {
      return res.status(400).json({ error: "deviceId is required" });
    }

    const deviceId = sensorData.deviceId;

    if (!buffers[deviceId]) buffers[deviceId] = [];

    // Push new data at end → ordering preserved
    buffers[deviceId].push(sensorData);
    console.log(`📥 Received data from ${deviceId}. Buffer size: ${buffers[deviceId].length}`);

    // Start timer if not already running
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

const getSensorData=async(req,res)=>{
    return {};
}
export {updateSensorData,getSensorData};