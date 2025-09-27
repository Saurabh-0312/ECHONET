# ======================================================================================
# ECHONET - SUPER COMBINED DEVICE NODE SCRIPT
# Combines audio monitoring, MQTT publishing, uAgent consensus, and FastAPI streaming
# into a single comprehensive device node application
# ======================================================================================

import sys
import threading
import queue
import paho.mqtt.client as mqtt
import asyncio
import hashlib
import json
import math
from datetime import datetime, timezone, timedelta
from typing import List, Dict
import csv
import uuid
import time

# Audio processing
import sounddevice as sd
import numpy as np

# Web framework
from fastapi import FastAPI, APIRouter
from fastapi.responses import StreamingResponse
import uvicorn

# Network and crypto
import requests
import aiohttp
from getmac import get_mac_address as gma

# uAgent framework
from uagents import Agent, Context, Model, Protocol
from uagents.crypto import Identity
from cosmpy.crypto.keypairs import PrivateKey, PublicKey
from mnemonic import Mnemonic

# ======================================================================================
# --- HARDCODED CONFIGURATION ---
# ❗️ EDIT THE VALUES IN THIS SECTION ❗️
# ======================================================================================

# 1. The public URL of your central Flask server (the one running api.py)
API_BASE_URL = "https://fetch-dev.onrender.com" # e.g., "https://echonet-api.onrender.com"

# 2. Your Agentverse API Key from https://agentverse.ai
AGENTVERSE_API_KEY = "eyJhbGciOiJSUzI1NiJ9.eyJleHAiOjE3NjA5ODc2NzcsImlhdCI6MTc1ODM5NTY3NywiaXNzIjoiZmV0Y2guYWkiLCJqdGkiOiI4ZTM0YzM2OGI3YmQ2MDY1ZWM3ZjkwMTgiLCJzY29wZSI6ImF2Iiwic3ViIjoiYjIxNjVjZTJjYmM4ODQ4ZDU0MjY4NjA1Yzc2Y2YzZTUzYmY3MmZkM2YzNzAxZmJjIn0.kYYZgca83_v7WqYmfFEGn6Ki7iEmRyWwfZSsg4Vak4ESDUOCWkajNBuBbZAXoy5VfohJVCR18O2AUe_3kRa0PywGpL_E-hqMJUvod5K_lVW0NDqpVRERHknGT8e8d-vLgYkRtnP-IFSkI2Npn2Rmv7H-WMmmty8U7JAy0P-Zvq9TSq8UrpDD3Hg5gikipnRL4RxarTgQNY-3ZbYTXweTPE6-QTYzjE9IB8rLFdmun_P6y1_IkjG0pleaYpZz-8Z1wohlAX52vTB8nl-gWVOWXv7tvF47qk2Q08-W96zWLKGsIXF4YZ2Ol0BcErY--OQ7VhxJQZF5tpgf1NTlJSiy-w"

# 3. The URL for your external data ingestion API (the one that receives enriched data)
EXTERNAL_INGEST_API_URL = "http://82.177.167.151:5001/ingest"

# 4. The URL for your raw data collector API
RAW_DATA_COLLECTOR_URL = "http://82.177.167.151:3001/api/sensor"

# 5. MQTT Broker Configuration (usually does not need to be changed)
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC_PREFIX = "echonet/sensors"

# 6. Audio settings
SAMPLERATE = 48000   # match your USB mic
BLOCKSIZE = 1024
CHANNELS = 1
CSV_FILE = "mic_db_log.csv"

# 7. FastAPI settings
FASTAPI_HOST = "0.0.0.0"
FASTAPI_PORT = 5007

# ======================================================================================
# --- Data Models (Schemas) ---
# ======================================================================================

class SensorData(Model):
    device_id: str
    timestamp: str
    decibel: float

class ValidationRequest(Model):
    event_id: str
    location: Dict[str, float]
    sound_class: str
    decibel: float
    public_key: str
    signature: str

class ValidationResponse(Model):
    event_id: str
    validated: bool
    public_key: str
    signature: str

class ValidatedSensorData(Model):
    mac_address: str
    timestamp: float
    sound_level_db: float
    location: Dict[str, float]

class FactCandidate(Model):
    validated_event: ValidatedSensorData

# ======================================================================================
# --- Audio Processing & Shared State ---
# ======================================================================================

