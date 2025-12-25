# backend/tests/test_logging.py
"""Tests for structured JSON logging"""
import pytest
import json
import logging
from io import StringIO
from app.logging_config import setup_logging, get_logger, JSONFormatter


def test_logger_outputs_json():
    """Logger should output JSON formatted logs"""
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JSONFormatter())

    logger = logging.getLogger("test_json")
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    logger.info("Test message", extra={"user_id": 1, "branch_id": 2})

    output = stream.getvalue()
    log_entry = json.loads(output.strip())
    assert log_entry["message"] == "Test message"
    assert log_entry["user_id"] == 1
    assert log_entry["branch_id"] == 2


def test_logger_includes_timestamp():
    """Log entries should include timestamp"""
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JSONFormatter())

    logger = logging.getLogger("test_ts")
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    logger.info("Test")

    output = stream.getvalue()
    log_entry = json.loads(output.strip())
    assert "timestamp" in log_entry
    assert "level" in log_entry
    assert log_entry["level"] == "INFO"


def test_get_logger_returns_json_logger():
    """get_logger should return a logger with JSON formatting"""
    # Clear any existing handlers first
    logger_name = "test_get_logger"
    base_logger = logging.getLogger(logger_name)
    base_logger.handlers.clear()

    logger = get_logger(logger_name)
    assert logger is not None
    assert len(logger.handlers) > 0
    assert isinstance(logger.handlers[0].formatter, JSONFormatter)


def test_setup_logging_validates_level():
    """setup_logging should reject invalid levels"""
    with pytest.raises(ValueError, match="Invalid logging level"):
        setup_logging("INVALID")


def test_json_formatter_handles_non_serializable():
    """JSONFormatter should handle non-serializable values gracefully"""
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JSONFormatter())

    logger = logging.getLogger("test_serial")
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # This should not raise - fallback to str()
    logger.info("Test", extra={"user_id": lambda x: x})  # lambda is not serializable

    output = stream.getvalue()
    # Should still produce valid JSON
    log_entry = json.loads(output.strip())
    assert "message" in log_entry
