# backend/tests/test_middleware.py
import pytest
import json
import logging
from io import StringIO
from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.middleware import RequestLoggingMiddleware
from app.logging_config import JSONFormatter


def test_middleware_logs_requests():
    """Middleware should log request/response info"""
    # Setup a logger to capture middleware logs
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JSONFormatter())

    # Configure the 'api' logger that middleware uses
    logger = logging.getLogger("api")
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Create app with middleware
    app = FastAPI()
    app.add_middleware(RequestLoggingMiddleware)

    @app.get("/test")
    def test_endpoint():
        return {"status": "ok"}

    client = TestClient(app)
    response = client.get("/test")

    assert response.status_code == 200

    # Parse the logged output
    output = stream.getvalue()
    log_lines = [line for line in output.strip().split('\n') if line]

    # Should have at least one log entry
    assert len(log_lines) > 0, "No logs were captured"

    # Parse and verify the log entry
    log_entry = json.loads(log_lines[0])
    assert log_entry["message"] == "GET /test - 200"
    assert log_entry["method"] == "GET"
    assert log_entry["endpoint"] == "/test"
    assert log_entry["status_code"] == 200
    assert "request_id" in log_entry
    assert "duration_ms" in log_entry
