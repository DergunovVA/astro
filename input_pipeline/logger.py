"""
Structured logging for input pipeline with PII redaction.

PII Fields Redacted:
  - Birth dates (partial: XXXX-XX-XX pattern)
  - Coordinates (masked: 55.XX, 37.XX)
  - Full place names (masked to country only)
"""

import logging
import json
from datetime import datetime
import sys


class PiiRedactingFormatter(logging.Formatter):
    """Custom formatter that redacts PII from log records."""

    PII_PATTERNS = {
        'date': r'\d{4}-\d{2}-\d{2}',  # Dates
        'time': r'\d{2}:\d{2}:\d{2}',  # Times
        'coordinates': r'-?\d+\.\d+',   # Floats (lat/lon)
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format and redact sensitive data."""
        # Redact message
        msg = record.getMessage()
        msg = self._redact_pii(msg)

        # Create JSON structure for structured logging
        log_dict = {
            'timestamp': datetime.now().isoformat(),
            'level': record.levelname,
            'module': record.module,
            'function': record.funcName,
            'message': msg,
        }

        # Add context if available
        if hasattr(record, 'operation'):
            log_dict['operation'] = record.operation
        if hasattr(record, 'status'):
            log_dict['status'] = record.status
        if hasattr(record, 'source'):
            log_dict['source'] = record.source
        if hasattr(record, 'confidence'):
            log_dict['confidence'] = record.confidence

        # Add exception if present
        if record.exc_info:
            log_dict['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_dict, ensure_ascii=False)

    @staticmethod
    def _redact_pii(text: str) -> str:
        """Redact PII from log text."""
        import re

        # Redact dates (YYYY-MM-DD -> XXXX-XX-XX)
        text = re.sub(r'\d{4}-\d{2}-\d{2}', 'XXXX-XX-XX', text)

        # Redact coordinates (float -> X.XX)
        text = re.sub(r'(\d+\.\d{4,})', 'X.XX', text)

        # Redact full place names (keep first word only if it looks like "City, Country")
        # E.g., "Moscow, RU" -> "[Place: RU]"
        text = re.sub(r'([A-Za-z\s]+),\s*([A-Z]{2})', r'[Place: \2]', text)

        return text


def get_pipeline_logger(name: str = 'astro.input_pipeline') -> logging.Logger:
    """
    Get or create structured logger for input pipeline.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger with PII redaction
    """
    logger = logging.getLogger(name)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Configure stderr handler with custom formatter
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.DEBUG)

    # Use custom formatter with PII redaction
    formatter = PiiRedactingFormatter()
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    # Don't propagate to root logger
    logger.propagate = False

    return logger


# Module-level logger
logger = get_pipeline_logger(__name__)


def log_operation(operation: str, status: str, **kwargs) -> None:
    """
    Log a pipeline operation.

    Args:
        operation: Name of operation (e.g., 'parse_date', 'resolve_city', 'make_aware')
        status: 'success', 'warning', 'error', 'fallback'
        **kwargs: Additional context (source, confidence, etc.)
    """
    record = logging.LogRecord(
        name=logger.name,
        level=logging.INFO if status == 'success' else logging.WARNING,
        pathname='',
        lineno=0,
        msg=f"{operation}: {status}",
        args=(),
        exc_info=None,
    )

    for key, value in kwargs.items():
        setattr(record, key, value)

    logger.handle(record)