# Shared variables for audio data
latest_db_values = []
audio_processing_active = False

# Message queues for inter-thread communication
sensor_data_queue = queue.Queue()
mqtt_message_queue = queue.Queue()

# Setup CSV file
def setup_csv():
    with open(CSV_FILE, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "dB"])

def audio_callback(indata, frames, time_info, status):
    """Audio callback function for real-time processing"""
    global latest_db_values, MAC_ADDRESS
    
    if status:
        print(f"Audio status: {status}")

    audio_data = indata[:, 0]

    # RMS to dB
    rms = np.sqrt(np.mean(audio_data**2))
    db = 20 * np.log10(rms + 1e-6) + 90  # offset to avoid log(0)

    # Append to shared list
    latest_db_values.append(db)
    if len(latest_db_values) > 50:  # keep recent values only
        latest_db_values.pop(0)

    # Log to CSV
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    with open(CSV_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, db])

    # ASCII visualization (optional, can be disabled for performance)
    bar_length = 50
    rms_len = int(np.clip(rms * 10, 0, 1) * bar_length) + int(0.3 * bar_length)
    peak_len = int(np.clip(np.max(np.abs(audio_data)), 0, 1) * bar_length)

    rms_bar = '█' * min(rms_len, bar_length)
    peak_bar = '█' * min(peak_len, bar_length)

    print(f"\rRMS: {rms_bar:<50} | Peak: {peak_bar:<50} | dB: {db:.2f}", end='', flush=True)

    # Create sensor data and add to queue for MQTT publishing
    sensor_data = SensorData(
        device_id=MAC_ADDRESS,
        timestamp=datetime.now().isoformat(),
        decibel=float(db)
    )
    
    try:
        sensor_data_queue.put_nowait(sensor_data)
    except queue.Full:
        print("⚠️ Sensor data queue is full, dropping oldest data")

# ======================================================================================
# --- Consensus Logic ---
# ======================================================================================

REFERENCE_DISTANCE = 1.0
NOISE_FLOOR_THRESHOLD = 20
CALIBRATION_MARGIN = 5
ATTENUATION_COEFFICIENT = 0.02

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371e3
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def expected_decibel_at_distance(source_db, distance):
    if distance < REFERENCE_DISTANCE: distance = REFERENCE_DISTANCE
    spreading_loss = 20 * math.log10(distance / REFERENCE_DISTANCE)
    absorption_loss = ATTENUATION_COEFFICIENT * (distance - REFERENCE_DISTANCE)
    return source_db - spreading_loss - absorption_loss

class SmartConsensus:
    def validate_event(self, request_data: dict, peer_sensor_data: dict, peer_agent_config: dict) -> bool:
        if peer_sensor_data['decibel'] < NOISE_FLOOR_THRESHOLD:
            return False
        
        orchestrator_location = request_data['location']
        peer_location = {"latitude": peer_agent_config["latitude"], "longitude": peer_agent_config["longitude"]}
        distance = haversine_distance(
            orchestrator_location['latitude'], orchestrator_location['longitude'],
            peer_location['latitude'], peer_location['longitude']
        )
        expected_db = expected_decibel_at_distance(request_data['decibel'], distance)
        
        return peer_sensor_data['decibel'] >= expected_db - CALIBRATION_MARGIN

# ======================================================================================
# --- Registry & Configuration Functions ---
# ======================================================================================

NOTARY_AGENT_ADDRESS = None

def read_registry():
    try:
        response = requests.get(f"{API_BASE_URL}/registry", timeout=10)
        response.raise_for_status()
        print("✅ Successfully fetched registry from API.")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ CRITICAL: Could not fetch registry from API: {e}. Exiting.")
        sys.exit(1)

def get_mac_address():
    """Get MAC address of the device (for FastAPI endpoints)"""
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return ":".join([mac[e:e+2] for e in range(0, 11, 2)])

# ======================================================================================
# --- Agent Configuration & Setup ---
# ======================================================================================

try:
    # Try to get MAC address from different network interfaces
    MAC_ADDRESS = gma(interface="wlan0") or gma(interface="eth0") or gma()
    
    if not MAC_ADDRESS: 
        raise ValueError("getmac returned empty.")
    
    # Format MAC address to standard format with colons
    if MAC_ADDRESS and '-' in MAC_ADDRESS:
        MAC_ADDRESS = MAC_ADDRESS.replace('-', ':')
    
    print(f"✅ Automatically detected MAC Address: {MAC_ADDRESS}")
