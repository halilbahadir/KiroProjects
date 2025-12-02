"""
Cart operation tools for the Shopping Assistant Chatbot.

This module provides custom tools for shopping cart management including
adding items, viewing cart contents, and removing items. Tools are decorated
with the Strands Agents SDK @tool decorator to enable agent invocation.
"""

import logging
from typing import Dict, Any, Optional

from strands import tool, ToolContext
import time

from ..backend.client import BackendAPIClient, BackendAPIError, Cart
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


@tool(context=True)
async def add_to_cart(
    product_id: str,
    quantity: int = 1,
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """
    Add a product to the user's shopping cart.
    
    This tool adds items to the user's cart by calling the backend e-commerce API.
    Use this when customers want to purchase products or add items to their cart.
    The user_id is automatically extracted from the invocation context.
    
    Args:
        product_id: Unique identifier of the product to add
        quantity: Number of items to add (default: 1, must be positive)
        tool_context: Context containing user_id from invocation state
    
    Returns:
        Dictionary containing:
            - success: Boolean indicating if the operation succeeded
            - cart: Updated cart information with items, total, and item_count
            - message: Human-readable confirmation message
            - error: Error message if operation failed (only present on failure)
    
    Examples:
        >>> await add_to_cart(product_id="prod-123", quantity=2)
        >>> await add_to_cart(product_id="prod-456")
    """
    # Extract user_id from invocation state
    user_id = tool_context.invocation_state.get("user_id") if tool_context else None
    
    if not user_id:
        error_msg = "User ID not found in invocation state"
        logger.error(f"add_to_cart tool error: {error_msg}")
        return {
            "success": False,
            "cart": None,
            "message": "Unable to add item to cart: user not identified",
            "error": error_msg
        }
    
    logger.info(
        f"add_to_cart tool invoked: user_id={user_id}, "
        f"product_id={product_id}, quantity={quantity}"
    )
    
    # Record start time for duration tracking
    start_time = time.time()
    
    try:
        # Validate quantity parameter
        if quantity < 1:
            error_msg = f"Invalid quantity: {quantity}. Must be at least 1"
            logger.warning(f"add_to_cart tool validation error: {error_msg}")
            return {
                "success": False,
                "cart": None,
                "message": "Unable to add item: quantity must be at least 1",
                "error": error_msg
            }
        
        # Get backend client
        client = get_backend_client()
        
        # Call backend API to add item to cart
        cart: Cart = await client.add_cart_item(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity
        )
        
        # Convert Cart object to dictionary for agent consumption
        cart_dict = {
            "user_id": cart.user_id,
            "items": [
                {
                    "product_id": item.product_id,
                    "product_name": item.product_name,
                    "quantity": item.quantity,
                    "price": item.price,
                    "subtotal": item.subtotal
                }
                for item in cart.items
            ],
            "total": cart.total,
            "item_count": cart.item_count
        }
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        logger.info(
            f"add_to_cart tool completed successfully: "
            f"added {quantity}x {product_id} to cart for user {user_id}"
        )
        
        # Log tool execution
        log_tool_execution(
            logger,
            tool_name="add_to_cart",
            outcome="success",
            duration_ms=round(duration_ms, 2),
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            cart_item_count=cart.item_count,
            cart_total=cart.total
        )
        
        return {
            "success": True,
            "cart": cart_dict,
            "message": f"Successfully added {quantity} item(s) to your cart. "
                      f"Cart now has {cart.item_count} items totaling ${cart.total:.2f}"
        }
        
    except BackendAPIError as e:
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Backend API specific errors
        error_msg = f"Failed to add item to cart: {str(e)}"
        logger.error(f"add_to_cart tool error: {error_msg}")
        
        # Log tool execution failure
        log_tool_execution(
            logger,
            tool_name="add_to_cart",
            outcome="error",
            duration_ms=round(duration_ms, 2),
            error=error_msg,
            user_id=user_id,
            product_id=product_id,
            quantity=quantity
        )
        
        return {
            "success": False,
            "cart": None,
            "message": "Unable to add item to cart. The product may be out of stock or unavailable.",
            "error": error_msg
        }
        
    except Exception as e:
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Unexpected errors
        error_msg = f"Unexpected error while adding to cart: {str(e)}"
        logger.error(f"add_to_cart tool error: {error_msg}", exc_info=True)
        
        # Log tool execution failure
        log_tool_execution(
            logger,
            tool_name="add_to_cart",
            outcome="error",
            duration_ms=round(duration_ms, 2),
            error=error_msg,
            user_id=user_id,
            product_id=product_id,
            quantity=quantity
        )
        
        return {
            "success": False,
            "cart": None,
            "message": "An unexpected error occurred while adding the item to your cart.",
            "error": error_msg
        }


@tool(context=True)
async def view_cart(tool_context: ToolContext) -> Dict[str, Any]:
    """
    View the contents of the user's shopping cart.
    
    This tool retrieves the current cart contents from the backend e-commerce API.
    Use this when customers want to see what's in their cart, review items before
    checkout, or check their cart total. The user_id is automatically extracted
    from the invocation context.
    
    Args:
        tool_context: Context containing user_id from invocation state
    
    Returns:
        Dictionary containing:
            - success: Boolean indicating if the operation succeeded
            - cart: Cart information with items, quantities, prices, and total
            - message: Human-readable summary of cart contents
            - error: Error message if operation failed (only present on failure)
    
    Examples:
        >>> await view_cart()
    """
    # Extract user_id from invocation state
    user_id = tool_context.invocation_state.get("user_id") if tool_context else None
    
    if not user_id:
        error_msg = "User ID not found in invocation state"
        logger.error(f"view_cart tool error: {error_msg}")
        return {
            "success": False,
            "cart": None,
            "message": "Unable to view cart: user not identified",
            "error": error_msg
        }
    
    logger.info(f"view_cart tool invoked: user_id={user_id}")
    
    # Record start time for duration tracking
    start_time = time.time()
    
    try:
        # Get backend client
        client = get_backend_client()
        
        # Call backend API to retrieve cart
        cart: Cart = await client.get_cart(user_id=user_id)
        
        # Convert Cart object to dictionary for agent consumption
        cart_dict = {
            "user_id": cart.user_id,
            "items": [
                {
                    "product_id": item.product_id,
                    "product_name": item.product_name,
                    "quantity": item.quantity,
                    "price": item.price,
                    "subtotal": item.subtotal
                }
                for item in cart.items
            ],
            "total": cart.total,
            "item_count": cart.item_count
        }
        
        # Create human-readable message
        if cart.item_count == 0:
            message = "Your shopping cart is empty."
        else:
            message = (
                f"Your cart contains {cart.item_count} item(s) "
                f"with a total of ${cart.total:.2f}"
            )
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        logger.info(
            f"view_cart tool completed successfully: "
            f"retrieved cart for user {user_id} with {cart.item_count} items"
        )
        
        # Log tool execution
        log_tool_execution(
            logger,
            tool_name="view_cart",
            outcome="success",
            duration_ms=round(duration_ms, 2),
            user_id=user_id,
            cart_item_count=cart.item_count,
            cart_total=cart.total
        )
        
        return {
            "success": True,
            "cart": cart_dict,
            "message": message
        }
        
    except BackendAPIError as e:
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Backend API specific errors
        error_msg = f"Failed to retrieve cart: {str(e)}"
        logger.error(f"view_cart tool error: {error_msg}")
        
        # Log tool execution failure
        log_tool_execution(
            logger,
            tool_name="view_cart",
            outcome="error",
            duration_ms=round(duration_ms, 2),
            error=error_msg,
            user_id=user_id
        )
        
        return {
            "success": False,
            "cart": None,
            "message": "Unable to retrieve your cart at this time.",
            "error": error_msg
        }
        
    except Exception as e:
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Unexpected errors
        error_msg = f"Unexpected error while viewing cart: {str(e)}"
        logger.error(f"view_cart tool error: {error_msg}", exc_info=True)
        
        # Log tool execution failure
        log_tool_execution(
            logger,
            tool_name="view_cart",
            outcome="error",
            duration_ms=round(duration_ms, 2),
            error=error_msg,
            user_id=user_id
        )
        
        return {
            "success": False,
            "cart": None,
            "message": "An unexpected error occurred while retrieving your cart.",
            "error": error_msg
        }


@tool(context=True)
async def remove_from_cart(
    product_id: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Remove a product from the user's shopping cart.
    
    This tool removes items from the user's cart by calling the backend e-commerce API.
    Use this when customers want to remove products they no longer wish to purchase.
    The user_id is automatically extracted from the invocation context.
    
    Args:
        product_id: Unique identifier of the product to remove
        tool_context: Context containing user_id from invocation state
    
    Returns:
        Dictionary containing:
            - success: Boolean indicating if the operation succeeded
            - cart: Updated cart information after removal
            - message: Human-readable confirmation message
            - error: Error message if operation failed (only present on failure)
    
    Examples:
        >>> await remove_from_cart(product_id="prod-123")
    """
    # Extract user_id from invocation state
    user_id = tool_context.invocation_state.get("user_id") if tool_context else None
    
    if not user_id:
        error_msg = "User ID not found in invocation state"
        logger.error(f"remove_from_cart tool error: {error_msg}")
        return {
            "success": False,
            "cart": None,
            "message": "Unable to remove item from cart: user not identified",
            "error": error_msg
        }
    
    logger.info(
        f"remove_from_cart tool invoked: user_id={user_id}, "
        f"product_id={product_id}"
    )
    
    # Record start time for duration tracking
    start_time = time.time()
    
    try:
        # Get backend client
        client = get_backend_client()
        
        # Call backend API to remove item from cart
        cart: Cart = await client.remove_cart_item(
            user_id=user_id,
            product_id=product_id
        )
        
        # Convert Cart object to dictionary for agent consumption
        cart_dict = {
            "user_id": cart.user_id,
            "items": [
                {
                    "product_id": item.product_id,
                    "product_name": item.product_name,
                    "quantity": item.quantity,
                    "price": item.price,
                    "subtotal": item.subtotal
                }
                for item in cart.items
            ],
            "total": cart.total,
            "item_count": cart.item_count
        }
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        logger.info(
            f"remove_from_cart tool completed successfully: "
            f"removed {product_id} from cart for user {user_id}"
        )
        
        # Log tool execution
        log_tool_execution(
            logger,
            tool_name="remove_from_cart",
            outcome="success",
            duration_ms=round(duration_ms, 2),
            user_id=user_id,
            product_id=product_id,
            cart_item_count=cart.item_count,
            cart_total=cart.total
        )
        
        return {
            "success": True,
            "cart": cart_dict,
            "message": f"Successfully removed item from your cart. "
                      f"Cart now has {cart.item_count} items totaling ${cart.total:.2f}"
        }
        
    except BackendAPIError as e:
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Backend API specific errors
        error_msg = f"Failed to remove item from cart: {str(e)}"
        logger.error(f"remove_from_cart tool error: {error_msg}")
        
        # Log tool execution failure
        log_tool_execution(
            logger,
            tool_name="remove_from_cart",
            outcome="error",
            duration_ms=round(duration_ms, 2),
            error=error_msg,
            user_id=user_id,
            product_id=product_id
        )
        
        return {
            "success": False,
            "cart": None,
            "message": "Unable to remove item from cart. The item may not be in your cart.",
            "error": error_msg
        }
        
    except Exception as e:
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Unexpected errors
        error_msg = f"Unexpected error while removing from cart: {str(e)}"
        logger.error(f"remove_from_cart tool error: {error_msg}", exc_info=True)
        
        # Log tool execution failure
        log_tool_execution(
            logger,
            tool_name="remove_from_cart",
            outcome="error",
            duration_ms=round(duration_ms, 2),
            error=error_msg,
            user_id=user_id,
            product_id=product_id
        )
        
        return {
            "success": False,
            "cart": None,
            "message": "An unexpected error occurred while removing the item from your cart.",
            "error": error_msg
        }
