#!/bin/bash

# Simple curl commands to test the dynamic marketplace
# Make sure the server is running on port 5002 before running these

echo "🧪 Testing Dynamic Marketplace with Curl Commands"
echo "=================================================="

SERVER="http://localhost:5002"

echo ""
echo "📡 Test 1: Basic Dynamic Purchase"
echo "Device: 00:1A:2B:3C:4D:5E, Owner: 0xB5f278f22c5E5C42174FC312cc593493d2f3570D, Price: 0.001"

curl -X POST $SERVER/market/purchase \
  -H "Content-Type: application/json" \
  -d '{
    "deviceId": "00:1A:2B:3C:4D:5E",
    "ownerAddress": "0xB5f278f22c5E5C42174FC312cc593493d2f3570D",
    "priceAmount": "0.01"
  }' | jq .

echo ""
echo "=================================================="
echo "📡 Test 2: Different Device with Custom Price"
echo "Device: SENSOR-TEMP-001, Owner: 0x26EFd260dbE98A8f7f44555b29079d93698119be, Price: $0.05"

curl -X POST $SERVER/market/purchase \
  -H "Content-Type: application/json" \
  -d '{
    "deviceId": "SENSOR-TEMP-001",
    "ownerAddress": "0x26EFd260dbE98A8f7f44555b29079d93698119be",
    "priceAmount": "0.05",
    "readingIndex": "3"
  }' | jq .

echo ""
echo "=================================================="
echo "📡 Test 3: High Value Sensor Data"
echo "Device: PREMIUM-SENSOR-XYZ, Owner: 0x742d35Cc6634C0532925a3b8D4C9dC0C012345678, Price: $1.00"

curl -X POST $SERVER/market/purchase \
  -H "Content-Type: application/json" \
  -d '{
    "deviceId": "PREMIUM-SENSOR-XYZ",
    "ownerAddress": "0x742d35Cc6634C0532925a3b8D4C9dC0C012345678",
    "priceAmount": "1.00",
    "readingIndex": "10"
  }' | jq .

echo ""
echo "=================================================="
echo "📡 Test 4: Error Test - Missing Parameters"

curl -X POST $SERVER/market/purchase \
  -H "Content-Type: application/json" \
  -d '{
    "deviceId": "TEST-DEVICE",
    "priceAmount": "0.01"
  }' | jq .

echo ""
echo "=================================================="
echo "✅ All tests completed!"
echo ""
echo "💡 To run individual commands, copy and paste from above"
echo "💡 Make sure jq is installed for pretty JSON output"
echo "💡 Remove '| jq .' if you don't have jq installed"