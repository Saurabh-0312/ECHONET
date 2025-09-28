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
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import logging

# Load environment variables
load_dotenv()

# --- MongoDB Configuration ---
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'echonet_db')
MONGODB_COLLECTION = os.getenv('MONGODB_COLLECTION', 'sensor_registry')

# Initialize MongoDB connection
try:
    mongo_client = MongoClient(MONGODB_URI)
    db = mongo_client[MONGODB_DATABASE]
    sensor_collection = db[MONGODB_COLLECTION]
    
    # Test connection
    mongo_client.admin.command('ping')
    print(f"✅ MongoDB connected successfully to {MONGODB_DATABASE}")
    MONGODB_AVAILABLE = True
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    print("⚠️  Falling back to in-memory storage")
    MONGODB_AVAILABLE = False
    mongo_client = None
    db = None
    sensor_collection = None

# --- Initial Data (for MongoDB migration only) ---
INITIAL_SENSOR_DATA = {
    "_network_services": {
        "notary_agent_address": "agent1qwmhdqv4smh9c5z82rdx0q09nqchtgyw2ewgl0zr8rqu4jtaq2psxp0n2ya" 
    },
    "11:2A:00:3B:4D:22": {
        "loc_id": "LOC004",
        "name": "NIT, 9, Jalandhar",
        "latitude": 28.50103,
        "longitude": 77.042798,
        "agent_name": "worker_agent_5",
        "agent_seed": "gold broket example fruit cliff crazy forum walk obscure glory luxury number",
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
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

try:
    from config.settings import ETHEREUM_NODE_URL, ECHONET_STAKING_CONTRACT_ADDRESS, CONTRACT_OWNER_PRIVATE_KEY
except ImportError:
    WEB3_STORAGE_TOKEN = "YOUR_WEB3_STORAGE_API_TOKEN"
    ETHEREUM_NODE_URL = "RPC"
    ECHONET_STAKING_CONTRACT_ADDRESS = "contract_address"
    CONTRACT_OWNER_PRIVATE_KEY = ""

app = Flask(__name__)

# Template folder configuration
app.template_folder = os.path.join(PROJECT_ROOT, 'frontend')

# CORS configuration
CORS(app, 
     origins="*",
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])

# Initialize blockchain connection
if ETHEREUM_NODE_URL and ETHEREUM_NODE_URL != "RPC":
    try:
        w3 = Web3(Web3.HTTPProvider(ETHEREUM_NODE_URL))
        owner_account = w3.eth.account.from_key(CONTRACT_OWNER_PRIVATE_KEY)
        with open(os.path.join(PROJECT_ROOT, 'abis', 'staking_contract.json'), 'r') as f:
            contract_abi = json.load(f)
        staking_contract = w3.eth.contract(address=ECHONET_STAKING_CONTRACT_ADDRESS, abi=contract_abi)
        print(f"✅ Blockchain connected. Contract Owner: {owner_account.address}")
        BLOCKCHAIN_AVAILABLE = True
    except Exception as e:
        print(f"❌ Blockchain connection failed: {e}")
        BLOCKCHAIN_AVAILABLE = False
        w3 = None
        staking_contract = None
        owner_account = None
else:
    BLOCKCHAIN_AVAILABLE = False
    w3 = None
    staking_contract = None
    owner_account = None

# --- MongoDB Database Functions ---

def init_mongodb_with_existing_data():
    """Initialize MongoDB with existing sensor data if collection is empty."""
    if not MONGODB_AVAILABLE:
        return
    
    try:
        # Check if collection is empty
        if sensor_collection.count_documents({}) == 0:
            print("📦 Initializing MongoDB with existing sensor data...")
            
            # Convert initial data to MongoDB documents
            documents = []
            for mac_address, sensor_data in INITIAL_SENSOR_DATA.items():
                document = {
                    "_id": mac_address,
                    "mac_address": mac_address,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    **sensor_data
                }
                documents.append(document)
            
            # Insert all documents
            if documents:
                sensor_collection.insert_many(documents)
                print(f"✅ Successfully migrated {len(documents)} sensors to MongoDB")
            else:
                print("⚠️  No sensors to migrate")
        else:
            print(f"📊 MongoDB already contains {sensor_collection.count_documents({})} sensors")
            
    except Exception as e:
        print(f"❌ Error initializing MongoDB: {e}")

def read_registry():
    """Reads sensor registry from MongoDB and returns in the exact same format as before."""
    if not MONGODB_AVAILABLE:
        # Fallback to initial data
        return clean_null_values(INITIAL_SENSOR_DATA)
    
    try:
        # Fetch all sensors from MongoDB
        sensors = sensor_collection.find({})
        registry = {}
        
        for sensor in sensors:
            mac_address = sensor.get('_id') or sensor.get('mac_address')
            if mac_address:
                # Remove MongoDB-specific fields and keep only the original sensor data
                sensor_data = {k: v for k, v in sensor.items() 
                             if k not in ['_id', 'created_at', 'updated_at', 'mac_address']}
                registry[mac_address] = sensor_data
        
        # Clean null values and return in exact same format
        cleaned_registry = clean_null_values(registry)
        return cleaned_registry if cleaned_registry else {}
        
    except Exception as e:
        print(f"❌ Error reading from MongoDB: {e}")
        # Fallback to initial data
        return clean_null_values(INITIAL_SENSOR_DATA)

def write_sensor_to_registry(mac_address, sensor_data):
    """Writes a single sensor to MongoDB."""
    if not MONGODB_AVAILABLE:
        print(f"⚠️  MongoDB not available, sensor {mac_address} not persisted")
        return False
    
    try:
        document = {
            "_id": mac_address,
            "mac_address": mac_address,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            **sensor_data
        }
        
        # Use upsert to insert or update
        sensor_collection.replace_one(
            {"_id": mac_address}, 
            document, 
            upsert=True
        )
        
        print(f"✅ Sensor {mac_address} saved to MongoDB")
        return True
        
    except Exception as e:
        print(f"❌ Error saving sensor {mac_address} to MongoDB: {e}")
        return False

def delete_sensor_from_registry(mac_address):
    """Deletes a sensor from MongoDB."""
    if not MONGODB_AVAILABLE:
        print(f"⚠️  MongoDB not available, sensor {mac_address} cannot be deleted")
        return False
    
    try:
        result = sensor_collection.delete_one({"_id": mac_address})
        
        if result.deleted_count > 0:
            print(f"✅ Sensor {mac_address} deleted from MongoDB")
            return True
        else:
            print(f"⚠️  Sensor {mac_address} not found in MongoDB")
            return False
            
    except Exception as e:
        print(f"❌ Error deleting sensor {mac_address} from MongoDB: {e}")
        return False

def get_existing_locations():
    """Get all existing locations from the registry for ID reuse."""
    registry = read_registry()
    existing_locations = {}
    
    for k, v in registry.items():
        if k is not None and not k.startswith('_') and v is not None and isinstance(v, dict):
            if 'name' in v and 'loc_id' in v and v['name'] is not None and v['loc_id'] is not None:
                existing_locations[v['name']] = v['loc_id']
    
    return existing_locations

def clean_null_values(data):
    """Recursively removes null/None values from dictionaries and lists."""
    if isinstance(data, dict):
        cleaned = {}
        for key, value in data.items():
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

# --- Flask Routes ---

@app.route('/')
def index():
    """Serves the main registration page."""
    try:
        return render_template('index.html')
    except Exception as e:
        return jsonify({"status": "error", "message": f"Frontend not found: {e}"}), 404

@app.route('/register', methods=['POST'])
def register_sensor():
    """Handles new sensor registration and stores in MongoDB."""
    try:
        # JSON validation
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
        
        # Validate MAC address
        if not mac_address or len(mac_address.strip()) == 0:
            return jsonify({"status": "error", "message": "MAC address cannot be empty"}), 400
        
        # Check if sensor already exists
        registry = read_registry()
        if mac_address in registry:
            return jsonify({"status": "error", "message": "This device (MAC address) is already registered."}), 409

        # Generate location name
        location_name = f"{data.get('area').strip()}, {data.get('sector_no').strip()}, {data.get('city').strip()}"
        
        # Check for existing locations to reuse location ID
        existing_locations = get_existing_locations()
        
        if location_name in existing_locations:
            loc_id = existing_locations[location_name]
            print(f"[API] Reusing existing location ID '{loc_id}' for '{location_name}'")
        else:
            # Generate new location ID
            new_id_num = len(existing_locations) + 1
            loc_id = f"LOC{str(new_id_num).zfill(3)}"
            print(f"[API] Creating new location ID '{loc_id}' for '{location_name}'")

        # Generate agent details
        agent_count = len(existing_locations)
        agent_name = f"worker_agent_{agent_count + 1}"
        new_port = 8010 + agent_count
        new_seed = Mnemonic("english").generate(strength=128)
        
        # Create sensor data (same format as before)
        sensor_data = {
            "loc_id": loc_id,
            "name": location_name,
            "latitude": float(data.get('latitude')),
            "longitude": float(data.get('longitude')),
            "agent_name": agent_name,
            "agent_seed": new_seed,
            "agent_port": new_port
        }
        
        # Save to MongoDB
        success = write_sensor_to_registry(mac_address, sensor_data)
        
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

@app.route('/registry', methods=['GET'])
def get_registry():
    """Returns the sensor registry in the exact same format as before."""
    try:
        registry = read_registry()
        
        # Return the registry in the exact same format as your current response
        return jsonify(registry)
        
    except Exception as e:
        print(f"[API] Registry error: {e}")
        return jsonify({"status": "error", "message": f"Failed to fetch registry: {str(e)}"}), 500

@app.route('/deregister', methods=['POST'])
def deregister_sensor():
    """Deregisters a sensor by removing it from MongoDB."""
    try:
        data = request.json
        mac_address = data.get('mac_address')
        
        if not mac_address:
            return jsonify({"status": "error", "message": "MAC address is required."}), 400
        
        # Check if sensor exists
        registry = read_registry()
        if mac_address not in registry:
            return jsonify({"status": "error", "message": f"Device {mac_address} not found in registry."}), 404
        
        # Store sensor info before removal
        sensor_info = registry[mac_address]
        agent_name = sensor_info.get('agent_name', 'unknown')
        
        print(f"[API] Deregistering sensor {mac_address} (Agent: {agent_name})")
        
        # Delete from MongoDB
        success = delete_sensor_from_registry(mac_address)
        
        if success or not MONGODB_AVAILABLE:
            print(f"[API] Sensor {mac_address} removed from registry")
            return jsonify({
                "status": "success",
                "message": f"Sensor {mac_address} successfully deregistered.",
                "agent_name": agent_name
            })
        else:
            return jsonify({"status": "error", "message": "Failed to delete sensor"}), 500
            
    except Exception as e:
        print(f"[API] Deregistration error: {e}")
        return jsonify({"status": "error", "message": f"Deregistration failed: {str(e)}"}), 500

@app.route('/database/stats', methods=['GET'])
def get_database_stats():
    """Returns database statistics."""
    try:
        stats = {
            "mongodb_available": MONGODB_AVAILABLE,
            "database_name": MONGODB_DATABASE,
            "collection_name": MONGODB_COLLECTION,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if MONGODB_AVAILABLE:
            try:
                stats.update({
                    "total_documents": sensor_collection.count_documents({}),
                    "connection_status": "Connected"
                })
            except Exception as e:
                stats.update({
                    "connection_status": f"Error: {e}",
                    "total_documents": 0
                })
        else:
            stats.update({
                "connection_status": "Not Available - Using fallback data",
                "total_documents": len(INITIAL_SENSOR_DATA)
            })
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/request-slash', methods=['POST'])
def request_slash():
    """Handles blockchain slashing requests."""
    if not BLOCKCHAIN_AVAILABLE:
        return jsonify({
            "status": "error", 
            "message": "Blockchain connection not available"
        }), 503
        
    data = request.json
    mac_address = data.get('mac_address')
    print(f"\n[API] Received slash request for MAC: {mac_address}")

    if not mac_address:
        return jsonify({"status": "error", "message": "MAC address is required."}), 400

    try:
        normalized_id = mac_address
        print(f"[API] Normalized deviceId for contract: {normalized_id}")

        contract_owner = staking_contract.functions.owner().call()
        print(f"[API] Contract owner: {contract_owner}")
        print(f"[API] Transaction sender: {owner_account.address}")

        # Preflight simulation
        try:
            staking_contract.functions.slashStake(normalized_id).call({
                'from': owner_account.address
            })
            print("[API] Preflight simulation SUCCESS")
        except ContractLogicError as e:
            print(f"[API] Preflight revert: {e}")
            return jsonify({
                "status": "error",
                "message": f"Simulation failed: {e}",
                "device_id": normalized_id
            }), 400

        # Build and send transaction
        tx = staking_contract.functions.slashStake(normalized_id).build_transaction({
            'from': owner_account.address,
            'nonce': w3.eth.get_transaction_count(owner_account.address),
            'gas': 300000,
            'gasPrice': w3.to_wei('50', 'gwei'),
        })

        signed_tx = w3.eth.account.sign_transaction(tx, private_key=CONTRACT_OWNER_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"[API] Transaction hash: {tx_hash.hex()}")

        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status == 0:
            return jsonify({
                "status": "error",
                "message": "Transaction reverted on-chain",
                "tx_hash": tx_hash.hex(),
                "device_id": normalized_id
            }), 400

        return jsonify({
            "status": "success",
            "message": "Slash transaction confirmed",
            "tx_hash": tx_hash.hex(),
            "device_id": normalized_id
        })

    except Exception as e:
        print(f"[API] Slash error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# --- Application Initialization ---

if __name__ == '__main__':
    print(f"🚀 Starting EchoNet Backend Server...")
    print(f"📁 Project root: {PROJECT_ROOT}")
    print(f"🗄️  MongoDB: {'Connected' if MONGODB_AVAILABLE else 'Not Available (using fallback)'}")
    print(f"⛓️  Blockchain: {'Connected' if BLOCKCHAIN_AVAILABLE else 'Not Available'}")
    
    # Initialize MongoDB with existing data
    if MONGODB_AVAILABLE:
        init_mongodb_with_existing_data()
    
    # Use environment PORT for deployment or 5000 for local
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)