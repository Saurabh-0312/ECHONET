// client.js
import "dotenv/config";
import { wrapFetchWithPayment, decodeXPaymentResponse } from "x402-fetch";
import { createWalletClient, http } from "viem";
import { privateKeyToAccount } from "viem/accounts";
import { polygonAmoy } from "viem/chains";

// --- 1. SETUP BUYER'S WALLET ---
const account = privateKeyToAccount(process.env.BUYER_WALLET_PRIVATE_KEY);
const client = createWalletClient({
  account,
  chain: polygonAmoy,
  transport: http(),
});
console.log(`Client wallet address: ${client.account.address}`);

// --- 2. WRAP FETCH WITH X402 PAYMENT LOGIC ---
const fetchWithPayment = wrapFetchWithPayment(fetch, client);

// --- 3. THE MAIN FUNCTION TO BUY DATA ---
async function buyData(deviceId, readingIndex) {
  const url = `http://localhost:3000/data/${deviceId}/${readingIndex}`;
  console.log(`Attempting to buy data from: ${url}`);

  try {
    console.log("Making payment request...");
    const response = await fetchWithPayment(url, { method: "GET" });

    // Log response details for debugging
    console.log(`Response status: ${response.status}`);
    console.log(`Response headers:`, Object.fromEntries(response.headers));

    if (!response.ok) {
      let errorBody;
      try {
        const responseText = await response.text();
        console.log(`Raw error response: ${responseText}`);
        errorBody = JSON.parse(responseText);
      } catch (parseError) {
        console.error("Failed to parse error response:", parseError.message);
        errorBody = { error: "Unable to parse error response" };
      }
      throw new Error(
        `Failed to fetch data: ${response.status} ${JSON.stringify(errorBody)}`
      );
    }

    // Handle JSON parsing more carefully
    let data;
    try {
      const responseText = await response.text();
      console.log(`Raw response text length: ${responseText.length}`);
      console.log(`Raw response text: "${responseText}"`);

      // Check for any problematic characters
      for (let i = 0; i < responseText.length; i++) {
        const char = responseText[i];
        const charCode = responseText.charCodeAt(i);
        if (charCode > 127) {
          console.log(
            `Non-ASCII character found at position ${i}: "${char}" (code: ${charCode})`
          );
        }
      }

      data = JSON.parse(responseText);
    } catch (parseError) {
      console.error("JSON Parse Error:", parseError.message);
      console.error("Failed to parse response as JSON");
      throw new Error(`Invalid JSON response: ${parseError.message}`);
    }

    console.log("\n✅ SUCCESS! Data Purchased:");
    console.log(data);

    // The server includes payment confirmation in a response header
    try {
      const paymentHeaderValue = response.headers.get("x-payment-response");
      console.log(`Payment header raw value: "${paymentHeaderValue}"`);

      if (paymentHeaderValue) {
        const paymentResponse = decodeXPaymentResponse(paymentHeaderValue);
        if (paymentResponse) {
          console.log("\n🧾 Payment Receipt:");
          console.log(
            `  Transaction Hash: https://www.oklink.com/amoy/tx/${paymentResponse.txHash}`
          );
        }
      } else {
        console.log("No payment response header found");
      }
    } catch (paymentError) {
      console.error("Error decoding payment response:", paymentError.message);
      console.log(
        "This doesn't affect the data purchase - the payment was successful"
      );
    }
  } catch (error) {
    console.error("\n❌ ERROR during purchase:", error.message);
    // If the error object has more details from the server, log them
    if (error.response) {
      try {
        console.error("Server Response:", await error.response.json());
      } catch (e) {
        console.error("Could not parse server response as JSON");
      }
    }
  }
}

// --- 4. RUN THE CLIENT ---
// Test with the working simple-test endpoint first
console.log("=== TESTING PAYMENT WITH SIMPLE ENDPOINT ===");

async function testSimplePayment() {
  const url = `http://localhost:3000/simple-test`;
  console.log(`Testing payment with: ${url}`);

  try {
    const response = await fetchWithPayment(url, { method: "GET" });
    const data = await response.json();
    console.log("\n✅ SUCCESS! Payment test worked:");
    console.log(data);
  } catch (error) {
    console.error("\n❌ Payment test failed:", error.message);
  }
}

// Test the payment system first
await testSimplePayment();

// Then test the original data endpoint
console.log("\n=== TESTING DATA ENDPOINT ===");
const targetDeviceId = "00:1A:2B:3C:4D:5E";
const targetReadingIndex = 0;

buyData(targetDeviceId, targetReadingIndex);
