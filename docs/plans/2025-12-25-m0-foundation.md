# Milestone 0: Foundation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Normalize schema, add feature flags, structured logging, and idempotency keys to prepare for RestaurantOS evolution.

**Architecture:**
- Replace hardcoded `kasa_*` and `pos_*` columns in CashDifference with normalized `CashDifferenceItem` table
- Add config-based feature flags system
- Add structured JSON logging with request context
- Add idempotency middleware for POST endpoints

**Tech Stack:** FastAPI, SQLAlchemy, Alembic, pytest, Python logging

---

## Task 1: Add Feature Flags System

**Files:**
- Create: `backend/app/features.py`
- Modify: `backend/app/config.py`
- Create: `backend/tests/test_features.py`

**Step 1: Write failing test**

```python
# backend/tests/test_features.py
import pytest
from app.features import Features, is_feature_enabled, get_enabled_features


def test_feature_flags_default_values():
    """Feature flags should have sensible defaults"""
    # These should be disabled by default
    assert is_feature_enabled(Features.IMPORT_HUB) == False
    assert is_feature_enabled(Features.AI_INSIGHTS) == False
    assert is_feature_enabled(Features.MULTI_TENANCY) == False
    assert is_feature_enabled(Features.DYNAMIC_PLATFORMS) == False


def test_feature_can_be_enabled_via_env(monkeypatch):
    """Features can be enabled via environment variables"""
    monkeypatch.setenv("FEATURE_IMPORT_HUB", "true")

    # Need to reload to pick up env change
    from importlib import reload
    import app.features
    reload(app.features)
    from app.features import is_feature_enabled, Features

    assert is_feature_enabled(Features.IMPORT_HUB) == True


def test_get_enabled_features_returns_dict():
    """get_enabled_features returns all flags as dict"""
    result = get_enabled_features()
    assert isinstance(result, dict)
    assert "import_hub" in result
    assert "ai_insights" in result
```

**Step 2: Run test to verify it fails**

```bash
cd backend && source ../venv/bin/activate && pytest tests/test_features.py -v
```

Expected: FAIL - ModuleNotFoundError: No module named 'app.features'

**Step 3: Create feature flags module**

```python
# backend/app/features.py
"""
Feature Flags System

Enable/disable features via environment variables:
- FEATURE_IMPORT_HUB=true
- FEATURE_AI_INSIGHTS=true
- FEATURE_MULTI_TENANCY=true
- FEATURE_DYNAMIC_PLATFORMS=true
"""
import os
from enum import Enum
from functools import lru_cache


class Features(str, Enum):
    """Available feature flags"""
    IMPORT_HUB = "import_hub"
    AI_INSIGHTS = "ai_insights"
    MULTI_TENANCY = "multi_tenancy"
    DYNAMIC_PLATFORMS = "dynamic_platforms"


def _get_env_bool(key: str, default: bool = False) -> bool:
    """Get boolean from environment variable"""
    val = os.getenv(key, str(default)).lower()
    return val in ("true", "1", "yes", "on")


def is_feature_enabled(feature: Features) -> bool:
    """Check if a feature is enabled"""
    env_key = f"FEATURE_{feature.value.upper()}"
    return _get_env_bool(env_key, default=False)


def get_enabled_features() -> dict[str, bool]:
    """Get all feature flags as dictionary"""
    return {f.value: is_feature_enabled(f) for f in Features}


def require_feature(feature: Features):
    """Decorator to require a feature flag for an endpoint"""
    from functools import wraps
    from fastapi import HTTPException

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not is_feature_enabled(feature):
                raise HTTPException(
                    status_code=404,
                    detail=f"Feature '{feature.value}' is not enabled"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

**Step 4: Run test to verify it passes**

```bash
cd backend && pytest tests/test_features.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/features.py backend/tests/test_features.py
git commit -m "feat: add feature flags system for controlled rollout"
```

---

## Task 2: Add Structured Logging

**Files:**
- Create: `backend/app/logging_config.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_logging.py`

**Step 1: Write failing test**

```python
# backend/tests/test_logging.py
import pytest
import json
import logging
from io import StringIO
from app.logging_config import setup_logging, get_logger


def test_logger_outputs_json():
    """Logger should output JSON formatted logs"""
    stream = StringIO()
    handler = logging.StreamHandler(stream)

    logger = get_logger("test")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    logger.info("Test message", extra={"user_id": 1, "branch_id": 2})

    output = stream.getvalue()
    # Should be valid JSON
    log_entry = json.loads(output.strip())
    assert log_entry["message"] == "Test message"
    assert log_entry["user_id"] == 1
    assert log_entry["branch_id"] == 2


