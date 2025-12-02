"""
HTTP API routes for the Shopping Assistant Chatbot Service.

This module implements FastAPI routes for the chat endpoint, including
request validation, error handling, and logging for all requests and responses.

Requirements: 1.2, 1.5, 8.2, 8.3, 8.4, 9.1
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from ..api.models import ChatRequest, ChatResponse
from ..agent_manager import AgentManager
from ..config import get_config
from ..utils.logging import log_request, log_response, log_error
from ..utils.security import sanitize_log_message


# Initialize logger
logger = logging.getLogger(__name__)

# Create FastAPI router
router = APIRouter()

# Global agent manager instance (initialized on startup)
_agent_manager: Optional[AgentManager] = None


def initialize_agent_manager() -> None:
    """
    Initialize the global agent manager instance.
    
    This should be called during application startup to ensure the agent
    is ready to process requests.
    
    Raises:
        ValueError: If agent initialization fails
    """
    global _agent_manager
    
    try:
        logger.info("Initializing agent manager for API routes")
        config = get_config()
        _agent_manager = AgentManager(config)
        logger.info("Agent manager initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize agent manager: {str(e)}", exc_info=True)
        raise ValueError(f"Agent initialization failed: {str(e)}") from e


def get_agent_manager() -> AgentManager:
    """
    Get the global agent manager instance.
    
    Returns:
        AgentManager: The initialized agent manager
        
    Raises:
        RuntimeError: If agent manager is not initialized
    """
    if _agent_manager is None:
        raise RuntimeError(
            "Agent manager not initialized. Call initialize_agent_manager() first."
        )
    return _agent_manager


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Successful response",
            "model": ChatResponse
        },
        400: {
            "description": "Bad Request - Invalid request format or validation error",
            "content": {
                "application/json": {
                    "example": {
                        "response": "Invalid request format",
                        "session_id": "",
                        "status": "error",
                        "error": "Message cannot be empty or only whitespace"
                    }
                }
            }
        },
        500: {
            "description": "Internal Server Error - System error",
            "content": {
                "application/json": {
                    "example": {
                        "response": "An internal error occurred",
                        "session_id": "",
                        "status": "error",
                        "error": "System error occurred"
                    }
                }
            }
        },
        503: {
            "description": "Service Unavailable - Agent or backend service error",
            "content": {
                "application/json": {
                    "example": {
                        "response": "Service temporarily unavailable",
                        "session_id": "",
                        "status": "error",
                        "error": "Bedrock service unavailable"
                    }
                }
            }
        }
    },
    summary="Process chat message",
    description="""
    Process a user message and return the chatbot's response.
    
    This endpoint accepts a chat message from the frontend, processes it through
    the Strands Agent with Bedrock Nova Pro, and returns a natural language response.
    
    The endpoint maintains conversation context across multiple messages within a session.
    """
)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """
    Handle incoming chat requests from the frontend.
    
    This endpoint:
    1. Validates the incoming request using Pydantic models
    2. Logs the incoming request (with sensitive data redacted)
    3. Processes the message through the agent manager
    4. Logs the outgoing response
    5. Returns the response in the expected format
    6. Handles errors appropriately with proper HTTP status codes
    
    Args:
        request: ChatRequest containing user message, session_id, and user_id
        
    Returns:
        ChatResponse: Agent's response with session_id and status
        
    Raises:
        HTTPException: 
            - 400 for validation errors
            - 503 for service unavailability
            - 500 for system errors
            
    Requirements:
        - 1.2: Accept POST requests with JSON payloads
        - 1.5: Return responses in JSON format with appropriate status codes
        - 8.2: Accept POST requests to chat endpoint
        - 8.3: Validate JSON payload structure
        - 8.4: Return 400 for malformed requests
        - 9.1: Log all requests and responses
    """
    session_id = request.session_id or ""
    user_id = request.user_id or "anonymous"
    
    try:
        # Log incoming request (with sensitive data redacted)
        redacted_message = sanitize_log_message(request.message)
        log_request(
            logger,
            message=redacted_message,
            session_id=session_id,
            user_id=user_id
        )
        
        # Get agent manager
        try:
            agent_manager = get_agent_manager()
        except RuntimeError as e:
            logger.error(f"Agent manager not available: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service temporarily unavailable"
            )
        
        # Process message through agent
        result = await agent_manager.process_message(
            message=request.message,
            session_id=request.session_id,
            user_id=request.user_id
        )
        
        # Create response object
        response = ChatResponse(
            response=result["response"],
            session_id=result["session_id"],
            status=result["status"],
            error=result.get("error")
        )
        
        # Log outgoing response (with sensitive data redacted)
        redacted_response = sanitize_log_message(response.response)
        log_response(
            logger,
            response=redacted_response,
            session_id=response.session_id,
            user_id=user_id,
            status=response.status
        )
        
        # If the agent returned an error status, return 503
        if response.status == "error":
            logger.warning(
                f"Agent returned error status for session {session_id}: {response.error}"
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=response.error or "Service error occurred"
            )
        
        return response
        
    except ValidationError as e:
        # Validation error (400 Bad Request)
        error_msg = f"Request validation failed: {str(e)}"
        logger.warning(error_msg)
        log_error(
            logger,
            error=e,
            context={"request": request.dict()},
            session_id=session_id,
            user_id=user_id
        )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (already have proper status codes)
        raise
        
    except Exception as e:
        # System error (500 Internal Server Error)
        error_msg = f"System error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        log_error(
            logger,
            error=e,
            context={"request": request.dict()},
            session_id=session_id,
            user_id=user_id
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred"
        )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Basic health check endpoint to verify service is running"
)
async def health_check() -> dict:
    """
    Basic health check endpoint.
    
    Returns:
        dict: Health status
    """
    return {
        "status": "healthy",
        "service": "shopping-assistant-chatbot"
    }


@router.get(
    "/health/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness check",
    description="Readiness check endpoint to verify service is ready to accept requests"
)
async def readiness_check() -> dict:
    """
    Readiness check endpoint.
    
    Verifies that the agent manager is initialized and ready to process requests.
    
    Returns:
        dict: Readiness status
        
    Raises:
        HTTPException: 503 if service is not ready
    """
    try:
        agent_manager = get_agent_manager()
        return {
            "status": "ready",
            "service": "shopping-assistant-chatbot",
            "agent_initialized": True
        }
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready - agent manager not initialized"
        )
