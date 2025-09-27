from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import random
import json
from datetime import datetime
import os

app = FastAPI(title="Fluence Python Worker", description="Device data collection and visualization API")

# Store for submitted device data
submitted_data = []

# Allow CORS for local frontend/dev. In production, lock this down to the frontend origin(s).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DeviceData(BaseModel):
    device_id: str
    mac_address: str  # MAC address as unique identifier
    location: Dict[str, float]  # {"latitude": float, "longitude": float}
    decibel: float
    event: str
    timestamp: str

class EnrichedPacket(BaseModel):
    """Model for enriched packet data from external sources"""
    mac_address: str
    device_id: str = None
    latitude: float
    longitude: float
    decibel_level: float = None
    noise_level: float = None
    event_type: str = "sensor_data"
    timestamp: str = None
    metadata: Dict[str, Any] = {}

def generate_device_data():
    """Generate realistic device sensor data"""
    cities = [
        (40.7128, -74.0060, "New York"),
        (34.0522, -118.2437, "Los Angeles"), 
        (51.5074, -0.1278, "London"),
        (35.6762, 139.6503, "Tokyo"),
        (48.8566, 2.3522, "Paris"),
        (55.7558, 37.6173, "Moscow"),
        (28.6139, 77.2090, "Delhi"),
        (-33.8688, 151.2093, "Sydney"),
        (19.4326, -99.1332, "Mexico City"),
        (52.5200, 13.4050, "Berlin")
    ]
    
    lat, lng, city = random.choice(cities)
    # Add some randomness around the city center
    lat += random.uniform(-0.5, 0.5)
    lng += random.uniform(-0.5, 0.5)
    
    events = ["traffic", "construction", "emergency", "normal", "event", "industrial"]
    
    # Generate realistic MAC addresses for demo data
    mac_address = ":".join([f"{random.randint(0, 255):02x}" for _ in range(6)])
    
    return {
        "device_id": f"DEVICE_{random.randint(1000, 9999)}",
        "mac_address": mac_address,
        "location": {
            "latitude": round(lat, 4),
            "longitude": round(lng, 4)
        },
        "decibel": round(random.uniform(30.0, 120.0), 1),
        "event": random.choice(events),
        "timestamp": datetime.now().isoformat(),
        "city": city
    }

@app.get("/")
def read_root():
    return {"message": "Fluence Python Worker is running!", "endpoints": ["/hello", "/data", "/heatmap", "/backend/"]}

@app.get("/hello")
def hello_world():
    return {"message": "Hello from Fluence Python Worker!", "timestamp": datetime.now().isoformat()}

@app.post("/data/submit")
def submit_device_data(data: DeviceData):
    """Submit device sensor data - updates existing device if MAC address exists"""
    data_dict = data.dict()
    
    # Check if device with same MAC address already exists
    existing_device_index = None
    for i, existing_data in enumerate(submitted_data):
        if existing_data.get("mac_address") == data.mac_address:
            existing_device_index = i
            break
    
    if existing_device_index is not None:
        # Update existing device data
        submitted_data[existing_device_index].update(data_dict)
        message = f"Device data updated for MAC address {data.mac_address}"
        updated_data = submitted_data[existing_device_index]
    else:
        # Add new device data
        submitted_data.append(data_dict)
        message = f"New device data added for MAC address {data.mac_address}"
        updated_data = data_dict
    
    return {
        "status": "success", 
        "message": message,
        "data": updated_data,
        "total_submitted": len(submitted_data),
        "is_update": existing_device_index is not None
    }

@app.get("/data")
def get_all_data():
    """Get all data (generated + submitted) for analysis"""
    # Combine generated sample data with submitted data
    generated = [generate_device_data() for _ in range(20)]
    all_data = generated + submitted_data
    return {
        "total_count": len(all_data),
        "generated_count": len(generated),
        "submitted_count": len(submitted_data),
        "data": all_data
    }