def test_logger_includes_timestamp():
    """Log entries should include timestamp"""
    stream = StringIO()
    handler = logging.StreamHandler(stream)

    logger = get_logger("test_ts")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    logger.info("Test")

    output = stream.getvalue()
    log_entry = json.loads(output.strip())
    assert "timestamp" in log_entry
```

**Step 2: Run test to verify it fails**

```bash
cd backend && pytest tests/test_logging.py -v
```

Expected: FAIL - ModuleNotFoundError

**Step 3: Create logging configuration**

```python
# backend/app/logging_config.py
"""
Structured JSON Logging Configuration

Provides consistent, parseable logs for production monitoring.
"""
import logging
import json
import sys
from datetime import datetime
from typing import Any


class JSONFormatter(logging.Formatter):
    """Format log records as JSON"""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        if hasattr(record, "branch_id"):
            log_entry["branch_id"] = record.branch_id
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        if hasattr(record, "duration_ms"):
            log_entry["duration_ms"] = record.duration_ms
        if hasattr(record, "endpoint"):
            log_entry["endpoint"] = record.endpoint
        if hasattr(record, "method"):
            log_entry["method"] = record.method
        if hasattr(record, "status_code"):
            log_entry["status_code"] = record.status_code

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def setup_logging(level: str = "INFO") -> None:
    """Configure root logger with JSON formatter"""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Add JSON handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with JSON formatting"""
    logger = logging.getLogger(name)

    # Only add handler if none exist
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.propagate = False

    return logger
```

**Step 4: Run test to verify it passes**

```bash
cd backend && pytest tests/test_logging.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/logging_config.py backend/tests/test_logging.py
git commit -m "feat: add structured JSON logging for observability"
```

---

## Task 3: Add Request Logging Middleware

**Files:**
- Create: `backend/app/middleware.py`
- Modify: `backend/app/main.py`

**Step 1: Write failing test**

```python
# backend/tests/test_middleware.py
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.middleware import RequestLoggingMiddleware


def test_middleware_logs_requests(caplog):
    """Middleware should log request/response info"""
    app = FastAPI()
    app.add_middleware(RequestLoggingMiddleware)

    @app.get("/test")
    def test_endpoint():
        return {"status": "ok"}

    client = TestClient(app)

    with caplog.at_level("INFO"):
        response = client.get("/test")

    assert response.status_code == 200
    # Should have logged the request
    assert any("GET /test" in record.message for record in caplog.records)
```

**Step 2: Run test to verify it fails**

```bash
cd backend && pytest tests/test_middleware.py -v
```

Expected: FAIL

**Step 3: Create middleware**

```python
# backend/app/middleware.py
"""
Request/Response Middleware

Adds request ID, logs all requests with timing.
"""
import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.logging_config import get_logger

logger = get_logger("api")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests with timing and context"""

    async def dispatch(self, request: Request, call_next) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        # Start timer
        start_time = time.time()

        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"{request.method} {request.url.path} - ERROR",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "endpoint": request.url.path,
                    "duration_ms": round(duration_ms, 2),
                    "error": str(e)
                }
            )
            raise

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Log request
        logger.info(
            f"{request.method} {request.url.path} - {response.status_code}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "endpoint": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2)
            }
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response
```

**Step 4: Update main.py to use middleware**

```python
# Add to backend/app/main.py after CORS middleware:

from app.middleware import RequestLoggingMiddleware
from app.logging_config import setup_logging

# Setup logging on startup
setup_logging(level="INFO" if not settings.DEBUG else "DEBUG")

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)
```

**Step 5: Run test to verify it passes**

```bash
cd backend && pytest tests/test_middleware.py -v
```

Expected: PASS

**Step 6: Commit**

```bash
git add backend/app/middleware.py backend/tests/test_middleware.py backend/app/main.py
git commit -m "feat: add request logging middleware with timing"
```

---

## Task 4: Create CashDifferenceItem Model (Schema Normalization)

**Files:**
- Modify: `backend/app/models/__init__.py`
- Create: `backend/alembic/versions/xxxx_add_cash_difference_items.py`
- Modify: `backend/app/schemas/__init__.py`

**Step 1: Write failing test**

```python
# backend/tests/test_cash_difference_items.py
import pytest
from decimal import Decimal
from app.models import CashDifference, CashDifferenceItem, OnlinePlatform


