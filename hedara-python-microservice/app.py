from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from datetime import datetime

# Try to import Hedera SDK; provide graceful fallback if not installed
try:
    from hedera import (Client, AccountId, PrivateKey, Hbar)
    HEDERA_AVAILABLE = True
except Exception:
    Client = None
    AccountId = None
    PrivateKey = None
    Hbar = None
    HEDERA_AVAILABLE = False

app = FastAPI(title="Hedara Python Microservice", description="FastAPI service with optional Hedera SDK integration")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HealthResponse(BaseModel):
    status: str
    time: str

class HederaStatus(BaseModel):
    hedera_available: bool
    network: Optional[str] = None
    operator: Optional[str] = None

@app.get("/", response_model=HealthResponse)
def root():
    return HealthResponse(status="ok", time=datetime.utcnow().isoformat())

@app.get("/hedera/status", response_model=HederaStatus)
def hedera_status():
    """Return hedera client availability and operator info (if configured)"""
    if not HEDERA_AVAILABLE:
        return HederaStatus(hedera_available=False)

    # Build client from env vars if present
    network = os.environ.get("HEDERA_NETWORK", "testnet")
    operator_id = os.environ.get("HEDERA_OPERATOR_ID")
    operator_key = os.environ.get("HEDERA_OPERATOR_KEY")

    operator = None
    if operator_id:
        operator = operator_id

    return HederaStatus(hedera_available=True, network=network, operator=operator)

class TransferRequest(BaseModel):
    to_account: str
    amount_hbar: float

@app.post("/hedera/transfer")
def create_transfer(req: TransferRequest):
    """Creates a simple HBAR transfer using the Hedera SDK if available and configured.
    This function will validate environment operator credentials and return a mock response when
    the SDK is not installed or credentials are missing.
    """
    if not HEDERA_AVAILABLE:
        # return a mock response for environments without the SDK
        return {"status": "mock", "message": "Hedera SDK not installed; this is a dry-run.", "request": req.dict()}

    network = os.environ.get("HEDERA_NETWORK", "testnet")
    operator_id = os.environ.get("HEDERA_OPERATOR_ID")
    operator_key = os.environ.get("HEDERA_OPERATOR_KEY")

    if not operator_id or not operator_key:
        raise HTTPException(status_code=400, detail="Operator credentials not configured in environment")

    # initialize client
    client = Client.for_name(network)
    client.set_operator(AccountId.from_string(operator_id), PrivateKey.from_string(operator_key))

    # Build a simple transfer - note: hedera-python SDK API may vary; this is a conservative example
    try:
        from hedera import TransferTransaction
        tx = TransferTransaction().add_hbar_transfer(AccountId.from_string(operator_id), Hbar.from_tinybars(int(-req.amount_hbar * 100_000_000)))
        tx.add_hbar_transfer(AccountId.from_string(req.to_account), Hbar.from_tinybars(int(req.amount_hbar * 100_000_000)))
        # Sign and execute
        tx_response = tx.execute(client)
        receipt = tx_response.get_receipt(client)
        return {"status": "success", "transaction_receipt": str(receipt)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transfer failed: {e}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "5100"))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
