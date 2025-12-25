# backend/app/logging_config.py
"""
Structured JSON Logging Configuration

Provides consistent, parseable logs for production monitoring.
"""
import logging
import json
import sys
from datetime import datetime, UTC


class JSONFormatter(logging.Formatter):
    """
    Format log records as JSON for structured logging.

    Handles extra fields and ensures safe serialization of all values.
    """

    # Extra fields we support
    EXTRA_FIELDS = (
        "user_id", "branch_id", "request_id",
        "duration_ms", "endpoint", "method", "status_code"
    )

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as a JSON string."""
        # Use record.created for accurate timestamp
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields if present
        for field in self.EXTRA_FIELDS:
            if hasattr(record, field):
                log_entry[field] = getattr(record, field)

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Safe JSON serialization with fallback
        try:
            return json.dumps(log_entry)
        except TypeError:
            # Fallback for non-serializable values
            log_entry = {k: str(v) for k, v in log_entry.items()}
            return json.dumps(log_entry)


def setup_logging(level: str = "INFO") -> None:
    """
    Configure root logger with JSON formatter.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Raises:
        ValueError: If level is not a valid logging level
    """
    level_upper = level.upper()
    if not hasattr(logging, level_upper):
        raise ValueError(f"Invalid logging level: {level}")

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level_upper))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Add JSON handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with JSON formatting.

    Prevents handler duplication by checking for existing JSON handlers.
    """
    logger = logging.getLogger(name)
    logger.propagate = False  # Always disable propagation

    # Check if we already have a JSON formatter handler
    has_json_handler = any(
        isinstance(h.formatter, JSONFormatter)
        for h in logger.handlers
    )

    if not has_json_handler:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)

    return logger