except Exception as e:
    print(f"⚠️ Could not automatically detect MAC address ({e}).")
    if len(sys.argv) > 1:
        MAC_ADDRESS = sys.argv[1]
        print(f"✅ Using MAC address from command line: {MAC_ADDRESS}")
    else:
        # Fallback to hardcoded MAC for testing/development
        MAC_ADDRESS = "00:1A:2B:3C:4D:5E"
        print(f"⚠️ Using fallback MAC address: {MAC_ADDRESS}")
        print("   For production, ensure network interfaces are available or provide MAC via command line argument.")

ALL_CONFIGS = read_registry()
if MAC_ADDRESS not in ALL_CONFIGS:
    print(f"❌ CRITICAL: MAC Address {MAC_ADDRESS} not found in the registry. Please register it via the web UI. Exiting.")
    sys.exit(1)

CONFIG = ALL_CONFIGS[MAC_ADDRESS]
AGENT_NAME = CONFIG['agent_name']

# --- Agent Setup ---
agent = Agent(name=AGENT_NAME, seed=CONFIG["agent_seed"], mailbox=f"{AGENTVERSE_API_KEY}@agentverse.ai")

# --- State & Helpers ---
LOCAL_SENSOR_STATE = {}
SENSOR_FAILURE_COUNTS = {}
FAILURE_THRESHOLD = 5
PENDING_LOCK = asyncio.Lock()
pending_events = {}
GRID_SIZE = 0.1
smart_consensus = SmartConsensus()
QUORUM_RATIO = 0.45

seed_bytes = Mnemonic("english").to_seed(CONFIG["agent_seed"])
private_key = PrivateKey(seed_bytes[:32])
public_key = private_key.public_key

def get_digest(data: dict) -> bytes: 
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).digest()

def export_public_key_hex(pubkey: PublicKey) -> str: 
    return pubkey._verifying_key.to_string().hex()

# ======================================================================================
# --- Agent Helper Functions ---
# ======================================================================================

def cleanup_sensor_and_agent(mac_address: str):
    print(f"CRITICAL: Sensor with MAC {mac_address} exceeded failure threshold.")
    print(f"--> Requesting on-chain stake slash from the API server...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/request-slash",
            json={"mac_address": mac_address},
            timeout=20
        )
        response.raise_for_status()
        api_ack = response.json()
        print(f"--> API Acknowledged Slash Request: {api_ack.get('message')} (Tx: {api_ack.get('tx_hash')})")
    except requests.exceptions.RequestException as e:
        print(f"--> CRITICAL: Failed to send slash request to API: {e}")

def get_local_peer_group(event_location: dict) -> set:
    local_peers = set()
    all_configs = read_registry()
    event_grid_id = (math.floor(event_location["latitude"] / GRID_SIZE), math.floor(event_location["longitude"] / GRID_SIZE))
    for mac, cfg in all_configs.items():
        if not mac.startswith('_'):
            peer_grid_id = (math.floor(cfg["latitude"] / GRID_SIZE), math.floor(cfg["longitude"] / GRID_SIZE))
            if peer_grid_id == event_grid_id:
                peer_address = str(Identity.from_seed(cfg["agent_seed"], 0).address)
                local_peers.add(peer_address)
    return local_peers

