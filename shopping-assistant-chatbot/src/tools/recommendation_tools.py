"""
Recommendation tools for the Shopping Assistant Chatbot.

This module provides custom tools for product recommendation operations.
Tools are decorated with the Strands Agents SDK @tool decorator to enable
agent invocation.
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
async def recommend_products(
    user_preferences: Optional[str] = None,
    limit: int = 5
) -> Dict[str, Any]:
    """
    Get product recommendations based on the e-shop catalog.
    
    This tool retrieves personalized product recommendations from the backend
    e-commerce API. Recommendations are based on the available product catalog
    and can be filtered by user preferences. Use this when customers ask for
    suggestions, want to discover new products, or need help finding items
    that match their interests.
    
    Args:
        user_preferences: Optional description of user preferences or interests
                         (e.g., "electronics for gaming", "casual clothing")
        limit: Maximum number of recommendations to return (default: 5, max: 20)
    
    Returns:
        Dictionary containing:
            - success: Boolean indicating if the operation succeeded
            - recommendations: List of product dictionaries with id, name,
                             description, price, category, in_stock, and image_url
            - count: Number of recommendations returned
            - error: Error message if operation failed (only present on failure)
    
    Examples:
        >>> await recommend_products()
        >>> await recommend_products(user_preferences="outdoor gear")
        >>> await recommend_products(user_preferences="budget laptops", limit=3)
    """
    logger.info(
        f"recommend_products tool invoked: "
        f"user_preferences={user_preferences}, limit={limit}"
    )
    
    # Record start time for duration tracking
    start_time = time.time()
    
    try:
        # Validate limit parameter
        if limit < 1:
            limit = 1
        elif limit > 20:
            limit = 20
        
        # Get backend client
        client = get_backend_client()
        
        # Call backend API to retrieve recommendations
        recommendations: List[Product] = await client.get_recommendations(
            preferences=user_preferences,
            limit=limit
        )
        
        # Convert Product objects to dictionaries for agent consumption
        recommendation_dicts = [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "price": p.price,
                "category": p.category,
                "in_stock": p.in_stock,
                "image_url": p.image_url
            }
            for p in recommendations
        ]
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        logger.info(
            f"recommend_products tool completed successfully: "
            f"returned {len(recommendation_dicts)} recommendations"
        )
        
        # Log tool execution
        log_tool_execution(
            logger,
            tool_name="recommend_products",
            outcome="success",
            duration_ms=round(duration_ms, 2),
            user_preferences=user_preferences,
            limit=limit,
            result_count=len(recommendation_dicts)
        )
        
        return {
            "success": True,
            "recommendations": recommendation_dicts,
            "count": len(recommendation_dicts)
        }
        
    except BackendAPIError as e:
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Backend API specific errors
        error_msg = f"Failed to retrieve recommendations from backend: {str(e)}"
        logger.error(f"recommend_products tool error: {error_msg}")
        
        # Log tool execution failure
        log_tool_execution(
            logger,
            tool_name="recommend_products",
            outcome="error",
            duration_ms=round(duration_ms, 2),
            error=error_msg,
            user_preferences=user_preferences,
            limit=limit
        )
        
        return {
            "success": False,
            "recommendations": [],
            "count": 0,
            "error": error_msg
        }
        
    except Exception as e:
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Unexpected errors
        error_msg = f"Unexpected error while getting recommendations: {str(e)}"
        logger.error(f"recommend_products tool error: {error_msg}", exc_info=True)
        
        # Log tool execution failure
        log_tool_execution(
            logger,
            tool_name="recommend_products",
            outcome="error",
            duration_ms=round(duration_ms, 2),
            error=error_msg,
            user_preferences=user_preferences,
            limit=limit
        )
        
        return {
            "success": False,
            "recommendations": [],
            "count": 0,
            "error": error_msg
        }
