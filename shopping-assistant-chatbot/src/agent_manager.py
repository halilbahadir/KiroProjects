"""
Agent Manager for the Shopping Assistant Chatbot Service.

This module initializes and manages the Strands Agent lifecycle, including
Bedrock model configuration, tool registration, and conversation state management.
"""

import logging
import os
from typing import Optional, Dict, Any
from uuid import uuid4

from strands import Agent
from strands.models.bedrock import BedrockModel

from .config import get_config, Config
from .tools.product_tools import list_products
from .tools.cart_tools import add_to_cart, view_cart, remove_from_cart
from .tools.recommendation_tools import recommend_products


logger = logging.getLogger(__name__)


class AgentManager:
    """
    Manages the Strands Agent lifecycle and conversation state.
    
    This class initializes the Bedrock model with AWS credentials, configures
    the agent with custom tools, and provides methods for processing user messages
    with conversation context.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the Agent Manager with Bedrock model and custom tools.
        
        Args:
            config: Optional configuration object. If not provided, loads from environment.
        
        Raises:
            ValueError: If AWS credentials are invalid or Bedrock initialization fails
        """
        # Load configuration
        self.config = config or get_config()
        
        logger.info("Initializing AgentManager")
        
        # Initialize Bedrock model
        self._initialize_bedrock_model()
        
        # Initialize agent with tools and system prompt
        self._initialize_agent()
        
        # Conversation state storage (session_id -> conversation history)
        self._conversations: Dict[str, list] = {}
        
        logger.info("AgentManager initialized successfully")
    
    def _initialize_bedrock_model(self) -> None:
        """
        Initialize the Bedrock model with credentials from configuration.
        
        Raises:
            ValueError: If Bedrock initialization fails
        """
        try:
            logger.info(
                f"Initializing Bedrock model: {self.config.BEDROCK_MODEL_ID} "
                f"in region {self.config.AWS_REGION}"
            )
            
            # Create Bedrock model with configuration
            # If credentials are not provided in config, boto3 will use AWS CLI default credentials
            model_kwargs = {
                "model_id": self.config.BEDROCK_MODEL_ID,
                "temperature": self.config.BEDROCK_TEMPERATURE,
                "max_tokens": self.config.BEDROCK_MAX_TOKENS
            }
            
            # Only add credentials if they are explicitly provided
            if self.config.AWS_ACCESS_KEY_ID and self.config.AWS_SECRET_ACCESS_KEY:
                logger.info("Using explicit AWS credentials from configuration")
                # Note: BedrockModel doesn't accept these parameters directly
                # We need to set up boto3 session instead
                import boto3
                session = boto3.Session(
                    aws_access_key_id=self.config.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=self.config.AWS_SECRET_ACCESS_KEY,
                    aws_session_token=self.config.AWS_SESSION_TOKEN,
                    region_name=self.config.AWS_REGION
                )
                # BedrockModel will use the default session, so we set environment variables
                os.environ['AWS_ACCESS_KEY_ID'] = self.config.AWS_ACCESS_KEY_ID
                os.environ['AWS_SECRET_ACCESS_KEY'] = self.config.AWS_SECRET_ACCESS_KEY
                if self.config.AWS_SESSION_TOKEN:
                    os.environ['AWS_SESSION_TOKEN'] = self.config.AWS_SESSION_TOKEN
                os.environ['AWS_REGION'] = self.config.AWS_REGION
            else:
                logger.info("Using AWS CLI default credentials (no explicit credentials provided)")
                # Ensure region is set
                os.environ['AWS_REGION'] = self.config.AWS_REGION
            
            self.model = BedrockModel(**model_kwargs)
            
            logger.info("Bedrock model initialized successfully")
            
        except Exception as e:
            error_msg = f"Failed to initialize Bedrock model: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg) from e
    
    def _initialize_agent(self) -> None:
        """
        Initialize the Strands Agent with custom tools and system prompt.
        
        The agent is configured with:
        - All custom tools for product, cart, and recommendation operations
        - A system prompt defining the chatbot's personality and capabilities
        - The Bedrock model for natural language understanding and generation
        """
        # Define system prompt
        system_prompt = """You are a helpful shopping assistant for an e-commerce platform.

Your role is to help customers:
- Browse and search for products in our catalog
- Add items to their shopping cart
- View and manage their cart contents
- Get personalized product recommendations
- Answer questions about products and shopping

Guidelines:
- Be friendly, helpful, and conversational
- Provide clear and concise information
- When showing products, include relevant details like name, price, and availability
- If a customer's request fails, explain what happened and suggest alternatives
- Always confirm actions like adding or removing items from the cart
- When recommending products, explain why they might be a good fit

You have access to the following tools:
- list_products: Browse the product catalog with optional filters
- add_to_cart: Add products to the customer's shopping cart
- view_cart: Show the customer what's in their cart
- remove_from_cart: Remove items from the cart
- recommend_products: Get personalized product recommendations

Use these tools to help customers with their shopping needs."""

        # Register all custom tools
        tools = [
            list_products,
            add_to_cart,
            view_cart,
            remove_from_cart,
            recommend_products
        ]
        
        logger.info(f"Registering {len(tools)} custom tools with agent")
        
        # Create agent with model, tools, and system prompt
        self.agent = Agent(
            model=self.model,
            tools=tools,
            system_prompt=system_prompt
        )
        
        logger.info("Agent initialized with custom tools and system prompt")
    
    async def process_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and return the agent's response.
        
        This method invokes the agent with the user's message, maintaining
        conversation context across multiple exchanges within a session.
        The user_id is passed in the invocation_state to enable tools to
        access user-specific data like shopping carts.
        
        Args:
            message: The user's message to process
            session_id: Optional session identifier for conversation continuity.
                       If not provided, a new session is created.
            user_id: Optional user identifier for personalization and cart operations.
                    If not provided, defaults to "anonymous".
        
        Returns:
            Dictionary containing:
                - response: The agent's natural language response
                - session_id: The session identifier for this conversation
                - status: "success" or "error"
                - error: Error message if processing failed (only present on failure)
        
        Examples:
            >>> response = await agent_manager.process_message(
            ...     message="Show me laptops",
            ...     session_id="session-123",
            ...     user_id="user-456"
            ... )
        """
        # Generate session_id if not provided
        if not session_id:
            session_id = str(uuid4())
            logger.info(f"Created new session: {session_id}")
        
        # Default user_id if not provided
        if not user_id:
            user_id = "anonymous"
        
        logger.info(
            f"Processing message for session {session_id}, user {user_id}: "
            f"{message[:100]}..."
        )
        
        try:
            # Prepare invocation state with user_id for tools
            invocation_state = {
                "user_id": user_id,
                "session_id": session_id
            }
            
            # Get or initialize conversation history for this session
            if session_id not in self._conversations:
                self._conversations[session_id] = []
                logger.debug(f"Initialized conversation history for session {session_id}")
            
            # Invoke agent with message and invocation state
            response = await self.agent.invoke_async(
                message,
                invocation_state=invocation_state
            )
            
            # Extract response text
            response_text = response.get("output", "")
            
            # Update conversation history
            self._conversations[session_id].append({
                "role": "user",
                "content": message
            })
            self._conversations[session_id].append({
                "role": "assistant",
                "content": response_text
            })
            
            logger.info(
                f"Message processed successfully for session {session_id}: "
                f"response length {len(response_text)} chars"
            )
            
            return {
                "response": response_text,
                "session_id": session_id,
                "status": "success"
            }
            
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            logger.error(
                f"Failed to process message for session {session_id}: {error_msg}",
                exc_info=True
            )
            
            return {
                "response": "I apologize, but I encountered an error processing your request. "
                           "Please try again or rephrase your question.",
                "session_id": session_id,
                "status": "error",
                "error": error_msg
            }
    
    def get_agent(self) -> Agent:
        """
        Get the configured agent instance.
        
        Returns:
            Agent: The Strands Agent instance
        """
        return self.agent
    
    def get_conversation_history(self, session_id: str) -> list:
        """
        Get the conversation history for a specific session.
        
        Args:
            session_id: The session identifier
        
        Returns:
            List of conversation messages with role and content
        """
        return self._conversations.get(session_id, [])
    
    def clear_conversation(self, session_id: str) -> None:
        """
        Clear the conversation history for a specific session.
        
        Args:
            session_id: The session identifier
        """
        if session_id in self._conversations:
            del self._conversations[session_id]
            logger.info(f"Cleared conversation history for session {session_id}")
    
    def clear_all_conversations(self) -> None:
        """Clear all conversation histories."""
        self._conversations.clear()
        logger.info("Cleared all conversation histories")
