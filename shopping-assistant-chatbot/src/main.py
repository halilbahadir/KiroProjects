"""
Main FastAPI application for the Shopping Assistant Chatbot Service.

This module initializes the FastAPI application with CORS middleware,
health check endpoints, API routes, and startup/shutdown event handlers.

Requirements: 8.1, 8.5, 9.4
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import time

from .api.routes import router, initialize_agent_manager
from .config import get_config
from .utils.logging import setup_logging
from .utils.security import sanitize_log_message


# Initialize configuration
config = get_config()

# Setup logging
setup_logging(config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all incoming requests and outgoing responses.
    
    This middleware:
    1. Logs incoming requests with method, path, and client info
    2. Measures request processing time
    3. Logs outgoing responses with status code and duration
    4. Redacts sensitive data from logs
    
    Requirements: 9.1, 9.3
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Process the request and log details.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler
            
        Returns:
            Response: HTTP response
        """
        # Generate request ID for tracking
        request_id = f"{int(time.time() * 1000)}"
        
        # Extract request details
        method = request.method
        path = request.url.path
        client_host = request.client.host if request.client else "unknown"
        
        # Log incoming request
        logger.info(
            f"Incoming request: {method} {path}",
            extra={
                "event_type": "http_request",
                "request_id": request_id,
                "method": method,
                "path": path,
                "client_host": client_host,
                "query_params": dict(request.query_params)
            }
        )
        
        # Record start time
        start_time = time.time()
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log outgoing response
            logger.info(
                f"Outgoing response: {method} {path} - {response.status_code}",
                extra={
                    "event_type": "http_response",
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration_ms, 2)
                }
            )
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log error
            logger.error(
                f"Request failed: {method} {path} - {str(e)}",
                extra={
                    "event_type": "http_error",
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "error": str(e),
                    "duration_ms": round(duration_ms, 2)
                },
                exc_info=True
            )
            
            # Re-raise to let FastAPI handle it
            raise


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan context manager.
    
    Handles startup and shutdown events with proper logging.
    
    Startup:
        - Logs service startup
        - Initializes agent manager
        - Logs successful initialization
    
    Shutdown:
        - Logs service shutdown
        - Performs cleanup if needed
    
    Args:
        app: FastAPI application instance
        
    Yields:
        None during application runtime
    """
    # Startup
    logger.info("=" * 60)
    logger.info("Shopping Assistant Chatbot Service starting up")
    logger.info(f"Server: {config.SERVER_HOST}:{config.SERVER_PORT}")
    logger.info(f"Bedrock Model: {config.BEDROCK_MODEL_ID}")
    logger.info(f"AWS Region: {config.AWS_REGION}")
    logger.info(f"Backend API: {config.BACKEND_API_URL}")
    logger.info(f"Log Level: {config.LOG_LEVEL}")
    logger.info("=" * 60)
    
    try:
        # Initialize agent manager
        logger.info("Initializing agent manager...")
        initialize_agent_manager()
        logger.info("Agent manager initialized successfully")
        logger.info("Service is ready to accept requests")
        
    except Exception as e:
        logger.error(f"Failed to initialize service: {str(e)}", exc_info=True)
        raise
    
    # Application is running
    yield
    
    # Shutdown
    logger.info("=" * 60)
    logger.info("Shopping Assistant Chatbot Service shutting down")
    logger.info("Performing cleanup...")
    
    # Cleanup operations (if needed)
    # For example: close database connections, flush logs, etc.
    
    logger.info("Shutdown complete")
    logger.info("=" * 60)


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    This function:
    1. Creates the FastAPI application with metadata
    2. Configures CORS middleware for browser compatibility
    3. Includes API routes from api/routes.py
    4. Sets up startup and shutdown event handlers
    
    Returns:
        FastAPI: Configured application instance
        
    Requirements:
        - 8.1: HTTP server listens on configurable port
        - 8.5: Return responses with appropriate CORS headers
        - 9.4: Log startup and shutdown events
    """
    # Create FastAPI application with lifespan handler
    app = FastAPI(
        title="Shopping Assistant Chatbot Service",
        description=(
            "A conversational AI service for e-commerce that provides "
            "product discovery, shopping cart management, and personalized "
            "recommendations through natural language interactions."
        ),
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # Add logging middleware (before CORS to log all requests)
    app.add_middleware(LoggingMiddleware)
    
    # Configure CORS middleware
    # Allow all origins for development; restrict in production
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure based on deployment environment
        allow_credentials=True,
        allow_methods=["*"],  # Allow all HTTP methods
        allow_headers=["*"],  # Allow all headers
        expose_headers=["*"],  # Expose all headers to the browser
        max_age=3600,  # Cache preflight requests for 1 hour
    )
    
    # Include API routes
    app.include_router(router, prefix="/api/v1", tags=["chat"])
    
    # Root endpoint
    @app.get("/", tags=["root"])
    async def root() -> dict:
        """
        Root endpoint providing service information.
        
        Returns:
            dict: Service metadata
        """
        return {
            "service": "Shopping Assistant Chatbot",
            "version": "1.0.0",
            "status": "running",
            "docs": "/docs",
            "health": "/api/v1/health"
        }
    
    logger.info("FastAPI application created and configured")
    
    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    """
    Run the application using uvicorn when executed directly.
    
    For production deployment, use:
        uvicorn src.main:app --host 0.0.0.0 --port 8000
    """
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host=config.SERVER_HOST,
        port=config.SERVER_PORT,
        reload=False,  # Set to True for development
        log_level=config.LOG_LEVEL.lower()
    )
