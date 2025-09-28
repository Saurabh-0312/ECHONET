from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import subprocess
import os
import sys
from mnemonic import Mnemonic
import numpy as np
from web3 import Web3
from web3.exceptions import ContractLogicError
import requests

# --- In-Memory Registry Buffer ---
# This dictionary will hold the sensor registry data in memory.
# WARNING: Data will be lost on application restart.
sensor_registry_buffer = {
    "_network_services": {
        "notary_agent_address": "agent1qwmhdqv4smh9c5z82rdx0q09nqchtgyw2ewgl0zr8rqu4jtaq2psxp0n2ya" 
    },
    "11:2A:00:3B:4D:22": {
        "loc_id": "LOC004",
        "name": "NIT, 9, Jalandhar",
        "latitude": 28.50103,
        "longitude": 77.042798,
        "agent_name": "worker_agent_5",
        "agent_seed": "gold broket example fruit cliff crazy forum walk obscure glory luxury number",  # Fixed typo
        "agent_port": 8014
    },
    "00:1A:2B:3C:4D:5E": {
        "loc_id": "LOC001",
        "name": "Dwarka , 7, Delhi",
        "latitude": 28.51103,
        "longitude": 77.012798,
        "agent_name": "worker_agent_1",
        "agent_seed": "hour armed goddess false smoke oak physical clean near place concert will",
        "agent_port": 8010
    },
    "AA:BB:CC:D1:EE:FF": {
        "loc_id": "LOC003",
        "name": "Area 51, S4, Nevada",
        "latitude": 37.235,
        "longitude": -115.8111,
        "agent_name": "worker_agent_3",
        "agent_seed": "skin blur buddy stairs nature solid math message timber exile mobile elephant",
        "agent_port": 8012
    }
}

# --- Path Configuration ---
# Assumes api.py is in the project's root directory.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

try:
    from config.settings import ETHEREUM_NODE_URL, ECHONET_STAKING_CONTRACT_ADDRESS, CONTRACT_OWNER_PRIVATE_KEY
except ImportError:
    WEB3_STORAGE_TOKEN = "YOUR_WEB3_STORAGE_API_TOKEN"
    ETHEREUM_NODE_URL="RPC"
    ECHONET_STAKING_CONTRACT_ADDRESS="contract_address"
    CONTRACT_OWNER_PRIVATE_KEY=""

app = Flask(__name__)

# The template folder is now correctly located in the 'frontend' directory.
app.template_folder = os.path.join(PROJECT_ROOT, 'frontend')

# Allow CORS for all origins
CORS(app, 
     origins="*",
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])

# Initialize blockchain connection only if credentials are available
if ETHEREUM_NODE_URL and ETHEREUM_NODE_URL != "RPC":
    try:
        w3 = Web3(Web3.HTTPProvider(ETHEREUM_NODE_URL))
        owner_account = w3.eth.account.from_key(CONTRACT_OWNER_PRIVATE_KEY)
        # Load the contract ABI
        with open(os.path.join(PROJECT_ROOT, 'abis', 'staking_contract.json'), 'r') as f:
            contract_abi = json.load(f)
        staking_contract = w3.eth.contract(address=ECHONET_STAKING_CONTRACT_ADDRESS, abi=contract_abi)
        print(f"Connected to blockchain. Contract Owner Address: {owner_account.address}")
        BLOCKCHAIN_AVAILABLE = True
    except Exception as e:
        print(f"Blockchain connection failed: {e}")
        BLOCKCHAIN_AVAILABLE = False
        w3 = None
        staking_contract = None
        owner_account = None
else:
    BLOCKCHAIN_AVAILABLE = False
    w3 = None
    staking_contract = None
    owner_account = None

def read_registry():
    """Reads from the in-memory sensor registry buffer."""
    global sensor_registry_buffer
    # Clean up any None keys that might have been introduced
    cleaned_registry = {k: v for k, v in sensor_registry_buffer.items() if k is not None and v is not None}
    sensor_registry_buffer = cleaned_registry
    return sensor_registry_buffer

def write_registry(registry_data):
    """Writes to the in-memory sensor registry buffer."""
    global sensor_registry_buffer
    sensor_registry_buffer = registry_data

@app.route('/')
def index():
    """Serves the main registration page from the frontend directory."""
    try:
        return render_template('index.html')
    except Exception as e:
        return jsonify({"status": "error", "message": f"Frontend not found: {e}"}), 404

