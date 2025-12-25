# backend/app/idempotency.py
"""
Idempotency Key Support

Prevents duplicate submissions by caching responses.
Uses in-memory store for simplicity (can upgrade to Redis later).
"""
from datetime import datetime, timedelta, UTC
from typing import Any, Optional
from dataclasses import dataclass
from threading import Lock


@dataclass
class CachedResponse:
    """Cached idempotency response"""
    response: Any
    created_at: datetime
    expires_at: datetime


class IdempotencyStore:
    """
    In-memory idempotency key store.
    Thread-safe with automatic expiration.
    """

    def __init__(self, ttl_seconds: int = 86400):  # 24 hours default
        self._store: dict[str, CachedResponse] = {}
        self._lock = Lock()
        self._ttl_seconds = ttl_seconds

    def get(self, key: str) -> Optional[Any]:
        """Get cached response for key, or None if not found/expired"""
        with self._lock:
            if key not in self._store:
                return None

            cached = self._store[key]

            # Check expiration
            if datetime.now(UTC) > cached.expires_at:
                del self._store[key]
                return None

            return cached.response

    def save(self, key: str, response: Any) -> None:
        """Save response for key"""
        with self._lock:
            now = datetime.now(UTC)
            self._store[key] = CachedResponse(
                response=response,
                created_at=now,
                expires_at=now + timedelta(seconds=self._ttl_seconds)
            )

    def cleanup(self) -> int:
        """Remove expired entries, return count removed"""
        with self._lock:
            now = datetime.now(UTC)
            expired = [k for k, v in self._store.items() if now > v.expires_at]
            for k in expired:
                del self._store[k]
            return len(expired)


# Global store instance
_store = IdempotencyStore()


def check_idempotency(key: Optional[str]) -> Optional[Any]:
    """Check if we have a cached response for this key"""
    if not key:
        return None
    return _store.get(key)


def save_idempotency(key: Optional[str], response: Any) -> None:
    """Save response for idempotency key"""
    if key:
        _store.save(key, response)


def get_idempotency_store() -> IdempotencyStore:
    """Get the global idempotency store"""
    return _store
