// Minimal test server to verify payment middleware is working
import express from "express";
import { paymentMiddleware } from "x402-express";

const app = express();

// Simple static payment recipient for testing
const getPayToAddress = async (req) => {
  console.log("🔍 getPayToAddress called!");
  return "0x26EFd260dbE98A8f7f44555b29079d93698119be"; // Static test address
};

console.log("Setting up payment middleware...");

app.use(
  paymentMiddleware(
    getPayToAddress,
    {
      "/test": {
        price: "$0.01",
        network: "amoy",
        token: "0x8B0180f2101c8260d49339abfEe87927412494B4",
        config: {
          description: "Test payment",
        },
      },
    },
    {
      url: "https://x402.polygon.technology/",
    }
  )
);

app.get("/test", (req, res) => {
  console.log("✅ Protected endpoint reached!");
  res.json({ message: "Payment successful!" });
});

app.listen(3001, () => {
  console.log("Test server running on http://localhost:3001");
});
