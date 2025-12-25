# backend/tests/test_idempotency.py
import pytest
from datetime import datetime, timedelta
from app.idempotency import IdempotencyStore, check_idempotency, save_idempotency


def test_idempotency_store_saves_and_retrieves():
    """Store should save and retrieve idempotency keys"""
    store = IdempotencyStore()

    key = "test-key-123"
    response = {"id": 1, "status": "created"}

    store.save(key, response)

    cached = store.get(key)
    assert cached == response


def test_idempotency_store_returns_none_for_unknown_key():
    """Store should return None for unknown keys"""
    store = IdempotencyStore()

    result = store.get("unknown-key")
    assert result is None


def test_idempotency_store_expires_old_keys():
    """Store should expire keys after TTL"""
    store = IdempotencyStore(ttl_seconds=1)

    key = "expiring-key"
    store.save(key, {"test": True})

    # Should exist immediately
    assert store.get(key) is not None

    # Wait for expiry
    import time
    time.sleep(1.1)

    # Should be expired
    assert store.get(key) is None