@app.route('/register', methods=['POST'])
def register_sensor():
    """
    Handles new sensor registration, manages the central registry with location IDs,
    and launches a dedicated worker agent and its gateway for the new device.
    """
    try:
        # Add JSON validation
        if not request.is_json:
            return jsonify({"status": "error", "message": "Request must be JSON"}), 400
            
        data = request.get_json()
        if data is None:
            return jsonify({"status": "error", "message": "Invalid JSON format"}), 400
            
        # Validate required fields
        required_fields = ['mac_address', 'area', 'sector_no', 'city', 'latitude', 'longitude']
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({"status": "error", "message": f"Missing required field: {field}"}), 400
        
        mac_address = data.get('mac_address')
        
        # Validate MAC address format (basic check)
        if not mac_address or len(mac_address.strip()) == 0:
            return jsonify({"status": "error", "message": "MAC address cannot be empty"}), 400
        
        registry = read_registry()
        if mac_address in registry:
            return jsonify({"status": "error", "message": "This device (MAC address) is already registered."}), 409

        # --- Section 1.A: Manage the Sensor Registry ---

        # 1. Standardize the location name as per the prompt.
        location_name = f"{data.get('area').strip()}, {data.get('sector_no').strip()}, {data.get('city').strip()}"
        
        # 2. Check for existing locations to reuse the location ID (loc_id).
        loc_id = None
        # Create a dictionary of existing location names and their corresponding IDs.
        # We must exclude the '_network_services' key from this check AND handle None keys
        existing_locations = {}
        for k, v in registry.items():
            # Skip if key is None or starts with '_' or if value is None
            if k is not None and not k.startswith('_') and v is not None and isinstance(v, dict):
                if 'name' in v and 'loc_id' in v and v['name'] is not None and v['loc_id'] is not None:
                    existing_locations[v['name']] = v['loc_id']
        
        if location_name in existing_locations:
            loc_id = existing_locations[location_name]
            print(f"[API] Reusing existing location ID '{loc_id}' for '{location_name}'")
        else:
            # 3. If it's a new location, generate a new, unique, sequential ID.
            new_id_num = len(existing_locations) + 1
            loc_id = f"LOC{str(new_id_num).zfill(3)}" # e.g., LOC001, LOC002
            print(f"[API] Creating new location ID '{loc_id}' for '{location_name}'")

        # --- Section 1.B: Launch the Worker Agent ---
        
        # 4. Generate a new, unique identity for the worker agent.
        # We count only the actual devices, not the network services entry.
        agent_count = len(existing_locations)  # Use existing_locations count instead
        agent_name = f"worker_agent_{agent_count + 1}"
        new_port = 8010 + agent_count # Use a different port range for workers to avoid conflicts
        new_seed = Mnemonic("english").generate(strength=128)
        
        # 5. Add the complete new entry to the registry.
        registry[mac_address] = {
            "loc_id": loc_id,
            "name": location_name,
            "latitude": float(data.get('latitude')),
            "longitude": float(data.get('longitude')),
            "agent_name": agent_name,
            "agent_seed": new_seed,
            "agent_port": new_port
        }
        write_registry(registry)

        print(f"[API] Successfully registered sensor {mac_address} with agent {agent_name}")

        return jsonify({
            "status": "success",
            "message": f"Agent '{agent_name}' for device {mac_address} registered and launched successfully.",
            "agent_name": agent_name,
            "location_id": loc_id
        })
        
    except ValueError as e:
        print(f"[API] JSON parsing error: {e}")
        return jsonify({"status": "error", "message": f"Invalid JSON format: {str(e)}"}), 400
    except Exception as e:
        print(f"[API] Registration error: {e}")
        return jsonify({"status": "error", "message": f"Registration failed: {str(e)}"}), 500

def clean_null_values(data):
    """Recursively removes null/None values from dictionaries and lists."""
    if isinstance(data, dict):
        cleaned = {}
        for key, value in data.items():
            # Skip None keys entirely
            if key is not None and value is not None:
                cleaned_value = clean_null_values(value)
                if cleaned_value is not None:
                    cleaned[key] = cleaned_value
        return cleaned if cleaned else None
    elif isinstance(data, list):
        cleaned = [clean_null_values(item) for item in data if item is not None]
        return [item for item in cleaned if item is not None] if cleaned else None
    else:
        return data if data is not None else None

@app.route('/registry', methods=['GET'])
def get_registry():
    """Serves the entire sensor registry from the in-memory buffer."""
    try:
        registry = read_registry()
        
        # Clean null values from the registry
        cleaned_registry = clean_null_values(registry)
        
        # Ensure we always return a valid dictionary
        if cleaned_registry is None:
            cleaned_registry = {}
            
        return jsonify(cleaned_registry)
        
    except Exception as e:
        print(f"[API] Registry error: {e}")
        return jsonify({"status": "error", "message": f"Failed to fetch registry: {str(e)}"}), 500

