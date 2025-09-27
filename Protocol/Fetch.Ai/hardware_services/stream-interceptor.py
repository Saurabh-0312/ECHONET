import requests
import json
import paho.mqtt.client as mqtt
import time

# --- Config ---
SOURCE_URL = "http://192.168.232.245:5007/stream"  # Your incoming stream URL
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC_PREFIX = "echonet/sensors"

# Dictionary to store MQTT clients per MAC
mqtt_clients = {}

def get_mqtt_client(mac_address):
    """Return a connected MQTT client for a given MAC. Create if not exists."""
    if mac_address not in mqtt_clients:
        client = mqtt.Client(client_id=f"interceptor_{mac_address}")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        mqtt_clients[mac_address] = client
    return mqtt_clients[mac_address]

def publish_sensor(mac_address, decibel_value, timestamp):
    """Publish a single sensor reading to MQTT."""
    topic = f"{MQTT_TOPIC_PREFIX}/{mac_address}"
    payload = {
        "device_id": mac_address,
        "timestamp": timestamp,
        "decibel": decibel_value
    }
    client = get_mqtt_client(mac_address)
    client.publish(topic, json.dumps(payload))
    print(f"[FORWARD] Published to {topic}: {payload}")

def process_stream_line(line):
    """Process a single JSON line from the stream."""
    try:
        decoded = line.decode("utf-8").replace("data: ", "").strip()
        if not decoded:
            return
        
        data = json.loads(decoded)  # Parse JSON
        mac_address = data["mac_address"].strip().upper()
        decibel_value = float(data["avg_db"])
        timestamp = data["timestamp"].strip()
        
        publish_sensor(mac_address, decibel_value, timestamp)
    except Exception as e:
        print(f"[ERROR] Processing line failed: {e} | Line: {line}")

def main():
    print("[INFO] Starting interceptor...")
    with requests.get(SOURCE_URL, stream=True) as r:
        for line in r.iter_lines():
            if line:
                process_stream_line(line)
            time.sleep(0.01)  # small sleep to prevent CPU overuse

if __name__ == "__main__":
    main()
