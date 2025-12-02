"""
Configuration management for the Shopping Assistant Chatbot Service.

This module loads and validates environment variables for AWS credentials,
Bedrock settings, server configuration, and backend API settings.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config(BaseModel):
    """Application configuration loaded from environment variables."""
    
    # AWS Credentials (Optional - will use AWS CLI default credentials if not provided)
    AWS_ACCESS_KEY_ID: Optional[str] = Field(
        default=None,
        description="AWS Access Key ID for Bedrock authentication (optional, uses AWS CLI default if not set)"
    )
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(
        default=None,
        description="AWS Secret Access Key for Bedrock authentication (optional, uses AWS CLI default if not set)"
    )
    AWS_SESSION_TOKEN: Optional[str] = Field(
        default=None,
        description="AWS Session Token (optional, for temporary credentials)"
    )
    AWS_REGION: str = Field(
        default="us-west-2",
        description="AWS Region for Bedrock service"
    )
    
    # Bedrock Configuration
    BEDROCK_MODEL_ID: str = Field(
        default="us.amazon.nova-pro-v1:0",
        description="Bedrock model identifier"
    )
    BEDROCK_TEMPERATURE: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Model temperature for response generation"
    )
    BEDROCK_MAX_TOKENS: int = Field(
        default=2048,
        gt=0,
        description="Maximum tokens for model responses"
    )
    
    # Server Configuration
    SERVER_HOST: str = Field(
        default="0.0.0.0",
        description="Host address for HTTP server"
    )
    SERVER_PORT: int = Field(
        default=8000,
        gt=0,
        lt=65536,
        description="Port number for HTTP server"
    )
    
    # Backend API Configuration (Required)
    BACKEND_API_URL: str = Field(
        ...,
        description="Base URL for backend e-commerce API"
    )
    BACKEND_API_KEY: Optional[str] = Field(
        default=None,
        description="API key for backend authentication (optional)"
    )
    
    # Logging Configuration
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate that log level is one of the standard Python logging levels."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(
                f"LOG_LEVEL must be one of {valid_levels}, got '{v}'"
            )
        return v_upper
    
    @field_validator("BACKEND_API_URL")
    @classmethod
    def validate_backend_url(cls, v: str) -> str:
        """Validate that backend URL is properly formatted."""
        if not v.startswith(("http://", "https://")):
            raise ValueError(
                "BACKEND_API_URL must start with http:// or https://"
            )
        return v.rstrip("/")  # Remove trailing slash for consistency
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


def load_config() -> Config:
    """
    Load and validate configuration from environment variables.
    
    Returns:
        Config: Validated configuration object
        
    Raises:
        ValueError: If required environment variables are missing or invalid
        
    Example:
        >>> config = load_config()
        >>> print(config.AWS_REGION)
        'us-west-2'
    """
    try:
        config = Config(
            AWS_ACCESS_KEY_ID=os.getenv("AWS_ACCESS_KEY_ID", ""),
            AWS_SECRET_ACCESS_KEY=os.getenv("AWS_SECRET_ACCESS_KEY", ""),
            AWS_SESSION_TOKEN=os.getenv("AWS_SESSION_TOKEN"),
            AWS_REGION=os.getenv("AWS_REGION", "us-west-2"),
            BEDROCK_MODEL_ID=os.getenv(
                "BEDROCK_MODEL_ID", 
                "us.amazon.nova-pro-v1:0"
            ),
            BEDROCK_TEMPERATURE=float(
                os.getenv("BEDROCK_TEMPERATURE", "0.7")
            ),
            BEDROCK_MAX_TOKENS=int(
                os.getenv("BEDROCK_MAX_TOKENS", "2048")
            ),
            SERVER_HOST=os.getenv("SERVER_HOST", "0.0.0.0"),
            SERVER_PORT=int(os.getenv("SERVER_PORT", "8000")),
            BACKEND_API_URL=os.getenv("BACKEND_API_URL", ""),
            BACKEND_API_KEY=os.getenv("BACKEND_API_KEY"),
            LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),
        )
        return config
    except Exception as e:
        raise ValueError(
            f"Configuration validation failed: {str(e)}. "
            "Please check your environment variables."
        ) from e


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get the global configuration instance.
    
    Loads configuration on first call and caches it for subsequent calls.
    
    Returns:
        Config: The global configuration object
    """
    global _config
    if _config is None:
        _config = load_config()
    return _config