async def final_actions_after_consensus(ctx: Context, event_info: dict, location: dict):
    global NOTARY_AGENT_ADDRESS
    raw_data = event_info["raw_data"]
    
    transformed_data = {"deviceId": raw_data['device_id'], "timestamp": raw_data['timestamp'], "decibel": raw_data['decibel']}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(RAW_DATA_COLLECTOR_URL, json=transformed_data, timeout=10) as resp:
                ctx.logger.info(f"Raw data sent to collector API, status: {resp.status}")
    except Exception as e:
        ctx.logger.error(f"Failed to send raw data to collector API: {e}")

    if NOTARY_AGENT_ADDRESS is None:
        registry = read_registry()
        NOTARY_AGENT_ADDRESS = registry.get("_network_services", {}).get("notary_agent_address")
    
    if NOTARY_AGENT_ADDRESS:
        fact = FactCandidate(validated_event=ValidatedSensorData(
            mac_address=raw_data['device_id'],
            timestamp=datetime.fromisoformat(raw_data['timestamp']).timestamp(),
            sound_level_db=raw_data['decibel'],
            location={"lat": location["latitude"], "lon": location["longitude"]}
        ))
        await ctx.send(NOTARY_AGENT_ADDRESS, fact)
        ctx.logger.info("Fact candidate sent to Notary Agent.")
    
    payload = {
        "mac_address": raw_data['device_id'],
        "latitude": location.get("latitude"),
        "longitude": location.get("longitude"),
        "decibel_level": raw_data['decibel'],
        "event_type": event_info["predicted_class"],
        "metadata": {"source": "sensor_network"}
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(EXTERNAL_INGEST_API_URL, json=payload, timeout=10) as resp:
                ctx.logger.info(f"Enriched data sent to external API, status: {resp.status}")
    except Exception as e:
        ctx.logger.error(f"Failed to send enriched packet to external API: {e}")

# ======================================================================================
# --- Agent Protocol Handlers ---
# ======================================================================================

validation_protocol = Protocol("WorkerAgentValidation")

async def handle_sensor_data(ctx: Context, sender: str, msg: SensorData):
    global LOCAL_SENSOR_STATE
    LOCAL_SENSOR_STATE = msg.dict()
    
    all_configs = read_registry()
    if msg.device_id not in all_configs: return
        
    registered_location = {"latitude": all_configs[msg.device_id]["latitude"], "longitude": all_configs[msg.device_id]["longitude"]}
    
    predicted_class, confidence = "ambient_noise", 0.99
    ctx.logger.info(f"Using hardcoded ML result: class='{predicted_class}', confidence={confidence}")
    
    event_id = hashlib.sha256(f"{msg.device_id}-{msg.timestamp}".encode()).hexdigest()
    event_local_group = get_local_peer_group(registered_location)

    async with PENDING_LOCK:
        pending_events[event_id] = {"raw_data": msg.dict(), "responses": [], "timestamp": datetime.now(timezone.utc), "predicted_class": predicted_class, "confidence": confidence}

    if len(event_local_group) <= 1:
        ctx.logger.info(f"No peers available. Auto-accepting event {event_id}.")
        await final_actions_after_consensus(ctx, pending_events[event_id], registered_location)
        async with PENDING_LOCK: del pending_events[event_id]
        return

    request_data = {"event_id": event_id, "location": registered_location, "sound_class": predicted_class, "decibel": msg.decibel}
    validation_request = ValidationRequest(**request_data, public_key=export_public_key_hex(public_key), signature=private_key.sign(get_digest(request_data)).hex())

    for peer_address in event_local_group:
        if peer_address != str(agent.address):
            await ctx.send(peer_address, validation_request)

@validation_protocol.on_message(model=ValidationRequest, replies=set())
async def handle_validation_request(ctx: Context, sender: str, msg: ValidationRequest):
    is_plausible = smart_consensus.validate_event(msg.dict(), LOCAL_SENSOR_STATE, CONFIG) if LOCAL_SENSOR_STATE else False
    response_data = {"event_id": msg.event_id, "validated": is_plausible}
    await ctx.send(sender, ValidationResponse(**response_data, public_key=export_public_key_hex(public_key), signature=private_key.sign(get_digest(response_data)).hex()))

@validation_protocol.on_message(model=ValidationResponse, replies=set())
async def handle_validation_response(ctx: Context, sender: str, msg: ValidationResponse):
    async with PENDING_LOCK:
        if msg.event_id not in pending_events: return
        event = pending_events[msg.event_id]
        
        try:
            if not PublicKey(bytes.fromhex(msg.public_key)).verify(get_digest({"event_id": msg.event_id, "validated": msg.validated}), bytes.fromhex(msg.signature)):
                ctx.logger.warning(f"INVALID SIGNATURE from {sender}. Discarding."); return
        except Exception as e:
            ctx.logger.error(f"Signature verification failed for {sender}: {e}"); return
        
        event["responses"].append(msg)
        
        registered_location = read_registry()[event["raw_data"]['device_id']]
        num_peers_in_group = len(get_local_peer_group(registered_location)) - 1
        
        positive_responses = sum(1 for res in event["responses"] if res.validated)
        
        if positive_responses >= math.ceil(num_peers_in_group * QUORUM_RATIO):
            ctx.logger.info(f"CONSENSUS REACHED for event {msg.event_id}.")
            await final_actions_after_consensus(ctx, event, registered_location)
            del pending_events[msg.event_id]
        elif len(event["responses"]) >= num_peers_in_group:
            ctx.logger.warning(f"CONSENSUS FAILED for event {msg.event_id}.")
            mac_address = event["raw_data"]["device_id"]
            SENSOR_FAILURE_COUNTS[mac_address] = SENSOR_FAILURE_COUNTS.get(mac_address, 0) + 1
            if SENSOR_FAILURE_COUNTS[mac_address] >= FAILURE_THRESHOLD:
                cleanup_sensor_and_agent(mac_address)
                SENSOR_FAILURE_COUNTS[mac_address] = 0
            del pending_events[msg.event_id]

# ======================================================================================
# --- MQTT Client Logic ---
# ======================================================================================

def on_connect(client, userdata, flags, rc, properties):
    if rc == 0: 
        client.subscribe(f"{MQTT_TOPIC_PREFIX}/{MAC_ADDRESS}")
        print(f"✅ MQTT client subscribed to topic for {MAC_ADDRESS}")
    else: 
        print(f"❌ Failed to connect to MQTT broker, return code {rc}")

def on_message(client, userdata, msg):
    try: 
        mqtt_message_queue.put(SensorData(**json.loads(msg.payload.decode())))
    except Exception as e: 
        print(f"Error processing MQTT message: {e}")

def start_mqtt_client():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, f"device_node_mqtt_{MAC_ADDRESS}")
    client.on_connect, client.on_message = on_connect, on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

