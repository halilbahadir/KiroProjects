"""
Logging utilities for the Shopping Assistant Chatbot Service.

This module provides structured logging with JSON format, configurable log levels,
and utilities for logging requests, responses, tool executions, and errors.

Requirements: 9.1, 9.2, 9.4, 9.5
"""

import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter that adds timestamp and formats log records as JSON.
    
    This formatter ensures all log messages are output in a structured JSON format
    suitable for log aggregation and analysis tools.
    """
    
    def add_fields(
        self, 
        log_record: Dict[str, Any], 
        record: logging.LogRecord, 
        message_dict: Dict[str, Any]
    ) -> None:
        """
        Add custom fields to the log record.
        
        Args:
            log_record: The dictionary that will be serialized to JSON
            record: The original LogRecord object
            message_dict: Additional message fields
        """
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp in ISO format
        log_record['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        
        # Add log level
        log_record['level'] = record.levelname
        
        # Add logger name
        log_record['logger'] = record.name
        
        # Add source location
        log_record['source'] = {
            'file': record.pathname,
            'line': record.lineno,
            'function': record.funcName
        }


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Configure structured logging with JSON format.
    
    Sets up the root logger with a JSON formatter that outputs to stdout.
    This configuration is suitable for containerized deployments where logs
    are captured from stdout.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        logging.Logger: Configured root logger
        
    Example:
        >>> logger = setup_logging("INFO")
        >>> logger.info("Service started", extra={"port": 8000})
    """
    # Get root logger
    root_logger = logging.getLogger()
    
    # Set log level
    level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Create JSON formatter
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(logger)s %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (typically __name__ of the module)
        
    Returns:
        logging.Logger: Logger instance
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing request")
    """
    return logging.getLogger(name)


def log_request(
    logger: logging.Logger,
    message: str,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    **kwargs: Any
) -> None:
    """
    Log an incoming request with structured context.
    
    Args:
        logger: Logger instance
        message: User message content
        session_id: Session identifier
        user_id: User identifier
        **kwargs: Additional context fields
        
    Requirement: 9.1 - Log incoming requests
    """
    logger.info(
        "Incoming request",
        extra={
            "event_type": "request",
            "user_message": message,
            "session_id": session_id,
            "user_id": user_id,
            **kwargs
        }
    )


def log_response(
    logger: logging.Logger,
    response: str,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    **kwargs: Any
) -> None:
    """
    Log an outgoing response with structured context.
    
    Args:
        logger: Logger instance
        response: Agent response content
        session_id: Session identifier
        user_id: User identifier
        **kwargs: Additional context fields
        
    Requirement: 9.1 - Log outgoing responses
    """
    logger.info(
        "Outgoing response",
        extra={
            "event_type": "response",
            "agent_response": response,
            "session_id": session_id,
            "user_id": user_id,
            **kwargs
        }
    )


def log_error(
    logger: logging.Logger,
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None
) -> None:
    """
    Log an error with sufficient context for debugging.
    
    Args:
        logger: Logger instance
        error: Exception that occurred
        context: Additional context about the error
        session_id: Session identifier
        user_id: User identifier
        
    Requirement: 9.2 - Log errors with context
    """
    logger.error(
        f"Error occurred: {str(error)}",
        extra={
            "event_type": "error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {},
            "session_id": session_id,
            "user_id": user_id
        },
        exc_info=True
    )


def log_tool_execution(
    logger: logging.Logger,
    tool_name: str,
    outcome: str,
    duration_ms: Optional[float] = None,
    **kwargs: Any
) -> None:
    """
    Log a custom tool invocation and its outcome.
    
    Args:
        logger: Logger instance
        tool_name: Name of the tool that was invoked
        outcome: Outcome of the tool execution (success, error, etc.)
        duration_ms: Execution duration in milliseconds
        **kwargs: Additional context fields
        
    Requirement: 9.5 - Log tool executions
    """
    logger.info(
        f"Tool execution: {tool_name}",
        extra={
            "event_type": "tool_execution",
            "tool_name": tool_name,
            "outcome": outcome,
            "duration_ms": duration_ms,
            **kwargs
        }
    )


def log_startup(
    logger: logging.Logger,
    service_name: str,
    version: Optional[str] = None,
    **kwargs: Any
) -> None:
    """
    Log service startup event.
    
    Args:
        logger: Logger instance
        service_name: Name of the service
        version: Service version
        **kwargs: Additional context fields
        
    Requirement: 9.4 - Log startup events
    """
    logger.info(
        f"Service starting: {service_name}",
        extra={
            "event_type": "startup",
            "service_name": service_name,
            "version": version,
            **kwargs
        }
    )


def log_shutdown(
    logger: logging.Logger,
    service_name: str,
    reason: Optional[str] = None,
    **kwargs: Any
) -> None:
    """
    Log service shutdown event.
    
    Args:
        logger: Logger instance
        service_name: Name of the service
        reason: Reason for shutdown
        **kwargs: Additional context fields
        
    Requirement: 9.4 - Log shutdown events
    """
    logger.info(
        f"Service shutting down: {service_name}",
        extra={
            "event_type": "shutdown",
            "service_name": service_name,
            "reason": reason,
            **kwargs
        }
    )