@app.get("/data/submitted")
def get_submitted_data():
    """Get only the submitted device data"""
    return {
        "count": len(submitted_data),
        "data": submitted_data
    }

@app.get("/data/device/{mac_address}")
def get_device_by_mac(mac_address: str):
    """Get device data by MAC address"""
    for device_data in submitted_data:
        if device_data.get("mac_address") == mac_address:
            return {
                "found": True,
                "data": device_data
            }
    
    raise HTTPException(status_code=404, detail=f"Device with MAC address {mac_address} not found")

@app.post("/ingest")
def ingest_enriched_packet(packet: EnrichedPacket):
    """
    Ingest enriched packet data with coordinates from external sources.
    Updates existing device if MAC address exists, otherwise creates new entry.
    """
    # Convert enriched packet to device data format
    device_data = {
        "device_id": packet.device_id or f"DEVICE_{packet.mac_address.replace(':', '_')}",
        "mac_address": packet.mac_address,
        "location": {
            "latitude": packet.latitude,
            "longitude": packet.longitude
        },
        "decibel": packet.decibel_level or packet.noise_level or 0.0,
        "event": packet.event_type,
        "timestamp": packet.timestamp or datetime.now().isoformat(),
        "metadata": packet.metadata
    }
    
    # Check if device with same MAC address already exists
    existing_device_index = None
    for i, existing_data in enumerate(submitted_data):
        if existing_data.get("mac_address") == packet.mac_address:
            existing_device_index = i
            break
    
    if existing_device_index is not None:
        # Update existing device data
        submitted_data[existing_device_index].update(device_data)
        message = f"Device coordinates and data updated for MAC address {packet.mac_address}"
        updated_data = submitted_data[existing_device_index]
        is_update = True
    else:
        # Add new device data
        submitted_data.append(device_data)
        message = f"New device ingested for MAC address {packet.mac_address}"
        updated_data = device_data
        is_update = False
    
    return {
        "status": "success",
        "message": message,
        "data": updated_data,
        "total_devices": len(submitted_data),
        "is_update": is_update,
        "coordinates": {
            "latitude": packet.latitude,
            "longitude": packet.longitude
        }
    }

@app.get("/heatmap", response_class=HTMLResponse)
def heatmap_visualization():
    """World map heatmap visualization of device data"""
    # For frontend integration: expose JSON data endpoint. Keep /heatmap as a small info page
    return HTMLResponse(content="<html><body><h3>Heatmap frontend is expected to be served from the React app. Use /heatmap/data for JSON.</h3></body></html>")


@app.get("/backend/", response_class=HTMLResponse)
def backend_root():
    """Compatibility endpoint for reverse-proxy path /backend/"""
    return HTMLResponse(content="<html><body><h3>Fluence Python Worker backend root. Use /data or /heatmap/data for JSON endpoints.</h3></body></html>")


@app.get("/heatmap/data")
def heatmap_data():
    """Return generated + submitted data as JSON for frontend heatmap."""
    sample_data = [generate_device_data() for _ in range(30)]
    all_data = sample_data + submitted_data

    heatmap_data = []
    for item in all_data:
        heatmap_data.append({
            "lat": item["location"]["latitude"],
            "lng": item["location"]["longitude"],
            "value": item["decibel"],
            "device_id": item["device_id"],
            "event": item["event"],
            "timestamp": item["timestamp"],
            "is_submitted": item in submitted_data,
            "city": item.get("city")
        })

    return {
        "total": len(all_data),
        "submitted": len(submitted_data),
        "data": heatmap_data,
    }


@app.get("/healthz")
def health_check():
    """Simple health check for reverse-proxy and container orchestrators"""
    return {"status": "ok", "service": "fluence-python-worker", "time": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    # Use PORT env var if provided so reverse-proxy or docker can map ports easily
    # Default to 5000 because the container listens on 5000 and docker-compose maps host 5001 -> container 5000
    port = int(os.environ.get("PORT", "5000"))
    uvicorn.run(app, host="0.0.0.0", port=port)