def test_cash_difference_item_model(db):
    """CashDifferenceItem should store platform-specific amounts"""
    # Create platform
    platform = OnlinePlatform(name="Visa", channel_type="pos_visa", is_system=True)
    db.add(platform)
    db.commit()

    # Create cash difference
    from datetime import date
    cd = CashDifference(
        branch_id=1,
        difference_date=date.today(),
        created_by=1
    )
    db.add(cd)
    db.commit()

    # Create item
    item = CashDifferenceItem(
        cash_difference_id=cd.id,
        platform_id=platform.id,
        source_type="kasa",
        amount=Decimal("1000.00")
    )
    db.add(item)
    db.commit()

    # Query back
    result = db.query(CashDifferenceItem).filter_by(cash_difference_id=cd.id).first()
    assert result is not None
    assert result.amount == Decimal("1000.00")
    assert result.source_type == "kasa"
    assert result.platform.name == "Visa"


def test_cash_difference_items_relationship(db):
    """CashDifference should have items relationship"""
    from datetime import date

    # Create platforms
    visa = OnlinePlatform(name="Visa", channel_type="pos_visa", is_system=True)
    nakit = OnlinePlatform(name="Nakit", channel_type="pos_nakit", is_system=True)
    db.add_all([visa, nakit])
    db.commit()

    # Create cash difference with items
    cd = CashDifference(
        branch_id=1,
        difference_date=date.today(),
        created_by=1
    )
    db.add(cd)
    db.commit()

    # Add items
    items = [
        CashDifferenceItem(cash_difference_id=cd.id, platform_id=visa.id, source_type="kasa", amount=Decimal("5000")),
        CashDifferenceItem(cash_difference_id=cd.id, platform_id=visa.id, source_type="pos", amount=Decimal("5100")),
        CashDifferenceItem(cash_difference_id=cd.id, platform_id=nakit.id, source_type="kasa", amount=Decimal("3000")),
        CashDifferenceItem(cash_difference_id=cd.id, platform_id=nakit.id, source_type="pos", amount=Decimal("2900")),
    ]
    db.add_all(items)
    db.commit()

    # Query through relationship
    db.refresh(cd)
    assert len(cd.items) == 4

    # Helper to get amount by platform and source
    def get_amount(platform_name: str, source: str) -> Decimal:
        for item in cd.items:
            if item.platform.name == platform_name and item.source_type == source:
                return item.amount
        return Decimal(0)

    assert get_amount("Visa", "kasa") == Decimal("5000")
    assert get_amount("Visa", "pos") == Decimal("5100")
```

**Step 2: Run test to verify it fails**

```bash
cd backend && pytest tests/test_cash_difference_items.py -v
```

Expected: FAIL - CashDifferenceItem not defined

**Step 3: Add CashDifferenceItem model**

Add to `backend/app/models/__init__.py` after CashDifference class:

```python
class CashDifferenceItem(Base):
    """Normalized cash difference amounts per platform"""
    __tablename__ = "cash_difference_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    cash_difference_id: Mapped[int] = mapped_column(ForeignKey("cash_differences.id", ondelete="CASCADE"))
    platform_id: Mapped[int] = mapped_column(ForeignKey("online_platforms.id"))
    source_type: Mapped[str] = mapped_column(String(10))  # 'kasa' or 'pos'
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)

    # Relationships
    cash_difference: Mapped["CashDifference"] = relationship(back_populates="items")
    platform: Mapped["OnlinePlatform"] = relationship()
```

And add to CashDifference class:

```python
# Add this relationship to CashDifference class
items: Mapped[list["CashDifferenceItem"]] = relationship(
    back_populates="cash_difference",
    cascade="all, delete-orphan"
)
```

**Step 4: Run test to verify it passes**

```bash
cd backend && pytest tests/test_cash_difference_items.py -v
```

Expected: PASS (with in-memory SQLite)

**Step 5: Create Alembic migration**

```bash
cd backend && alembic revision -m "add_cash_difference_items_table"
```

Edit the generated migration:

```python
"""add_cash_difference_items_table

Revision ID: [auto-generated]
Revises: [previous]
Create Date: 2025-12-25
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '[auto-generated]'
down_revision: Union[str, None] = 'ccba155171a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'cash_difference_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cash_difference_id', sa.Integer(), nullable=False),
        sa.Column('platform_id', sa.Integer(), nullable=False),
        sa.Column('source_type', sa.String(10), nullable=False),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['cash_difference_id'], ['cash_differences.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['platform_id'], ['online_platforms.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_cdi_cash_difference_id', 'cash_difference_items', ['cash_difference_id'])
    op.create_index('ix_cdi_platform_source', 'cash_difference_items', ['platform_id', 'source_type'])


def downgrade() -> None:
    op.drop_index('ix_cdi_platform_source', 'cash_difference_items')
    op.drop_index('ix_cdi_cash_difference_id', 'cash_difference_items')
    op.drop_table('cash_difference_items')
```

**Step 6: Commit**

```bash
git add backend/app/models/__init__.py backend/tests/test_cash_difference_items.py backend/alembic/versions/
git commit -m "feat: add CashDifferenceItem model for normalized schema"
```

---

## Task 5: Add Idempotency Key Support

**Files:**
- Create: `backend/app/idempotency.py`
- Create: `backend/tests/test_idempotency.py`

**Step 1: Write failing test**

```python
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
```

**Step 2: Run test to verify it fails**

```bash
cd backend && pytest tests/test_idempotency.py -v
```

Expected: FAIL

**Step 3: Create idempotency module**

```python
# backend/app/idempotency.py
"""
Idempotency Key Support

