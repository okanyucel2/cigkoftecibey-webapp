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
