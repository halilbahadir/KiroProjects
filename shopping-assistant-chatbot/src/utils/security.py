"""
Security utilities for the Shopping Assistant Chatbot Service.

This module provides functions to redact sensitive data from log messages,
including credentials, PII (Personally Identifiable Information), and other
sensitive information that should not appear in logs.

Requirements: 9.3
"""

import re
from typing import Any, Dict, Union


# Patterns for sensitive data detection
PATTERNS = {
    # Email addresses
    'email': re.compile(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        re.IGNORECASE
    ),
    
    # Credit card numbers (various formats)
    'credit_card': re.compile(
        r'\b(?:\d{4}[-\s]?){3}\d{4}\b'
    ),
    
    # API keys (common patterns)
    'api_key': re.compile(
        r'\b(?:api[_-]?key|apikey|access[_-]?key|secret[_-]?key)["\']?\s*[:=]\s*["\']?([A-Za-z0-9_\-]{20,})["\']?',
        re.IGNORECASE
    ),
    
    # AWS Access Key ID
    'aws_access_key': re.compile(
        r'\b(AKIA[0-9A-Z]{16})\b'
    ),
    
    # AWS Secret Access Key (base64-like pattern)
    'aws_secret_key': re.compile(
        r'\b([A-Za-z0-9/+=]{40})\b'
    ),
    
    # Bearer tokens
    'bearer_token': re.compile(
        r'\bBearer\s+([A-Za-z0-9_\-\.]+)',
        re.IGNORECASE
    ),
    
    # Authorization headers
    'auth_header': re.compile(
        r'\bAuthorization\s*:\s*([^\s,]+)',
        re.IGNORECASE
    ),
    
    # Password fields
    'password': re.compile(
        r'\b(?:password|passwd|pwd)["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)["\']?',
        re.IGNORECASE
    ),
    
    # Social Security Numbers (US format)
    'ssn': re.compile(
        r'\b\d{3}-\d{2}-\d{4}\b'
    ),
    
    # Phone numbers (various formats)
    'phone': re.compile(
        r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
    ),
    
    # IP addresses (for privacy)
    'ip_address': re.compile(
        r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    ),
}


# Redaction placeholder
REDACTED = '[REDACTED]'


def redact_email(text: str) -> str:
    """
    Redact email addresses from text.
    
    Args:
        text: Input text that may contain email addresses
        
    Returns:
        str: Text with email addresses replaced with [REDACTED]
        
    Example:
        >>> redact_email("Contact user@example.com for help")
        'Contact [REDACTED] for help'
    """
    return PATTERNS['email'].sub(REDACTED, text)


def redact_credit_card(text: str) -> str:
    """
    Redact credit card numbers from text.
    
    Args:
        text: Input text that may contain credit card numbers
        
    Returns:
        str: Text with credit card numbers replaced with [REDACTED]
        
    Example:
        >>> redact_credit_card("Card: 4532-1234-5678-9010")
        'Card: [REDACTED]'
    """
    return PATTERNS['credit_card'].sub(REDACTED, text)


def redact_api_keys(text: str) -> str:
    """
    Redact API keys and access keys from text.
    
    Args:
        text: Input text that may contain API keys
        
    Returns:
        str: Text with API keys replaced with [REDACTED]
        
    Example:
        >>> redact_api_keys("api_key: sk_live_1234567890abcdef")
        'api_key: [REDACTED]'
    """
    # Redact the captured group (the actual key value)
    text = PATTERNS['api_key'].sub(lambda m: m.group(0).replace(m.group(1), REDACTED), text)
    return text


def redact_aws_credentials(text: str) -> str:
    """
    Redact AWS credentials (access keys and secret keys) from text.
    
    Args:
        text: Input text that may contain AWS credentials
        
    Returns:
        str: Text with AWS credentials replaced with [REDACTED]
        
    Example:
        >>> redact_aws_credentials("AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE")
        'AWS_ACCESS_KEY_ID=[REDACTED]'
    """
    text = PATTERNS['aws_access_key'].sub(REDACTED, text)
    text = PATTERNS['aws_secret_key'].sub(REDACTED, text)
    return text


def redact_bearer_tokens(text: str) -> str:
    """
    Redact bearer tokens from text.
    
    Args:
        text: Input text that may contain bearer tokens
        
    Returns:
        str: Text with bearer tokens replaced with [REDACTED]
        
    Example:
        >>> redact_bearer_tokens("Authorization: Bearer eyJhbGc...")
        'Authorization: Bearer [REDACTED]'
    """
    return PATTERNS['bearer_token'].sub(lambda m: f"Bearer {REDACTED}", text)


def redact_auth_headers(text: str) -> str:
    """
    Redact authorization headers from text.
    
    Args:
        text: Input text that may contain authorization headers
        
    Returns:
        str: Text with authorization values replaced with [REDACTED]
        
    Example:
        >>> redact_auth_headers("Authorization: Basic dXNlcjpwYXNz")
        'Authorization: [REDACTED]'
    """
    return PATTERNS['auth_header'].sub(lambda m: f"Authorization: {REDACTED}", text)


def redact_passwords(text: str) -> str:
    """
    Redact password values from text.
    
    Args:
        text: Input text that may contain passwords
        
    Returns:
        str: Text with passwords replaced with [REDACTED]
        
    Example:
        >>> redact_passwords('{"password": "secret123"}')
        '{"password": "[REDACTED]"}'
    """
    return PATTERNS['password'].sub(lambda m: m.group(0).replace(m.group(1), REDACTED), text)