Prevents duplicate submissions by caching responses.
Uses in-memory store for simplicity (can upgrade to Redis later).
"""
from datetime import datetime, timedelta
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
            if datetime.utcnow() > cached.expires_at:
                del self._store[key]
                return None

            return cached.response

    def save(self, key: str, response: Any) -> None:
        """Save response for key"""
        with self._lock:
            now = datetime.utcnow()
            self._store[key] = CachedResponse(
                response=response,
                created_at=now,
                expires_at=now + timedelta(seconds=self._ttl_seconds)
            )

    def cleanup(self) -> int:
        """Remove expired entries, return count removed"""
        with self._lock:
            now = datetime.utcnow()
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
```

**Step 4: Run test to verify it passes**

```bash
cd backend && pytest tests/test_idempotency.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/idempotency.py backend/tests/test_idempotency.py
git commit -m "feat: add idempotency key support for safe retries"
```

---

## Task 6: Add Idempotency Header to Cash Difference Import

**Files:**
- Modify: `backend/app/api/cash_difference.py`
- Create: `backend/tests/test_cash_difference_idempotency.py`

**Step 1: Write failing test**

```python
# backend/tests/test_cash_difference_idempotency.py
import pytest
from fastapi.testclient import TestClient


def test_import_with_idempotency_key_prevents_duplicates(client):
    """Same idempotency key should return cached response"""
    payload = {
        "difference_date": "2025-12-25",
        "kasa_visa": 5000,
        "kasa_nakit": 3000,
        "kasa_total": 8000,
        "pos_visa": 5100,
        "pos_nakit": 2900,
        "pos_total": 8000,
        "expenses": []
    }

    idempotency_key = "test-import-123"

    # First request
    response1 = client.post(
        "/api/cash-difference/import",
        json=payload,
        headers={"X-Idempotency-Key": idempotency_key}
    )
    assert response1.status_code == 200
    record_id_1 = response1.json()["id"]

    # Second request with same key
    response2 = client.post(
        "/api/cash-difference/import",
        json=payload,
        headers={"X-Idempotency-Key": idempotency_key}
    )
    assert response2.status_code == 200
    record_id_2 = response2.json()["id"]

    # Should return same record
    assert record_id_1 == record_id_2


def test_import_without_idempotency_key_works(client):
    """Request without idempotency key should work normally"""
    payload = {
        "difference_date": "2025-12-26",
        "kasa_visa": 1000,
        "kasa_nakit": 500,
        "kasa_total": 1500,
        "pos_visa": 1000,
        "pos_nakit": 500,
        "pos_total": 1500,
        "expenses": []
    }

    response = client.post(
        "/api/cash-difference/import",
        json=payload
    )
    assert response.status_code == 200
```

**Step 2: Run test to verify it fails**

```bash
cd backend && pytest tests/test_cash_difference_idempotency.py -v
```

Expected: FAIL (or different behavior)

**Step 3: Update cash_difference.py import endpoint**

Modify `backend/app/api/cash_difference.py`:

```python
# Add at top:
from fastapi import Header
from app.idempotency import check_idempotency, save_idempotency

# Modify import_cash_difference function signature:
@router.post("/import", response_model=CashDifferenceResponse)
def import_cash_difference(
    request: CashDifferenceImportRequest,
    db: DBSession,
    ctx: CurrentBranchContext,
    import_expenses: bool = Query(default=True),
    sync_to_sales: bool = Query(default=True),
    x_idempotency_key: str | None = Header(default=None, alias="X-Idempotency-Key")
):
    """Import parsed data and create CashDifference record."""

    # Check idempotency cache first
    if x_idempotency_key:
        cached = check_idempotency(x_idempotency_key)
        if cached:
            return cached

    # ... rest of existing code ...

    db.commit()
    db.refresh(record)

    # Convert to response model for caching
    response = CashDifferenceResponse.model_validate(record)

    # Save to idempotency cache
    save_idempotency(x_idempotency_key, response)

    return response
```

**Step 4: Run test to verify it passes**

```bash
cd backend && pytest tests/test_cash_difference_idempotency.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/api/cash_difference.py backend/tests/test_cash_difference_idempotency.py
git commit -m "feat: add idempotency key support to cash difference import"
```

---

## Task 7: Update Test Coverage and Documentation

**Files:**
- Create: `backend/tests/test_foundation.py`
- Modify: `backend/README.md` (if exists)

**Step 1: Create comprehensive test suite**

```python
# backend/tests/test_foundation.py
"""
Milestone 0 Foundation Tests

