# backend/app/features.py
"""
Feature Flags System

Enable/disable features via environment variables:
- FEATURE_IMPORT_HUB=true
- FEATURE_AI_INSIGHTS=true
- FEATURE_MULTI_TENANCY=true
- FEATURE_DYNAMIC_PLATFORMS=true
"""
import asyncio
import os
from enum import Enum
from functools import wraps

from fastapi import HTTPException


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
    """
    Decorator to require a feature flag for an endpoint.

    Works with both sync and async functions.
    Returns 404 if feature is not enabled.

    Usage:
        @router.get("/new-feature")
        @require_feature(Features.IMPORT_HUB)
        async def new_feature_endpoint():
            return {"status": "ok"}
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not is_feature_enabled(feature):
                raise HTTPException(
                    status_code=404,
                    detail=f"Feature '{feature.value}' is not enabled"
                )
            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not is_feature_enabled(feature):
                raise HTTPException(
                    status_code=404,
                    detail=f"Feature '{feature.value}' is not enabled"
                )
            return func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator
