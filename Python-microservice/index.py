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
    location: Dict[str, float]  # {"latitude": float, "longitude": float}
    decibel: float
    event: str
    timestamp: str

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
    
    return {
        "device_id": f"DEVICE_{random.randint(1000, 9999)}",
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
    """Submit device sensor data"""
    data_dict = data.dict()
    submitted_data.append(data_dict)
    return {
        "status": "success", 
        "message": "Device data submitted successfully",
        "data": data_dict,
        "total_submitted": len(submitted_data)
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