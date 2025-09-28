import axios from "axios";

const BACKEND_URL = "http://localhost:3001/api/sensor";

// Simulated device MAC addresses
const devices = [
  "02c:cf:67:c5:6b:63"
];

// Function to send random sensor data
async function sendSensorData(deviceId) {
  const data = {
    deviceId,
    timestamp: new Date().toISOString(),
    decibel: (Math.random() * 40 + 60).toFixed(2) // random 60–100 dB
  };

  try {
    const res = await axios.post(BACKEND_URL, data);
    console.log(`📡 Sent from ${deviceId}:`, res.data);
  } catch (err) {
    console.error(`❌ Error sending from ${deviceId}:`, err.message);
  }
}

// Stream every 5s per device
devices.forEach((deviceId) => {
  setInterval(() => sendSensorData(deviceId), 5000);
});

console.log("🚀 Streaming started. Sending fake sensor data every 5s per device...");