def redact_ssn(text: str) -> str:
    """
    Redact Social Security Numbers from text.
    
    Args:
        text: Input text that may contain SSNs
        
    Returns:
        str: Text with SSNs replaced with [REDACTED]
        
    Example:
        >>> redact_ssn("SSN: 123-45-6789")
        'SSN: [REDACTED]'
    """
    return PATTERNS['ssn'].sub(REDACTED, text)


def redact_phone_numbers(text: str) -> str:
    """
    Redact phone numbers from text.
    
    Args:
        text: Input text that may contain phone numbers
        
    Returns:
        str: Text with phone numbers replaced with [REDACTED]
        
    Example:
        >>> redact_phone_numbers("Call (555) 123-4567")
        'Call [REDACTED]'
    """
    return PATTERNS['phone'].sub(REDACTED, text)


def redact_ip_addresses(text: str) -> str:
    """
    Redact IP addresses from text for privacy.
    
    Args:
        text: Input text that may contain IP addresses
        
    Returns:
        str: Text with IP addresses replaced with [REDACTED]
        
    Example:
        >>> redact_ip_addresses("Request from 192.168.1.1")
        'Request from [REDACTED]'
    """
    return PATTERNS['ip_address'].sub(REDACTED, text)


def sanitize_log_message(message: Union[str, Dict[str, Any]]) -> Union[str, Dict[str, Any]]:
    """
    Sanitize a log message by redacting all sensitive data.
    
    This function applies all redaction patterns to ensure no sensitive
    information appears in logs. It handles both string messages and
    dictionary structures (for structured logging).
    
    Args:
        message: Log message as string or dictionary
        
    Returns:
        Union[str, Dict[str, Any]]: Sanitized message with sensitive data redacted
        
    Example:
        >>> sanitize_log_message("User user@example.com logged in with key: AKIAIOSFODNN7EXAMPLE")
        'User [REDACTED] logged in with key: [REDACTED]'
        
        >>> sanitize_log_message({"email": "user@example.com", "status": "active"})
        {'email': '[REDACTED]', 'status': 'active'}
        
    Requirement: 9.3 - Redact customer data and credentials from logs
    """
    if isinstance(message, dict):
        # Recursively sanitize dictionary values
        return {
            key: sanitize_log_message(value) if isinstance(value, (str, dict)) else value
            for key, value in message.items()
        }
    
    if not isinstance(message, str):
        # Convert to string if not already
        message = str(message)
    
    # Apply all redaction patterns
    message = redact_email(message)
    message = redact_credit_card(message)
    message = redact_api_keys(message)
    message = redact_aws_credentials(message)
    message = redact_bearer_tokens(message)
    message = redact_auth_headers(message)
    message = redact_passwords(message)
    message = redact_ssn(message)
    message = redact_phone_numbers(message)
    message = redact_ip_addresses(message)
    
    return message


def sanitize_dict(data: Dict[str, Any], sensitive_keys: list = None) -> Dict[str, Any]:
    """
    Sanitize a dictionary by redacting values for sensitive keys.
    
    This function is useful for sanitizing structured data like request/response
    objects before logging. It redacts both by pattern matching and by key name.
    
    Args:
        data: Dictionary to sanitize
        sensitive_keys: List of key names whose values should be redacted
                       (default: common sensitive key names)
        
    Returns:
        Dict[str, Any]: Sanitized dictionary
        
    Example:
        >>> sanitize_dict({"username": "john", "password": "secret", "email": "john@example.com"})
        {'username': 'john', 'password': '[REDACTED]', 'email': '[REDACTED]'}
    """
    if sensitive_keys is None:
        sensitive_keys = [
            'password', 'passwd', 'pwd', 'secret', 'token', 'api_key', 'apikey',
            'access_key', 'secret_key', 'aws_access_key_id', 'aws_secret_access_key',
            'aws_session_token', 'authorization', 'auth', 'bearer', 'credit_card',
            'card_number', 'cvv', 'ssn', 'social_security'
        ]
    
    sanitized = {}
    
    for key, value in data.items():
        # Check if key name indicates sensitive data
        if any(sensitive_key in key.lower() for sensitive_key in sensitive_keys):
            sanitized[key] = REDACTED
        elif isinstance(value, dict):
            # Recursively sanitize nested dictionaries
            sanitized[key] = sanitize_dict(value, sensitive_keys)
        elif isinstance(value, str):
            # Apply pattern-based redaction to string values
            sanitized[key] = sanitize_log_message(value)
        else:
            sanitized[key] = value
    
    return sanitized


def create_safe_log_context(**kwargs: Any) -> Dict[str, Any]:
    """
    Create a safe logging context by sanitizing all provided keyword arguments.
    
    This is a convenience function for creating structured log contexts that
    are guaranteed to be free of sensitive data.
    
    Args:
        **kwargs: Arbitrary keyword arguments to include in log context
        
    Returns:
        Dict[str, Any]: Sanitized context dictionary safe for logging
        
    Example:
        >>> context = create_safe_log_context(
        ...     user_id="12345",
        ...     email="user@example.com",
        ...     api_key="secret_key_123"
        ... )
        >>> context
        {'user_id': '12345', 'email': '[REDACTED]', 'api_key': '[REDACTED]'}
    """
    return sanitize_dict(kwargs)