@app.route('/deregister', methods=['POST'])
def deregister_sensor():
    """
    Deregisters a sensor by removing it from the buffer and then calling request-slash.
    """
    data = request.json
    mac_address = data.get('mac_address')
    
    if not mac_address:
        return jsonify({"status": "error", "message": "MAC address is required."}), 400
    
    registry = read_registry()
    
    # Check if the MAC address exists in the registry
    if mac_address not in registry:
        return jsonify({"status": "error", "message": f"Device {mac_address} not found in registry."}), 404
    
    # Store the sensor info before removal for logging
    sensor_info = registry[mac_address]
    agent_name = sensor_info.get('agent_name', 'unknown')
    
    print(f"[API] Deregistering sensor {mac_address} (Agent: {agent_name})")
    
    # Remove the sensor from the registry buffer
    del registry[mac_address]
    write_registry(registry)
    
    print(f"[API] Sensor {mac_address} removed from registry buffer")
    
    return jsonify({
        "status": "success",
        "message": f"Sensor {mac_address} successfully deregistered.",
        "agent_name": agent_name
    })
            
   
@app.route('/request-slash', methods=['POST'])
def request_slash():
    if not BLOCKCHAIN_AVAILABLE:
        return jsonify({
            "status": "error", 
            "message": "Blockchain connection not available"
        }), 503
        
    data = request.json
    mac_address = data.get('mac_address')
    print(f"\n[API] Received slash request for raw MAC: {mac_address}")

    if not mac_address:
        return jsonify({"status": "error", "message": "MAC address is required."}), 400

    try:
        # 🔍 Normalize the device ID (here just use MAC directly)
        normalized_id = mac_address
        print(f"[API] Normalized deviceId for contract: {normalized_id}")

        # 🔍 Fetch contract owner
        contract_owner = staking_contract.functions.owner().call()
        print(f"[API] Contract owner (on-chain): {contract_owner}")
        print(f"[API] Transaction sender (local): {owner_account.address}")
        print(f"[API] Are they equal? {contract_owner.lower() == owner_account.address.lower()}")

        # 🔍 Query deviceId -> sensor address mapping
        try:
            sensor_addr = staking_contract.functions.deviceIdToOwner(normalized_id).call()
            print(f"[API] deviceIdToOwner[{normalized_id}] -> {sensor_addr}")

            if sensor_addr and sensor_addr != "0x0000000000000000000000000000000000000000":
                stake_amount = staking_contract.functions.stakes(sensor_addr).call()
                print(f"[API] Current stake for {sensor_addr}: {stake_amount}")
            else:
                print(f"[API] No sensor registered for deviceId {normalized_id}")

        except Exception as e:
            print(f"[API] Could not query deviceIdToOwner[{normalized_id}]: {e}")

        # 🔍 Preflight call simulation
        try:
            staking_contract.functions.slashStake(normalized_id).call({
                'from': owner_account.address
            })
            print("[API] Preflight simulation SUCCESS — tx should not revert.")
        except ContractLogicError as e:
            print(f"[API] Preflight revert: {e}")
            return jsonify({
                "status": "error",
                "message": f"Simulation failed: {e}",
                "device_id": normalized_id
            }), 400

        # ✅ Build real transaction
        tx = staking_contract.functions.slashStake(normalized_id).build_transaction({
            'from': owner_account.address,
            'nonce': w3.eth.get_transaction_count(owner_account.address),
            'gas': 300000,
            'gasPrice': w3.to_wei('50', 'gwei'),
        })
        print(f"[API] Built transaction: {tx}")

        signed_tx = w3.eth.account.sign_transaction(tx, private_key=CONTRACT_OWNER_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"[API] Slash transaction broadcast. Hash: {tx_hash.hex()}")

        # Wait for confirmation
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"[API] Receipt: {receipt}")

        if receipt.status == 0:
            print("[API] Transaction REVERTED on-chain ❌")
            return jsonify({
                "status": "error",
                "message": "Transaction reverted on-chain",
                "tx_hash": tx_hash.hex(),
                "device_id": normalized_id
            }), 400

        print("[API] Transaction SUCCESS ✅")
        return jsonify({
            "status": "success",
            "message": "Slash transaction confirmed",
            "tx_hash": tx_hash.hex(),
            "device_id": normalized_id
        })

    except Exception as e:
        print(f"[API] CRITICAL ERROR: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print(f"Project root: {PROJECT_ROOT}")
    
    # Use environment PORT for deployment or 5000 for local
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)