"""Lightweight Hedera client wrapper with safe fallbacks for environments without the SDK.

This module exposes a minimal API: `get_client()` to create a configured client or `None` if unavailable,
and `create_transfer()` which will either perform a real transfer or return a mock response.
"""
from typing import Optional
import os

try:
    from hedera import Client, AccountId, PrivateKey, Hbar, TransferTransaction
    _SDK = True
except Exception:
    Client = None
    AccountId = None
    PrivateKey = None
    Hbar = None
    TransferTransaction = None
    _SDK = False


def get_client() -> Optional[Client]:
    """Return a configured Hedera client or None if SDK/credentials missing."""
    if not _SDK:
        return None

    network = os.environ.get("HEDERA_NETWORK", "testnet")
    operator_id = os.environ.get("HEDERA_OPERATOR_ID")
    operator_key = os.environ.get("HEDERA_OPERATOR_KEY")

    client = Client.for_name(network)
    if operator_id and operator_key:
        client.set_operator(AccountId.from_string(operator_id), PrivateKey.from_string(operator_key))
    return client


def create_transfer(to_account: str, amount_hbar: float):
    """Perform or simulate hbar transfer.

    Returns a dict describing the result. If SDK not available, returns a mock response.
    """
    if not _SDK:
        return {"status": "mock", "message": "SDK not installed", "to": to_account, "amount_hbar": amount_hbar}

    client = get_client()
    if not client:
        return {"status": "error", "message": "Client not configured"}

    operator_id = os.environ.get("HEDERA_OPERATOR_ID")
    try:
        tx = TransferTransaction().add_hbar_transfer(AccountId.from_string(operator_id), Hbar.from_tinybars(int(-amount_hbar * 100_000_000)))
        tx.add_hbar_transfer(AccountId.from_string(to_account), Hbar.from_tinybars(int(amount_hbar * 100_000_000)))
        tx_response = tx.execute(client)
        receipt = tx_response.get_receipt(client)
        return {"status": "success", "receipt": str(receipt)}
    except Exception as e:
        return {"status": "error", "message": str(e)}
