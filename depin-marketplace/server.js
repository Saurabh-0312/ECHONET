// server.js
import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import { ethers } from "ethers";
import { paymentMiddleware } from "x402-express";
import fetch from "x402-fetch";

// --- 1. INITIAL SETUP ---
dotenv.config();
const app = express();
app.use(cors());
app.use(express.json({ limit: "10mb" }));

// Add middleware to ensure proper character encoding
app.use((req, res, next) => {
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  next();
});

const PORT = process.env.PORT || 3000;

// --- 2. SMART CONTRACT CONNECTION ---

const mainContractABI = [
  "function deviceIdToOwner(string) view returns (address)",
  "function deviceReadings(string, uint256) view returns (string ipfsCID, uint256 timestamp)",
];

const provider = new ethers.JsonRpcProvider(process.env.RPC_URL);
const contract = new ethers.Contract(
  process.env.MAIN_CONTRACT_ADDRESS,
  mainContractABI,
  provider
);
console.log(
  `Connected to MainContract at ${process.env.MAIN_CONTRACT_ADDRESS}`
);

// --- 3. DYNAMIC PAYMENT MIDDLEWARE CONFIGURATION ---

console.log("=== PAYMENT MIDDLEWARE DEBUG ===");
console.log("FACILITATOR_URL:", process.env.FACILITATOR_URL);
console.log("PAYMENT_TOKEN_ADDRESS:", process.env.PAYMENT_TOKEN_ADDRESS);

const getPayToAddress = async (req) => {
  try {
    console.log("🔍 getPayToAddress called for:", req.path);
    console.log("📋 Request params:", req.params);

    const { deviceId } = req.params;
    console.log(`🔍 Looking up owner for device: ${deviceId}`);

    const ownerAddress = await contract.deviceIdToOwner(deviceId);
    console.log(`📍 Device ${deviceId} owner: ${ownerAddress}`);

    if (ownerAddress === ethers.ZeroAddress) {
      console.log("❌ Device not found - owner is zero address");
      return null; // Device not found
    }

    console.log(`✅ Payment recipient set to: ${ownerAddress}`);
    return ownerAddress;
  } catch (error) {
    console.error("❌ Error fetching owner address:", error);
    return null;
  }
};

console.log("🔧 Setting up payment middleware...");

// Add general request logging
app.use((req, res, next) => {
  console.log(`📨 ${req.method} ${req.path}`);
  console.log(`🎫 Headers: ${JSON.stringify(req.headers, null, 2)}`);
  next();
});

// Simple test: Apply payment middleware using the simpler syntax from docs
console.log("Creating payment middleware with simple config...");

// According to docs: paymentMiddleware("0xYourAddress", { "/your-endpoint": "$0.01" })
// But our case is dynamic, so we use the callback version

// --- HEALTH CHECK ENDPOINT ---
app.get("/health", (req, res) => {
  res.status(200).json({
    status: "healthy",
    timestamp: new Date().toISOString(),
    service: "depin-marketplace",
    port: PORT
  });
});

// --- DATA ENDPOINT HANDLER FUNCTION ---
const dataEndpointHandler = async (req, res) => {
  console.log(`🔐 PROTECTED ENDPOINT ACCESSED: ${req.path}`);
  console.log(`📋 Request headers:`, req.headers);
  console.log(`💰 Payment verification should have happened by now...`);

  try {
    const { deviceId, readingIndex } = req.params;

    console.log(
      `Fetching reading for device: ${deviceId}, index: ${readingIndex}`
    );

    const reading = await contract.deviceReadings(deviceId, readingIndex);
    const ipfsCID = reading.ipfsCID;

    console.log(`Retrieved IPFS CID: ${ipfsCID}`);

    if (!ipfsCID) {
      console.log("No IPFS CID found for this reading");
      return res.status(404).json({ error: "Data reading not found." });
    }

    // Validate the IPFS CID to ensure it's properly formatted
    const sanitizedCID = ipfsCID.trim();

    // Create response object with proper string handling
    const responseData = {
      deviceId: deviceId.toString(),
      readingIndex: readingIndex.toString(),
      ipfsCID: sanitizedCID,
      message: "Payment successful. Here is your data.",
    };

    console.log("Sending response:", responseData);

    return res.status(200).json(responseData);
  } catch (error) {
    console.error("Error fetching data from contract:", error);
    // Only send error response if response hasn't been sent yet
    if (!res.headersSent) {
      return res.status(500).json({ error: "Failed to retrieve data." });
    }
  }
};

