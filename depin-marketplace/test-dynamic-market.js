#!/usr/bin/env node

// Test script for the new dynamic marketplace endpoint
// This script demonstrates how to use the new parameters: deviceId, ownerAddress, priceAmount

import fetch from 'node-fetch';

const SERVER_URL = 'http://localhost:5002';

async function testDynamicMarketplace() {
    console.log('🧪 Testing Dynamic Marketplace Endpoint');
    console.log('========================================\n');

    // Test parameters - you can modify these
    const testParams = {
        deviceId: "00:1A:2B:3C:4D:5E",           // Device MAC address or ID
        ownerAddress: "0xB5f278f22c5E5C42174FC312cc593493d2f3570D",  // Payment recipient
        priceAmount: "0.01",                      // Price in USD
        readingIndex: "0"                         // Optional: reading index (defaults to "0")
    };

    console.log('📋 Test Parameters:');
    console.log(`   Device ID: ${testParams.deviceId}`);
    console.log(`   Owner Address: ${testParams.ownerAddress}`);
    console.log(`   Price Amount: $${testParams.priceAmount}`);
    console.log(`   Reading Index: ${testParams.readingIndex}\n`);

    try {
        console.log('📡 Making POST request to /market/purchase...\n');

        const response = await fetch(`${SERVER_URL}/market/purchase`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(testParams)
        });

        console.log(`📊 Response Status: ${response.status}`);
        console.log(`📊 Response Headers:`, Object.fromEntries(response.headers));

        const responseData = await response.json();
        
        if (response.ok) {
            console.log('\n✅ SUCCESS! Dynamic Marketplace Purchase Complete');
            console.log('📦 Response Data:');
            console.log(JSON.stringify(responseData, null, 2));
            
            if (responseData.purchaseDetails) {
                console.log('\n🛍️  Purchase Details:');
                console.log(`   Device: ${responseData.purchaseDetails.deviceId}`);
                console.log(`   Owner: ${responseData.purchaseDetails.ownerAddress}`);
                console.log(`   Price: $${responseData.purchaseDetails.priceAmount}`);
                console.log(`   Endpoint: ${responseData.purchaseDetails.endpointUsed}`);
            }
            
        } else {
            console.log('\n❌ Purchase Failed');
            console.log('Error Details:');
            console.log(JSON.stringify(responseData, null, 2));
        }

    } catch (error) {
        console.error('\n💥 Request Failed:', error.message);
        
        if (error.code === 'ECONNREFUSED') {
            console.log('\n💡 Make sure the marketplace server is running on port 5002:');
            console.log('   cd depin-marketplace');
            console.log('   npm start');
        }
    }
}

// Example of different test cases
async function runTestCases() {
    const testCases = [
        {
            name: "Test Case 1: Standard Sound Sensor",
            params: {
                deviceId: "00:1A:2B:3C:4D:5E",
                ownerAddress: "0xB5f278f22c5E5C42174FC312cc593493d2f3570D",
                priceAmount: "0.01"
            }
        },
        {
            name: "Test Case 2: Different Device, Higher Price",
            params: {
                deviceId: "AA:BB:CC:DD:EE:FF",
                ownerAddress: "0x26EFd260dbE98A8f7f44555b29079d93698119be",
                priceAmount: "0.05",
                readingIndex: "1"
            }
        },
        {
            name: "Test Case 3: Custom Parameters",
            params: {
                deviceId: "CUSTOM-DEVICE-001",
                ownerAddress: "0x742d35Cc6634C0532925a3b8D4C9dC0C0123456789",
                priceAmount: "0.25",
                readingIndex: "5"
            }
        }
    ];

    for (const testCase of testCases) {
        console.log(`\n${'='.repeat(60)}`);
        console.log(`🧪 ${testCase.name}`);
        console.log(`${'='.repeat(60)}`);
        
        try {
            const response = await fetch(`${SERVER_URL}/market/purchase`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(testCase.params)
            });
            
            const result = await response.json();
            console.log(`Status: ${response.status}`);
            console.log(`Result: ${JSON.stringify(result, null, 2)}`);
            
        } catch (error) {
            console.error(`Error: ${error.message}`);
        }
        
        // Wait between requests
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
}

// Check command line arguments
const args = process.argv.slice(2);

if (args.includes('--help') || args.includes('-h')) {
    console.log(`
Dynamic Marketplace Test Script

Usage:
  node test-dynamic-market.js              # Run single test
  node test-dynamic-market.js --all        # Run all test cases
  node test-dynamic-market.js --help       # Show this help

Environment:
  Make sure the marketplace server is running on port 5002
  
Example curl equivalent:
  curl -X POST http://localhost:5002/market/purchase \\
    -H "Content-Type: application/json" \\
    -d '{
      "deviceId": "00:1A:2B:3C:4D:5E",
      "ownerAddress": "0xB5f278f22c5E5C42174FC312cc593493d2f3570D",
      "priceAmount": "0.01",
      "readingIndex": "0"
    }'
`);
} else if (args.includes('--all')) {
    runTestCases();
} else {
    testDynamicMarketplace();
}