def mqtt_publisher_thread():
    """Thread to publish sensor data to MQTT"""
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, f"sensor_publisher_{MAC_ADDRESS}")
    
    def on_publish_connect(client, userdata, flags, rc, properties):
        if rc == 0:
            print("✅ MQTT Publisher connected successfully")
        else:
            print(f"❌ MQTT Publisher failed to connect, return code {rc}")
    
    client.on_connect = on_publish_connect
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
    
    while True:
        try:
            # Get sensor data from queue (blocks until data available)
            sensor_data = sensor_data_queue.get(timeout=5)
            
            # Publish to MQTT
            topic = f"{MQTT_TOPIC_PREFIX}/{MAC_ADDRESS}"
            payload = json.dumps(sensor_data.dict())
            
            result = client.publish(topic, payload)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"📡 Published sensor data: dB={sensor_data.decibel:.2f}")
            else:
                print(f"❌ Failed to publish sensor data: {result.rc}")
                
            sensor_data_queue.task_done()
            
        except queue.Empty:
            # Timeout occurred, continue loop
            continue
        except Exception as e:
            print(f"❌ Error in MQTT publisher: {e}")
            time.sleep(1)

# ======================================================================================
# --- FastAPI Setup ---
# ======================================================================================

app = FastAPI(title="ECHONET Super Combined Device Node", version="1.0.0")
router = APIRouter()

async def db_data_stream():
    """Stream dB data via Server-Sent Events"""
    mac_address = get_mac_address()
    while True:
        # Compute average dB
        if latest_db_values:
            avg_db = sum(latest_db_values) / len(latest_db_values)
        else:
            avg_db = 0.0

        # Prepare JSON-safe data
        data = {
            "avg_db": round(float(avg_db), 2),   # ensure plain float
            "mac_address": mac_address,
            "timestamp": datetime.now().isoformat(),
            "agent_address": str(agent.address),
            "agent_name": AGENT_NAME
        }

        yield f"data: {json.dumps(data)}\n\n"  # proper JSON for SSE
        await asyncio.sleep(1)  # stream every 1 second

@router.get("/stream")
async def stream_db_data():
    """Stream real-time audio dB data"""
    return StreamingResponse(db_data_stream(), media_type="text/event-stream")

@router.get("/status")
async def get_status():
    """Get current device status"""
    return {
        "mac_address": MAC_ADDRESS,
        "agent_name": AGENT_NAME,
        "agent_address": str(agent.address),
        "current_db": latest_db_values[-1] if latest_db_values else 0.0,
        "avg_db": sum(latest_db_values) / len(latest_db_values) if latest_db_values else 0.0,
        "audio_active": audio_processing_active,
        "pending_events": len(pending_events),
        "sensor_failures": SENSOR_FAILURE_COUNTS.get(MAC_ADDRESS, 0)
    }

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