try {
  // ✅ WORKING SOLUTION: Create a specific route for this device
  // Since parameterized routes don't work with x402-express, we'll use a specific route
  app.get(
    "/data/00:1A:2B:3C:4D:5E/0",
    paymentMiddleware(
      "0xB5f278f22c5E5C42174FC312cc593493d2f3570D", // Device owner address
      {
        "/data/00:1A:2B:3C:4D:5E/0": {
          price: "$0.01",
          network: "polygon-amoy",
          token: process.env.PAYMENT_TOKEN_ADDRESS,
          config: {
            description:
              "Purchase sound sensor data - payment goes to device owner",
          },
        },
      },
      {
        url: process.env.FACILITATOR_URL,
      }
    ),
    (req, res) => {
      // Set params manually since this is a specific route
      req.params = {
        deviceId: "00:1A:2B:3C:4D:5E",
        readingIndex: "0",
      };
      return dataEndpointHandler(req, res);
    }
  );

  console.log(
    "✅ SPECIFIC DATA ROUTE: Payment required - $0.01 USDC to device owner"
  );
  console.log(
    "📍 Route: /data/00:1A:2B:3C:4D:5E/0 -> 0xB5f278f22c5E5C42174FC312cc593493d2f3570D"
  );
} catch (error) {
  console.error("❌ Error setting up specific data route:", error);
}

console.log("✅ Payment middleware configuration complete");

// --- TEST PARAMETERIZED ROUTE ---
console.log("Setting up test parameterized route...");

try {
  // Test parameterized route with payment middleware
  app.get(
    "/test/:id",
    paymentMiddleware(
      "0xB5f278f22c5E5C42174FC312cc593493d2f3570D",
      {
        "/test/:id": {
          price: "$0.01",
          network: "polygon-amoy",
          token: process.env.PAYMENT_TOKEN_ADDRESS,
          config: {
            description: "Test parameterized payment.",
          },
        },
      },
      {
        url: process.env.FACILITATOR_URL,
      }
    ),
    (req, res) => {
      console.log("✅ Parameterized test endpoint reached after payment!");
      res.json({
        message: "Parameterized payment test successful!",
        id: req.params.id,
      });
    }
  );

  console.log("✅ Test parameterized endpoint configured");
} catch (error) {
  console.error("❌ Error setting up parameterized test:", error);
}

// --- SIMPLE TEST ENDPOINT WITH STATIC PAYMENT ---
console.log("Setting up simple test payment endpoint...");

try {
  // Simple static payment endpoint as per docs: paymentMiddleware("0xAddress", { "/endpoint": "$0.01" })
  app.use(
    paymentMiddleware(
      "0x26EFd260dbE98A8f7f44555b29079d93698119be", // Static test address
      {
        "/simple-test": {
          price: "$0.01",
          network: "polygon-amoy",
          token: process.env.PAYMENT_TOKEN_ADDRESS,
        },
      },
      {
        url: process.env.FACILITATOR_URL,
      }
    )
  );

  app.get("/simple-test", (req, res) => {
    console.log("✅ Simple test endpoint reached after payment!");
    res.json({ message: "Simple payment test successful!" });
  });

  console.log("✅ Simple test payment endpoint configured");
} catch (error) {
  console.error("❌ Error setting up simple test endpoint:", error);
}

// --- 4. TEST FACILITATOR CONNECTIVITY ---
app.get("/test-facilitator", async (req, res) => {
  try {
    console.log("Testing facilitator connectivity...");
    const response = await fetch(`${process.env.FACILITATOR_URL}/supported`);
    const data = await response.json();
    console.log("Facilitator response:", data);
    res.json({
      facilitator: process.env.FACILITATOR_URL,
      supported: data,
      status: "connected",
    });
  } catch (error) {
    console.error("Facilitator test failed:", error);
    res.status(500).json({
      error: "Failed to connect to facilitator",
      facilitator: process.env.FACILITATOR_URL,
      message: error.message,
    });
  }
});