Verifies all foundation components work together.
"""
import pytest
from app.features import Features, is_feature_enabled, get_enabled_features
from app.logging_config import setup_logging, get_logger
from app.idempotency import IdempotencyStore


class TestFeatureFlags:
    """Feature flags system tests"""

    def test_all_features_defined(self):
        """All expected features should be defined"""
        expected = ["import_hub", "ai_insights", "multi_tenancy", "dynamic_platforms"]
        for feature_name in expected:
            assert hasattr(Features, feature_name.upper())

    def test_get_enabled_features_complete(self):
        """get_enabled_features should return all flags"""
        result = get_enabled_features()
        assert len(result) == len(Features)


class TestStructuredLogging:
    """Structured logging tests"""

    def test_logger_can_be_created(self):
        """Loggers should be creatable with names"""
        logger = get_logger("test.foundation")
        assert logger is not None
        assert logger.name == "test.foundation"


class TestIdempotency:
    """Idempotency system tests"""

    def test_store_isolation(self):
        """Different stores should be isolated"""
        store1 = IdempotencyStore()
        store2 = IdempotencyStore()

        store1.save("key1", {"from": "store1"})

        assert store1.get("key1") is not None
        assert store2.get("key1") is None


class TestModelIntegration:
    """Model integration tests"""

    def test_cash_difference_item_exists(self):
        """CashDifferenceItem model should be importable"""
        from app.models import CashDifferenceItem
        assert CashDifferenceItem is not None
```

**Step 2: Run all foundation tests**

```bash
cd backend && pytest tests/test_foundation.py tests/test_features.py tests/test_logging.py tests/test_idempotency.py -v
```

Expected: ALL PASS

**Step 3: Commit**

```bash
git add backend/tests/test_foundation.py
git commit -m "test: add comprehensive foundation test suite"
```

---

## Task 8: Run Migration and Final Verification

**Step 1: Run Alembic migration**

```bash
cd backend && alembic upgrade head
```

**Step 2: Run all backend tests**

```bash
cd backend && pytest -v
```

Expected: ALL PASS

**Step 3: Start backend and verify**

```bash
cd backend && uvicorn app.main:app --reload
```

Check logs show JSON format:
```json
{"timestamp": "2025-12-25T...", "level": "INFO", "message": "GET /api/health - 200", ...}
```

**Step 4: Final commit and tag**

```bash
git add -A
git commit -m "milestone: complete M0 Foundation

- Feature flags system for controlled rollout
- Structured JSON logging for observability
- Request logging middleware with timing
- CashDifferenceItem model for normalized schema
- Idempotency key support for safe retries
- Comprehensive test suite

Exit criteria met:
✅ Schema normalization started (CashDifferenceItem)
✅ Feature flags implemented
✅ Structured logging in place
✅ Idempotency keys on import endpoint
✅ Test coverage added"

git tag m0-foundation
```

---

## Exit Criteria Checklist

- [ ] Schema normalized (CashDifferenceItem table created)
- [ ] Feature flags implemented and tested
- [ ] Structured logging in place with JSON output
- [ ] Idempotency keys working on cash difference import
- [ ] All tests passing
- [ ] Migration runs successfully

---

## Notes for Implementer

1. **Test Order**: Run tests after each file change, not just at the end
2. **Migrations**: Test migration on local DB before committing
3. **Backward Compatibility**: Old hardcoded columns still exist (will migrate data in future task)
4. **Feature Flags**: All new features should check flags before executing
