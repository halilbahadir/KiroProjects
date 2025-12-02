"""
API module for the Shopping Assistant Chatbot Service.

This module contains HTTP API routes, request/response models,
and related API functionality.
"""

from .routes import router, initialize_agent_manager

__all__ = ["router", "initialize_agent_manager"]
