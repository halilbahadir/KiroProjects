"""
Product operation tools for the Shopping Assistant Chatbot.

This module provides custom tools for product-related operations including
listing products and searching the e-commerce catalog. Tools are decorated
with the Strands Agents SDK @tool decorator to enable agent invocation.
"""

import logging
from typing import Optional, List, Dict, Any

from strands import tool
import time

from ..backend.client import BackendAPIClient, BackendAPIError, Product
from ..config import get_config
from ..utils.logging import log_tool_execution


logger = logging.getLogger(__name__)


# Global backend client instance
_backend_client: Optional[BackendAPIClient] = None


def get_backend_client() -> BackendAPIClient:
    """
    Get or create the global backend API client instance.
    
    Returns:
        BackendAPIClient: Configured backend API client
    """
    global _backend_client
    if _backend_client is None:
        config = get_config()
        _backend_client = BackendAPIClient(
            base_url=config.BACKEND_API_URL,
            api_key=config.BACKEND_API_KEY
        )
        logger.info("Initialized backend API client")
    return _backend_client


@tool
async def list_products(
    category: Optional[str] = None,
    search_query: Optional[str] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    List available products from the e-shop catalog.
    
    This tool retrieves products from the backend e-commerce API, allowing
    filtering by category and search terms. Use this when customers ask to
    browse products, search for specific items, or explore the catalog.
    
    Args:
        category: Optional product category filter (e.g., "electronics", "clothing")
        search_query: Optional search term to find specific products
        limit: Maximum number of products to return (default: 10, max: 50)
    
    Returns:
        Dictionary containing:
            - success: Boolean indicating if the operation succeeded
            - products: List of product dictionaries with id, name, description, 
                       price, category, in_stock, and image_url
            - count: Number of products returned
            - error: Error message if operation failed (only present on failure)
    
    Examples:
        >>> await list_products()
        >>> await list_products(category="electronics")
        >>> await list_products(search_query="laptop", limit=5)
    """
    logger.info(
        f"list_products tool invoked: category={category}, "
        f"search_query={search_query}, limit={limit}"
    )
    
    # Record start time for duration tracking
    start_time = time.time()
    
    try:
        # Validate limit parameter
        if limit < 1:
            limit = 1
        elif limit > 50:
            limit = 50
        
        # Get backend client
        client = get_backend_client()
        
        # Call backend API to retrieve products
        products: List[Product] = await client.get_products(
            category=category,
            search=search_query,
            limit=limit
        )
        
        # Convert Product objects to dictionaries for agent consumption
        product_dicts = [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "price": p.price,
                "category": p.category,
                "in_stock": p.in_stock,
                "image_url": p.image_url
            }
            for p in products
        ]
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        logger.info(
            f"list_products tool completed successfully: "
            f"returned {len(product_dicts)} products"
        )
        
        # Log tool execution
        log_tool_execution(
            logger,
            tool_name="list_products",
            outcome="success",
            duration_ms=round(duration_ms, 2),
            category=category,
            search_query=search_query,
            limit=limit,
            result_count=len(product_dicts)
        )
        
        return {
            "success": True,
            "products": product_dicts,
            "count": len(product_dicts)
        }
        
    except BackendAPIError as e:
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Backend API specific errors
        error_msg = f"Failed to retrieve products from backend: {str(e)}"
        logger.error(f"list_products tool error: {error_msg}")
        
        # Log tool execution failure
        log_tool_execution(
            logger,
            tool_name="list_products",
            outcome="error",
            duration_ms=round(duration_ms, 2),
            error=error_msg,
            category=category,
            search_query=search_query,
            limit=limit
        )
        
        return {
            "success": False,
            "products": [],
            "count": 0,
            "error": error_msg
        }
        
    except Exception as e:
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Unexpected errors
        error_msg = f"Unexpected error while listing products: {str(e)}"
        logger.error(f"list_products tool error: {error_msg}", exc_info=True)
        
        # Log tool execution failure
        log_tool_execution(
            logger,
            tool_name="list_products",
            outcome="error",
            duration_ms=round(duration_ms, 2),
            error=error_msg,
            category=category,
            search_query=search_query,
            limit=limit
        )
        
        return {
            "success": False,
            "products": [],
            "count": 0,
            "error": error_msg
        }
