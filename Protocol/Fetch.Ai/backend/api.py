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

# --- Path Configuration ---
# Assumes api.py is in the project's root directory.

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
SENSOR_REGISTRY_FILE = os.path.join(PROJECT_ROOT, "sensor_registry.json")

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
CORS(app)

w3 = Web3(Web3.HTTPProvider(ETHEREUM_NODE_URL))
owner_account = w3.eth.account.from_key(CONTRACT_OWNER_PRIVATE_KEY)
# Load the contract ABI
with open(os.path.join(PROJECT_ROOT, 'abis', 'staking_contract.json'), 'r') as f:
    contract_abi = json.load(f)
staking_contract = w3.eth.contract(address=ECHONET_STAKING_CONTRACT_ADDRESS, abi=contract_abi)
print(f"Connected to blockchain. Contract Owner Address: {owner_account.address}")


def read_registry():
    """Safely reads the shared sensor registry file."""
    if not os.path.exists(SENSOR_REGISTRY_FILE):
        # If the file doesn't exist, start with a default structure.
        return {"_network_services": {}}
    with open(SENSOR_REGISTRY_FILE, 'r') as f:
        return json.load(f)

def write_registry(registry):
    """Safely writes to the shared sensor registry file."""
    with open(SENSOR_REGISTRY_FILE, 'w') as f:
        json.dump(registry, f, indent=4)

@app.route('/')
def index():
    """Serves the main registration page from the frontend directory."""
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register_sensor():
    """
    Handles new sensor registration, manages the central registry with location IDs,
    and launches a dedicated worker agent and its gateway for the new device.
    """
    data = request.json
    mac_address = data.get('mac_address')
    
    registry = read_registry()
    if mac_address in registry:
        return jsonify({"status": "error", "message": "This device (MAC address) is already registered."}), 409

    # --- Section 1.A: Manage the Sensor Registry ---

    # 1. Standardize the location name as per the prompt.
    location_name = f"{data.get('area').strip()}, {data.get('sector_no').strip()}, {data.get('city').strip()}"
    
    # 2. Check for existing locations to reuse the location ID (loc_id).
    loc_id = None
    # Create a dictionary of existing location names and their corresponding IDs.
    # We must exclude the '_network_services' key from this check.
    existing_locations = {v['name']: v['loc_id'] for k, v in registry.items() if not k.startswith('_')}
    
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
    agent_count = len({k: v for k, v in registry.items() if not k.startswith('_')})
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

    # 6. Launch the new worker agent and its dedicated gateway process.
    python_executable = sys.executable
    try:
        # Construct absolute paths to the scripts to be launched.
        agent_script_path = os.path.join(PROJECT_ROOT, "fetch_services", "agents", "regional_agent.py")
        gateway_script_path = os.path.join(PROJECT_ROOT, "hardware_services", "esp32_gateway.py")

        # The agent and gateway are started with only the MAC address.
        # They will use this MAC to look up their full configuration in the registry.
        print(f"Launching agent: {agent_name} for MAC: {mac_address}")
        subprocess.Popen([python_executable, agent_script_path, mac_address])
        
        print(f"Launching gateway for MAC: {mac_address}")
        subprocess.Popen([python_executable, gateway_script_path, mac_address])
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to launch processes: {e}"}), 500

    return jsonify({
        "status": "success",
        "message": f"Agent '{agent_name}' for device {mac_address} registered and launched successfully."
    })

@app.route('/request-slash', methods=['POST'])
def request_slash():
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
    print(PROJECT_ROOT)
    
    app.run(host='0.0.0.0', port=5000, debug=True)

