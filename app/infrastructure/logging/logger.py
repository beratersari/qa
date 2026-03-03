"""
Custom logging module for Language Learning App.

Provides structured JSON logging for file output (Elasticsearch-compatible)
and human-readable format for console output.

Log levels: TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL
"""

import logging
import json
import sys
import os
from datetime import datetime, timezone
from typing import Optional, Any
from pathlib import Path
from functools import lru_cache
import traceback


# Custom TRACE level (lower than DEBUG)
TRACE = 5
logging.addLevelName(TRACE, "TRACE")


class TraceLogger(logging.Logger):
    """Custom Logger class with trace level support."""
    
    def trace(self, msg: str, *args, **kwargs) -> None:
        """Log a message with TRACE level."""
        if self.isEnabledFor(TRACE):
            self._log(TRACE, msg, args, **kwargs)


# Set custom logger class
logging.setLoggerClass(TraceLogger)


class JsonFormatter(logging.Formatter):
    """
    JSON formatter for structured logging compatible with Elasticsearch.
    
    Output format:
    {
        "level": "ERROR",
        "message": "Payment failed",
        "user_id": 123,
        "request_id": "abc-456",
        "timestamp": "2026-03-03T12:00:00Z",
        "logger": "app.services.auth",
        "module": "auth_service",
        "function": "authenticate_user",
        "line": 42,
        "exception": "Traceback..."
    }
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as JSON."""
        log_data: dict[str, Any] = {
            "level": record.levelname,
            "message": record.getMessage(),
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat().replace("+00:00", "Z"),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "extra_data"):
            log_data["extra_data"] = record.extra_data
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, default=str)


class ConsoleFormatter(logging.Formatter):
    """
    Human-readable formatter for console output.
    
    Format: LEVEL | filename:line | message
    Example: ERROR | auth_service.py:42 | Authentication failed for user john
    """
    
    # Color codes for different log levels
    COLORS = {
        "TRACE": "\033[37m",      # White
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[35m",   # Magenta
    }
    RESET = "\033[0m"
    BOLD = "\033[1m"
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record for console output."""
        # Get color for level
        color = self.COLORS.get(record.levelname, "")
        
        # Build the formatted message
        level_str = f"{color}{self.BOLD}{record.levelname:8}{self.RESET}"
        location_str = f"{record.filename}:{record.lineno}"
        message = record.getMessage()
        
        # Base format
        formatted = f"{level_str} | {location_str:30} | {message}"
        
        # Add extra context if present
        extra_parts = []
        if hasattr(record, "user_id"):
            extra_parts.append(f"user_id={record.user_id}")
        if hasattr(record, "request_id"):
            extra_parts.append(f"request_id={record.request_id}")
        
        if extra_parts:
            formatted += f" | {', '.join(extra_parts)}"
        
        # Add exception info if present
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return formatted


class LoggerAdapter(logging.LoggerAdapter):
    """
    Custom logger adapter that allows adding context to log messages.
    
    Usage:
        logger = get_logger(__name__)
        logger.info("User logged in", extra={"user_id": 123, "request_id": "abc"})
    """
    
    def process(self, msg: str, kwargs: dict) -> tuple[str, dict]:
        """Process the logging call to add extra context."""
        extra = kwargs.get("extra", {})
        
        # Add any context from the adapter
        if self.extra:
            extra.update(self.extra)
        
        kwargs["extra"] = extra
        return msg, kwargs


@lru_cache()
def get_logger(name: str) -> TraceLogger:
    """
    Get a logger instance by name.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Logger instance with trace level support
    """
    return logging.getLogger(name)


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    console_output: bool = True,
    json_format: bool = True
) -> None:
    """
    Configure application-wide logging.
    
    Args:
        log_level: Minimum log level to capture (TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file for JSON structured logs (Elasticsearch-compatible)
        console_output: Whether to output logs to console
        json_format: Whether to use JSON format for file output
    """
    # Get numeric level
    level = _get_log_level(log_level)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers
    root_logger.handlers = []
    
    # Console handler with human-readable format
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(ConsoleFormatter())
        root_logger.addHandler(console_handler)
    
    # File handler with JSON format for Elasticsearch
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        
        if json_format:
            file_handler.setFormatter(JsonFormatter())
        else:
            file_handler.setFormatter(ConsoleFormatter())
        
        root_logger.addHandler(file_handler)


def _get_log_level(level_name: str) -> int:
    """Convert log level name to numeric value."""
    levels = {
        "TRACE": TRACE,
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    return levels.get(level_name.upper(), logging.INFO)


class LogContext:
    """
    Context manager for adding context to log messages.
    
    Usage:
        with LogContext(user_id=123, request_id="abc"):
            logger.info("Processing request")
    """
    
    _context: dict[str, Any] = {}
    
    def __init__(self, **kwargs: Any):
        self._new_context = kwargs
        self._old_context: dict[str, Any] = {}
    
    def __enter__(self) -> "LogContext":
        self._old_context = LogContext._context.copy()
        LogContext._context.update(self._new_context)
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        LogContext._context = self._old_context
    
    @classmethod
    def get_context(cls) -> dict[str, Any]:
        """Get current logging context."""
        return cls._context.copy()
    
    @classmethod
    def clear_context(cls) -> None:
        """Clear the logging context."""
        cls._context = {}


def log_with_context(logger: TraceLogger, level: int, message: str, **kwargs: Any) -> None:
    """
    Log a message with the current context.
    
    Args:
        logger: Logger instance
        level: Log level
        message: Log message
        **kwargs: Additional context to include
    """
    context = LogContext.get_context()
    context.update(kwargs)
    logger.log(level, message, extra=context)
