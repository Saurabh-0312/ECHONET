import sounddevice as sd
import numpy as np
import csv
from datetime import datetime
from fastapi import FastAPI, APIRouter
from fastapi.responses import StreamingResponse
import asyncio
import uuid
import json
import uvicorn

# ---------------- Audio settings ----------------
samplerate = 48000   # match your USB mic
blocksize = 1024
channels = 1
csv_file = "mic_db_log.csv"
# -------------------------------------------------

# Shared variable to store latest dB values
latest_db_values = []

# Setup CSV file
with open(csv_file, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["Timestamp", "dB"])

# ---------------- Audio callback ----------------
def audio_callback(indata, frames, time_info, status):
    if status:
        print(status)

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
    with open(csv_file, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, db])

    # ASCII visualization
    bar_length = 50
    rms_len = int(np.clip(rms * 10, 0, 1) * bar_length) + int(0.3 * bar_length)
    peak_len = int(np.clip(np.max(np.abs(audio_data)), 0, 1) * bar_length)

    rms_bar = '█' * min(rms_len, bar_length)
    peak_bar = '█' * min(peak_len, bar_length)

    print(f"\rRMS: {rms_bar:<50} | Peak: {peak_bar:<50} | dB: {db:.2f}", end='', flush=True)

# ---------------- FastAPI setup ----------------
app = FastAPI()
router = APIRouter()

def get_mac_address():
    """Get MAC address of the device"""
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return ":".join([mac[e:e+2] for e in range(0, 11, 2)])

async def db_data_stream():
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
            "timestamp": datetime.now().isoformat()
        }

        yield f"data: {json.dumps(data)}\n\n"  # proper JSON for SSE
        await asyncio.sleep(1)  # stream every 1 second

@router.get("/stream")
async def stream_db_data():
    return StreamingResponse(db_data_stream(), media_type="text/event-stream")

app.include_router(router)

# ---------------- Run both mic + server ----------------
if __name__ == "__main__":
    try:
        with sd.InputStream(callback=audio_callback,
                            channels=channels,
                            samplerate=samplerate,
                            blocksize=blocksize):
            print("🎤 Live audio monitor + FastAPI SSE running at http://0.0.0.0:5007/stream")
            uvicorn.run(app, host="0.0.0.0", port=5007)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopped audio monitoring")
    except Exception as e:
        print(f"\n❌ Error: {e}")