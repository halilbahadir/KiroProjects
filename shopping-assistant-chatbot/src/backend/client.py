"""
Backend API client for e-commerce operations.

This module provides an async HTTP client for interacting with the backend
e-commerce API, including product listings, cart management, and recommendations.
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

import httpx
from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


class Product(BaseModel):
    """Product information from backend."""
    id: str
    name: str
    description: str
    price: float
    category: str
    in_stock: bool
    image_url: Optional[str] = None


class CartItem(BaseModel):
    """Item in shopping cart."""
    product_id: str
    product_name: str
    quantity: int
    price: float
    subtotal: float


class Cart(BaseModel):
    """Shopping cart contents."""
    user_id: str
    items: List[CartItem]
    total: float
    item_count: int


class BackendAPIError(Exception):
    """Base exception for backend API errors."""
    pass


class BackendAPIClient:
    """
    Async HTTP client for backend e-commerce API.
    
    Handles authentication, retries with exponential backoff, and error handling
    for all backend API operations.
    """
    
    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        initial_retry_delay: float = 1.0,
    ):
        """
        Initialize the backend API client.
        
        Args:
            base_url: Base URL for the backend API
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            initial_retry_delay: Initial delay for exponential backoff (seconds)
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.initial_retry_delay = initial_retry_delay
        
        # Create async HTTP client
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            follow_redirects=True,
        )
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers including authentication.
        
        Returns:
            Dictionary of HTTP headers
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        return headers
    
    async def _request_with_retry(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> httpx.Response:
        """
        Make HTTP request with exponential backoff retry logic.
        
        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for httpx request
            
        Returns:
            HTTP response object
            
        Raises:
            BackendAPIError: If all retry attempts fail
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        # Merge provided headers with authentication headers
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))
        
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(
                    f"API request attempt {attempt + 1}/{self.max_retries}: "
                    f"{method} {url}"
                )
                
                response = await self.client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    **kwargs
                )
                
                # Raise for 4xx and 5xx status codes
                response.raise_for_status()
                
                logger.debug(
                    f"API request successful: {method} {url} "
                    f"(status: {response.status_code})"
                )
                
                return response
                
            except httpx.HTTPStatusError as e:
                # Don't retry client errors (4xx), only server errors (5xx)
                if 400 <= e.response.status_code < 500:
                    logger.error(
                        f"Client error from backend API: {e.response.status_code} "
                        f"- {e.response.text}"
                    )
                    raise BackendAPIError(
                        f"Backend API client error: {e.response.status_code}"
                    ) from e
                
                last_exception = e
                logger.warning(
                    f"Server error on attempt {attempt + 1}: "
                    f"{e.response.status_code}"
                )
                
            except (httpx.RequestError, httpx.TimeoutException) as e:
                last_exception = e
                logger.warning(
                    f"Network error on attempt {attempt + 1}: {str(e)}"
                )
            
            # Calculate exponential backoff delay
            if attempt < self.max_retries - 1:
                delay = self.initial_retry_delay * (2 ** attempt)
                logger.info(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
        
        # All retries exhausted
        error_msg = (
            f"Backend API request failed after {self.max_retries} attempts: "
            f"{method} {url}"
        )
        logger.error(error_msg)
        raise BackendAPIError(error_msg) from last_exception
    
    async def get_products(
        self,
        category: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 10
    ) -> List[Product]:
        """
        Fetch products from backend API.
        
        Args:
            category: Optional product category filter
            search: Optional search query
            limit: Maximum number of products to return
            
        Returns:
            List of Product objects
            
        Raises:
            BackendAPIError: If the API request fails
        """
        params = {"limit": limit}
        if category:
            params["category"] = category
        if search:
            params["search"] = search
        
        try:
            response = await self._request_with_retry(
                "GET",
                "/api/products",
                params=params
            )
            
            data = response.json()
            products = [Product(**item) for item in data.get("products", [])]
            
            logger.info(f"Retrieved {len(products)} products from backend")
            return products
            
        except Exception as e:
            logger.error(f"Failed to get products: {str(e)}")
            raise BackendAPIError(f"Failed to get products: {str(e)}") from e
    
    async def get_cart(self, user_id: str) -> Cart:
        """
        Fetch user's shopping cart from backend API.
        
        Args:
            user_id: User identifier
            
        Returns:
            Cart object with items and totals
            
        Raises:
            BackendAPIError: If the API request fails
        """
        try:
            response = await self._request_with_retry(
                "GET",
                f"/api/cart/{user_id}"
            )
            
            data = response.json()
            cart = Cart(**data)
            
            logger.info(
                f"Retrieved cart for user {user_id}: "
                f"{cart.item_count} items, total ${cart.total:.2f}"
            )
            return cart
            
        except Exception as e:
            logger.error(f"Failed to get cart for user {user_id}: {str(e)}")
            raise BackendAPIError(
                f"Failed to get cart for user {user_id}: {str(e)}"
            ) from e
    
    async def add_cart_item(
        self,
        user_id: str,
        product_id: str,
        quantity: int = 1
    ) -> Cart:
        """
        Add item to user's shopping cart.
        
        Args:
            user_id: User identifier
            product_id: Product identifier to add
            quantity: Number of items to add
            
        Returns:
            Updated Cart object
            
        Raises:
            BackendAPIError: If the API request fails
        """
        payload = {
            "product_id": product_id,
            "quantity": quantity
        }
        
        try:
            response = await self._request_with_retry(
                "POST",
                f"/api/cart/{user_id}/items",
                json=payload
            )
            
            data = response.json()
            cart = Cart(**data)
            
            logger.info(
                f"Added {quantity}x product {product_id} to cart for user {user_id}"
            )
            return cart
            
        except Exception as e:
            logger.error(
                f"Failed to add item to cart for user {user_id}: {str(e)}"
            )
            raise BackendAPIError(
                f"Failed to add item to cart: {str(e)}"
            ) from e
    
    async def remove_cart_item(
        self,
        user_id: str,
        product_id: str
    ) -> Cart:
        """
        Remove item from user's shopping cart.
        
        Args:
            user_id: User identifier
            product_id: Product identifier to remove
            
        Returns:
            Updated Cart object
            
        Raises:
            BackendAPIError: If the API request fails
        """
        try:
            response = await self._request_with_retry(
                "DELETE",
                f"/api/cart/{user_id}/items/{product_id}"
            )
            
            data = response.json()
            cart = Cart(**data)
            
            logger.info(
                f"Removed product {product_id} from cart for user {user_id}"
            )
            return cart
            
        except Exception as e:
            logger.error(
                f"Failed to remove item from cart for user {user_id}: {str(e)}"
            )
            raise BackendAPIError(
                f"Failed to remove item from cart: {str(e)}"
            ) from e
    
    async def get_recommendations(
        self,
        preferences: Optional[str] = None,
        limit: int = 5
    ) -> List[Product]:
        """
        Get product recommendations from backend API.
        
        Args:
            preferences: Optional user preferences description
            limit: Maximum number of recommendations
            
        Returns:
            List of recommended Product objects
            
        Raises:
            BackendAPIError: If the API request fails
        """
        params = {"limit": limit}
        if preferences:
            params["preferences"] = preferences
        
        try:
            response = await self._request_with_retry(
                "GET",
                "/api/recommendations",
                params=params
            )
            
            data = response.json()
            recommendations = [
                Product(**item) for item in data.get("recommendations", [])
            ]
            
            logger.info(
                f"Retrieved {len(recommendations)} product recommendations"
            )
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to get recommendations: {str(e)}")
            raise BackendAPIError(
                f"Failed to get recommendations: {str(e)}"
            ) from e
    
    async def close(self):
        """Close the HTTP client and cleanup resources."""
        await self.client.aclose()
        logger.debug("Backend API client closed")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