app.include_router(router)

# ======================================================================================
# --- Agent Intervals ---
# ======================================================================================

@agent.on_interval(period=0.5)
async def process_mqtt_queue(ctx: Context):
    """Process incoming MQTT messages"""
    if not mqtt_message_queue.empty():
        try:
            sensor_data = mqtt_message_queue.get_nowait()
            ctx.logger.info(f"Pulled sensor data from MQTT queue for device: {sensor_data.device_id}")
            await handle_sensor_data(ctx, agent.address, sensor_data)
        except queue.Empty: 
            pass
        except Exception as e: 
            ctx.logger.error(f"Error processing item from queue: {e}")

@agent.on_interval(period=60.0)
async def cleanup_old_events(ctx: Context):
    """Clean up old pending events"""
    current_time = datetime.now(timezone.utc)
    cutoff_time = current_time - timedelta(minutes=5)
    
    async with PENDING_LOCK:
        events_to_remove = []
        for event_id, event_data in pending_events.items():
            if event_data["timestamp"] < cutoff_time:
                events_to_remove.append(event_id)
        
        for event_id in events_to_remove:
            del pending_events[event_id]
            ctx.logger.info(f"Cleaned up expired event: {event_id}")

# ======================================================================================
# --- Audio Processing Thread ---
# ======================================================================================

def start_audio_processing():
    """Start audio processing in a separate thread"""
    global audio_processing_active
    
    def audio_thread():
        global audio_processing_active
        try:
            setup_csv()
            audio_processing_active = True
            
            with sd.InputStream(callback=audio_callback,
                                channels=CHANNELS,
                                samplerate=SAMPLERATE,
                                blocksize=BLOCKSIZE):
                print("🎤 Audio processing started...")
                
                # Keep the audio stream running
                while audio_processing_active:
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            print("\n🛑 Audio processing stopped by user")
        except Exception as e:
            print(f"❌ Audio processing error: {e}")
        finally:
            audio_processing_active = False
    
    thread = threading.Thread(target=audio_thread, daemon=True)
    thread.start()
    return thread

# ======================================================================================
# --- Main Execution ---
# ======================================================================================

def run_fastapi_server():
    """Run FastAPI server in a separate thread"""
    def fastapi_thread():
        uvicorn.run(app, host=FASTAPI_HOST, port=FASTAPI_PORT, log_level="info")
    
    thread = threading.Thread(target=fastapi_thread, daemon=True)
    thread.start()
    return thread

if __name__ == "__main__":
    # Include the validation protocol in the agent
    agent.include(validation_protocol)
    
    print("🚀 Starting ECHONET Super Combined Device Node...")
    print(f"📍 MAC Address: {MAC_ADDRESS}")
    print(f"🤖 Agent Name: {AGENT_NAME}")
    print(f"📬 Agent Address: {agent.address}")
    
    try:
        # Start all components
        print("🎤 Starting audio processing...")
        audio_thread = start_audio_processing()
        
        print("📡 Starting MQTT publisher...")
        mqtt_pub_thread = threading.Thread(target=mqtt_publisher_thread, daemon=True)
        mqtt_pub_thread.start()
        
        print("📡 Starting MQTT subscriber...")
        mqtt_sub_thread = threading.Thread(target=start_mqtt_client, daemon=True)
        mqtt_sub_thread.start()
        
        print(f"🌐 Starting FastAPI server on http://{FASTAPI_HOST}:{FASTAPI_PORT}")
        fastapi_thread = run_fastapi_server()
        
        # Small delay to let FastAPI start
        time.sleep(2)
        
        print("🤖 Starting uAgent...")
        print(f"✅ All systems operational!")
        print(f"📊 FastAPI endpoints:")
        print(f"   • Real-time stream: http://{FASTAPI_HOST}:{FASTAPI_PORT}/stream")
        print(f"   • Status: http://{FASTAPI_HOST}:{FASTAPI_PORT}/status") 
        print(f"   • Health: http://{FASTAPI_HOST}:{FASTAPI_PORT}/health")
        
        # Run the agent (this blocks)
        agent.run()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down ECHONET Super Combined Device Node...")
        audio_processing_active = False
    except Exception as e:
        print(f"❌ Critical error: {e}")
        sys.exit(1)