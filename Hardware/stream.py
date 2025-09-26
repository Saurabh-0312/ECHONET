from fastapi import FastAPI, APIRouter
from fastapi.responses import StreamingResponse
import asyncio
import random
import uuid
from datetime import datetime

app = FastAPI()
router = APIRouter()

def get_mac_address():
    """Get the MAC address of the device"""
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return ":".join([mac[e:e+2] for e in range(0, 11, 2)])

async def random_data_stream():
    mac_address = get_mac_address()
    while True:
        value = random.randint(30, 90)
        timestamp = datetime.now().isoformat()
        data = {
            "value": value,
            "mac_address": mac_address,
            "timestamp": timestamp
        }
        yield f"data: {data}\n\n"   # SSE format
        await asyncio.sleep(1)       # stream 1 value per second

@router.get("/stream")
async def stream_random_data():
    return StreamingResponse(random_data_stream(), media_type="text/event-stream")

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5007)