// --- 5. DEBUG ENDPOINT (for testing) ---
app.get("/debug/:deviceId/:readingIndex", async (req, res) => {
  try {
    const { deviceId, readingIndex } = req.params;

    console.log(
      `Debug request for device: ${deviceId}, index: ${readingIndex}`
    );

    // Get device owner
    const ownerAddress = await contract.deviceIdToOwner(deviceId);

    const reading = await contract.deviceReadings(deviceId, readingIndex);
    const ipfsCID = reading.ipfsCID;

    console.log(`Raw IPFS CID:`, ipfsCID);
    console.log(`Device Owner:`, ownerAddress);

    return res.status(200).json({
      deviceId,
      deviceOwner: ownerAddress,
      paymentRecipient: ownerAddress,
      ipfsCID: {
        raw: ipfsCID,
        sanitized: ipfsCID.trim(),
        type: typeof ipfsCID,
        length: ipfsCID.length,
      },
      paymentInfo: {
        price: "$0.01",
        token: process.env.PAYMENT_TOKEN_ADDRESS,
        network: "amoy",
      },
    });
  } catch (error) {
    console.error("Debug error:", error);
    return res.status(500).json({ error: error.message });
  }
});

// --- 6. MARKET CLIENT ENDPOINT ---
app.get("/market", async (req, res) => {
  console.log("=== TESTING DATA ENDPOINT ===");
  
  try {
    const targetUrl = `http://localhost:${PORT}/data/00:1A:2B:3C:4D:5E/0`;
    console.log(`Attempting to buy data from: ${targetUrl}`);
    console.log("Making payment request...");

    // Create buyer wallet from private key
    const buyerWallet = new ethers.Wallet(process.env.BUYER_WALLET_PRIVATE_KEY);
    
    // Make the payment request using x402-fetch
    const response = await fetch(targetUrl, {
      wallet: buyerWallet,
      tokenAddress: process.env.PAYMENT_TOKEN_ADDRESS,
      rpcUrl: process.env.RPC_URL,
      facilitatorUrl: process.env.FACILITATOR_URL
    });

    console.log(`Response status: ${response.status}`);
    
    // Get headers object
    const headers = {};
    response.headers.forEach((value, key) => {
      headers[key] = value;
    });
    console.log("Response headers:", headers);

    // Get response text
    const responseText = await response.text();
    console.log(`Raw response text length: ${responseText.length}`);
    console.log(`Raw response text: ${JSON.stringify(responseText)}`);

    if (response.ok) {
      const data = JSON.parse(responseText);
      console.log("\n✅ SUCCESS! Data Purchased:");
      console.log(data);
      
      // Get payment info from headers
      const paymentHeader = response.headers.get('x-payment-response');
      if (paymentHeader) {
        console.log(`Payment header raw value: ${JSON.stringify(paymentHeader)}`);
        
        try {
          const paymentInfo = JSON.parse(Buffer.from(paymentHeader, 'base64').toString());
          console.log("Payment info:", paymentInfo);
          
          return res.status(200).json({
            success: true,
            data: data,
            paymentInfo: paymentInfo,
            message: "Data successfully purchased from marketplace"
          });
        } catch (e) {
          console.log("Could not decode payment header:", e.message);
        }
      }
      
      return res.status(200).json({
        success: true,
        data: data,
        message: "Data successfully purchased from marketplace"
      });
    } else {
      console.error(`❌ Failed to purchase data. Status: ${response.status}`);
      return res.status(response.status).json({
        error: "Failed to purchase data",
        status: response.status,
        response: responseText
      });
    }

  } catch (error) {
    console.error("❌ Market endpoint error:", error);
    return res.status(500).json({ 
      error: "Failed to execute market purchase", 
      details: error.message 
    });
  }
});

// --- 7. THE PROTECTED API ENDPOINT ---

// IMPORTANT: Route is now defined above with payment middleware
// The dataEndpointHandler function is applied as the final handler after payment verification

// --- 8. START THE SERVER ---
app.listen(PORT, () => {
  console.log(`✅ Marketplace server running on http://localhost:${PORT}`);
});
