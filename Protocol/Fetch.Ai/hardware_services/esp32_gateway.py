import paho.mqtt.client as mqtt
import json
import asyncio
import sys
import os
import threading
import queue

# --- Path Configuration ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
SENSOR_REGISTRY_FILE = os.path.join(PROJECT_ROOT, "sensor_registry.json")

# This absolute import will now work correctly with the updated schema
from fetch_services.agents.schemas import SensorData

if len(sys.argv) < 2:
    print("Usage: python esp32_gateway.py <mac_address>")
    sys.exit(1)

MAC_ADDRESS = sys.argv[1]

# --- Dynamically find the agent address from the shared config file ---
try:
    with open(SENSOR_REGISTRY_FILE, 'r') as f:
        registry = json.load(f)
        agent_config = registry[MAC_ADDRESS]
        from uagents.crypto import Identity
        AGENT_ADDRESS = Identity.from_seed(agent_config['agent_seed'], 0).address
except (FileNotFoundError, KeyError):
    print(f"Error: Could not find configuration for MAC address {MAC_ADDRESS}")
    sys.exit(1)

# --- MQTT and Agent Logic ---
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC_PREFIX = "echonet/sensors"

message_queue = queue.Queue()

from uagents import Agent, Context

# Use a dynamic port for each gateway's internal agent to prevent conflicts
gateway_agent_port = 8100 + (hash(MAC_ADDRESS) % 100)

sender_agent = Agent(
    name=f"gateway_sender_{MAC_ADDRESS}", 
    seed=f"{MAC_ADDRESS}_seed",
    port=gateway_agent_port
)

@sender_agent.on_interval(period=0.1)
async def process_message_queue(ctx: Context):
    """Periodically checks the queue for new messages and forwards them."""
    if not message_queue.empty():
        destination, message = message_queue.get()
        print(f"[{sender_agent.name}] Forwarding message from queue to {destination}")
        await ctx.send(destination, message)

def run_sender_agent():
    """Function to run the agent's event loop."""
    sender_agent.run()

def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        topic = f"{MQTT_TOPIC_PREFIX}/{MAC_ADDRESS}"
        client.subscribe(topic)
        print(f"Gateway for {MAC_ADDRESS} connected and subscribed to {topic}")
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    """
    This function is called by the MQTT client. It safely puts the message into the queue.
    """
    try:
        payload = json.loads(msg.payload.decode())
        # The gateway now expects the new, simplified SensorData format
        sensor_data = SensorData(**payload)
        message_queue.put((AGENT_ADDRESS, sensor_data))
    except Exception as e:
        print(f"Error processing message: {e}")

if __name__ == "__main__":
    agent_thread = threading.Thread(target=run_sender_agent, daemon=True)
    agent_thread.start()
    
    print(f"Sender agent for {MAC_ADDRESS} is running in the background on port {gateway_agent_port}.")
    
    print(f"Starting MQTT listener for MAC {MAC_ADDRESS}...")
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, f"gateway_{MAC_ADDRESS}")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

