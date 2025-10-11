# Hedara Python Microservice

Lightweight FastAPI service that demonstrates how to integrate with the Hedera network using a safe wrapper around the Hedera Python SDK.

Quick start

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Configure environment variables (example for Testnet):

```bash
export HEDERA_NETWORK=testnet
export HEDERA_OPERATOR_ID=0.0.xxxx
export HEDERA_OPERATOR_KEY=302e020100300506032b6570...
export PORT=5100
```

3. Run the service:

```bash
uvicorn app:app --host 0.0.0.0 --port 5100
```

Endpoints:

- GET / : health
- GET /hedera/status : check SDK availability and configured operator
- POST /hedera/transfer : create or simulate an HBAR transfer

Notes:
- This project intentionally provides mock responses when the Hedera SDK isn't installed to make local development easier.
