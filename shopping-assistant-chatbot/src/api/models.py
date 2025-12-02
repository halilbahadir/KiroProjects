"""
Data models for the Shopping Assistant Chatbot Service.

This module defines Pydantic models for API requests/responses,
product data, shopping cart data, and AWS credentials.
"""

from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    """
    Incoming chat request from frontend.
    
    Represents a user message sent to the chatbot service.
    """
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's message to the chatbot"
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Optional session identifier for conversation continuity"
    )
    user_id: Optional[str] = Field(
        default=None,
        description="Optional user identifier for personalized responses"
    )
    
    @field_validator("message")
    @classmethod
    def validate_message_not_empty(cls, v: str) -> str:
        """Ensure message is not just whitespace."""
        if not v.strip():
            raise ValueError("Message cannot be empty or only whitespace")
        return v.strip()


class ChatResponse(BaseModel):
    """
    Outgoing chat response to frontend.
    
    Represents the chatbot's response to a user message.
    """
    response: str = Field(
        ...,
        description="Chatbot's response message"
    )
    session_id: str = Field(
        ...,
        description="Session identifier for conversation tracking"
    )
    status: str = Field(
        default="success",
        description="Response status (success or error)"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if status is error"
    )
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Ensure status is either success or error."""
        if v not in ["success", "error"]:
            raise ValueError("Status must be 'success' or 'error'")
        return v


class Product(BaseModel):
    """
    Product information from backend.
    
    Represents a product in the e-commerce catalog.
    """
    id: str = Field(
        ...,
        description="Unique product identifier"
    )
    name: str = Field(
        ...,
        min_length=1,
        description="Product name"
    )
    description: str = Field(
        ...,
        description="Product description"
    )
    price: float = Field(
        ...,
        gt=0,
        description="Product price (must be positive)"
    )
    category: str = Field(
        ...,
        description="Product category"
    )
    in_stock: bool = Field(
        ...,
        description="Whether product is currently in stock"
    )
    image_url: Optional[str] = Field(
        default=None,
        description="URL to product image"
    )
    
    @field_validator("price")
    @classmethod
    def validate_price(cls, v: float) -> float:
        """Ensure price is positive and has reasonable precision."""
        if v <= 0:
            raise ValueError("Price must be positive")
        # Round to 2 decimal places for currency
        return round(v, 2)


class CartItem(BaseModel):
    """
    Item in shopping cart.
    
    Represents a single product in a user's shopping cart.
    """
    product_id: str = Field(
        ...,
        description="Unique product identifier"
    )
    product_name: str = Field(
        ...,
        min_length=1,
        description="Product name for display"
    )
    quantity: int = Field(
        ...,
        gt=0,
        description="Quantity of product in cart (must be positive)"
    )
    price: float = Field(
        ...,
        gt=0,
        description="Unit price of product"
    )
    subtotal: float = Field(
        ...,
        ge=0,
        description="Total price for this cart item (price * quantity)"
    )
    
    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        """Ensure quantity is positive."""
        if v <= 0:
            raise ValueError("Quantity must be positive")
        return v
    
    @field_validator("subtotal")
    @classmethod
    def validate_subtotal(cls, v: float) -> float:
        """Ensure subtotal is non-negative and properly formatted."""
        if v < 0:
            raise ValueError("Subtotal cannot be negative")
        return round(v, 2)


class Cart(BaseModel):
    """
    Shopping cart contents.
    
    Represents a user's complete shopping cart with all items.
    """
    user_id: str = Field(
        ...,
        description="User identifier who owns this cart"
    )
    items: List[CartItem] = Field(
        default_factory=list,
        description="List of items in the cart"
    )
    total: float = Field(
        ...,
        ge=0,
        description="Total cost of all items in cart"
    )
    item_count: int = Field(
        ...,
        ge=0,
        description="Total number of items in cart"
    )
    
    @field_validator("total")
    @classmethod
    def validate_total(cls, v: float) -> float:
        """Ensure total is non-negative and properly formatted."""
        if v < 0:
            raise ValueError("Total cannot be negative")
        return round(v, 2)
    
    @field_validator("item_count")
    @classmethod
    def validate_item_count(cls, v: int) -> int:
        """Ensure item count is non-negative."""
        if v < 0:
            raise ValueError("Item count cannot be negative")
        return v


class AWSCredentials(BaseModel):
    """
    AWS authentication credentials.
    
    Contains credentials needed to authenticate with AWS Bedrock.
    """
    access_key_id: str = Field(
        ...,
        min_length=1,
        description="AWS Access Key ID"
    )
    secret_access_key: str = Field(
        ...,
        min_length=1,
        description="AWS Secret Access Key"
    )
    session_token: Optional[str] = Field(
        default=None,
        description="AWS Session Token (for temporary credentials)"
    )
    region: str = Field(
        default="us-west-2",
        description="AWS Region"
    )
    
    @field_validator("access_key_id", "secret_access_key")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Ensure credentials are not empty or whitespace."""
        if not v.strip():
            raise ValueError("Credential cannot be empty or only whitespace")
        return v.strip()
    
    class Config:
        """Pydantic configuration for sensitive data."""
        # Hide sensitive fields in string representation
        json_schema_extra = {
            "example": {
                "access_key_id": "AKIAIOSFODNN7EXAMPLE",
                "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
                "session_token": None,
                "region": "us-west-2"
            }
        }
