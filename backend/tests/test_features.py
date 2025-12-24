# backend/tests/test_features.py
"""Tests for feature flags system"""
import pytest
from app.features import Features, is_feature_enabled, get_enabled_features


def test_feature_flags_default_values():
    """Feature flags should have sensible defaults - all disabled"""
    assert not is_feature_enabled(Features.IMPORT_HUB)
    assert not is_feature_enabled(Features.AI_INSIGHTS)
    assert not is_feature_enabled(Features.MULTI_TENANCY)
    assert not is_feature_enabled(Features.DYNAMIC_PLATFORMS)


def test_feature_can_be_enabled_via_env(monkeypatch):
    """Features can be enabled via environment variables"""
    # Set env before calling is_feature_enabled (reads fresh each call)
    monkeypatch.setenv("FEATURE_IMPORT_HUB", "true")

    # is_feature_enabled reads from os.getenv directly, no reload needed
    assert is_feature_enabled(Features.IMPORT_HUB)

    # Other features should still be disabled
    assert not is_feature_enabled(Features.AI_INSIGHTS)


def test_feature_accepts_various_true_values(monkeypatch):
    """Features accept multiple true representations"""
    for true_val in ("true", "1", "yes", "on", "TRUE", "Yes"):
        monkeypatch.setenv("FEATURE_AI_INSIGHTS", true_val)
        assert is_feature_enabled(Features.AI_INSIGHTS)


def test_get_enabled_features_returns_dict():
    """get_enabled_features returns all flags as dict"""
    result = get_enabled_features()
    assert isinstance(result, dict)
    assert "import_hub" in result
    assert "ai_insights" in result
    assert "multi_tenancy" in result
    assert "dynamic_platforms" in result
    assert len(result) == len(Features)
