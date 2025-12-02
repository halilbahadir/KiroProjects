# Implementation Plan

- [x] 1. Set up project structure and dependencies
  - Create directory structure for src/, tests/, and configuration files
  - Initialize Python package with __init__.py files
  - Create requirements.txt with all dependencies (strands-agents, fastapi, boto3, httpx, pydantic, pytest, hypothesis)
  - Create .env.example file with required environment variables
  - Create README.md with setup instructions
  - _Requirements: 2.1, 8.1_

- [x] 2. Implement configuration management
  - Create config.py to load environment variables for AWS credentials, Bedrock settings, server configuration, and backend API settings
  - Implement validation for required environment variables
  - Add default values for optional configuration
  - _Requirements: 2.1, 2.2_

- [ ]* 2.1 Write property test for configuration validation
  - **Property 5: Credentials are read from environment**
  - **Validates: Requirements 2.3**

- [x] 3. Implement Backend API client
  - Create backend/client.py with BackendAPIClient class
  - Implement async methods for get_products, get_cart, add_cart_item, remove_cart_item, get_recommendations
  - Add authentication header handling
  - Implement error handling and retries with exponential backoff
  - _Requirements: 3.1, 4.2, 5.1, 6.2, 7.2, 10.2, 10.3_

- [ ]* 3.1 Write property test for backend API authentication
  - **Property 28: Authentication headers are included**
  - **Validates: Requirements 10.3**

- [ ]* 3.2 Write unit tests for backend client methods
  - Test HTTP request formatting
  - Test response parsing
  - Test timeout handling
  - _Requirements: 3.1, 4.2, 5.1, 6.2, 7.2_

- [x] 4. Implement data models
  - Create api/models.py with Pydantic models for ChatRequest, ChatResponse, Product, CartItem, Cart, AWSCredentials
  - Add field validation and constraints
  - _Requirements: 1.2, 1.5, 3.2, 5.2_

- [ ]* 4.1 Write property test for product data structure
  - **Property 7: Product data structure is complete**
  - **Validates: Requirements 3.2**

- [ ]* 4.2 Write property test for cart data structure
  - **Property 12: Cart data structure is complete**
  - **Validates: Requirements 5.2**

- [x] 5. Implement custom tools for product operations
  - Create tools/product_tools.py with list_products tool using @tool decorator
  - Implement async function that calls BackendAPIClient.get_products
  - Add proper docstrings and type hints
  - Implement error handling for backend failures
  - _Requirements: 3.1, 3.2, 3.4, 10.1, 10.2, 10.4_

- [ ]* 5.1 Write property test for list products tool invocation
  - **Property 6: Product listing tool is invoked**
  - **Validates: Requirements 3.1**

- [ ]* 5.2 Write property test for tool decorator usage
  - **Property 26: Tools use SDK decorators**
  - **Validates: Requirements 10.1**

- [ ]* 5.3 Write property test for tools calling backend APIs
  - **Property 27: Tools call backend APIs**
  - **Validates: Requirements 10.2**

- [ ]* 5.4 Write property test for structured data return
  - **Property 29: Tools return structured data**
  - **Validates: Requirements 10.4**

- [x] 6. Implement custom tools for cart operations
  - Create tools/cart_tools.py with add_to_cart, view_cart, remove_from_cart tools using @tool decorator
  - Use ToolContext to access user_id from invocation_state
  - Implement async functions that call BackendAPIClient methods
  - Add proper docstrings and type hints
  - Implement error handling for backend failures
  - _Requirements: 4.1, 4.2, 5.1, 5.2, 6.1, 6.2, 10.1, 10.2, 10.4_

- [ ]* 6.1 Write property test for add to cart tool invocation
  - **Property 8: Add to cart tool is invoked**
  - **Validates: Requirements 4.1**

- [ ]* 6.2 Write property test for backend API calls on cart updates
  - **Property 9: Backend API is called for cart updates**
  - **Validates: Requirements 4.2**

- [ ]* 6.3 Write property test for cart addition confirmation
  - **Property 10: Cart addition is confirmed**
  - **Validates: Requirements 4.3**

- [ ]* 6.4 Write property test for view cart tool invocation
  - **Property 11: View cart tool is invoked**
  - **Validates: Requirements 5.1**

- [ ]* 6.5 Write property test for remove from cart tool invocation
  - **Property 13: Remove from cart tool is invoked**
  - **Validates: Requirements 6.1**

- [ ]* 6.6 Write property test for backend API calls on cart removal
  - **Property 14: Backend API is called for cart removal**
  - **Validates: Requirements 6.2**

- [ ]* 6.7 Write property test for cart removal confirmation
  - **Property 15: Cart removal is confirmed**
  - **Validates: Requirements 6.3**

- [x] 7. Implement custom tools for recommendations
  - Create tools/recommendation_tools.py with recommend_products tool using @tool decorator
  - Implement async function that calls BackendAPIClient.get_recommendations
  - Add proper docstrings and type hints
  - Implement error handling for backend failures
  - _Requirements: 7.1, 7.2, 10.1, 10.2, 10.4_

- [ ]* 7.1 Write property test for recommendation tool invocation
  - **Property 16: Recommendation tool is invoked**
  - **Validates: Requirements 7.1**

- [ ]* 7.2 Write property test for recommendations from catalog
  - **Property 17: Recommendations come from catalog**
  - **Validates: Requirements 7.2**

- [ ]* 7.3 Write property test for recommendation data completeness
  - **Property 18: Recommendation data is complete**
  - **Validates: Requirements 7.3**

- [x] 8. Implement logging utilities
  - Create utils/logging.py with logging configuration
  - Implement structured logging with JSON format
  - Add log level configuration from environment
  - _Requirements: 9.1, 9.2, 9.4, 9.5_

- [x] 9. Implement security utilities
  - Create utils/security.py with redaction functions for credentials and PII
  - Implement functions to sanitize log messages
  - Add pattern matching for common sensitive data (emails, credit cards, API keys)
  - _Requirements: 9.3_

- [ ]* 9.1 Write property test for sensitive data redaction
  - **Property 24: Sensitive data is redacted**
  - **Validates: Requirements 9.3**

- [x] 10. Implement Agent Manager
  - Create agent_manager.py with AgentManager class
  - Initialize BedrockModel with credentials from config
  - Configure model with temperature=0.7, max_tokens=2048, model_id="us.amazon.nova-pro-v1:0"
  - Create Agent with all custom tools and system prompt
  - Implement process_message method that invokes agent with user_id in invocation_state
  - Add conversation state management
  - _Requirements: 1.1, 1.3, 2.3_

- [ ]* 10.1 Write property test for message processing
  - **Property 1: Message processing returns responses**
  - **Validates: Requirements 1.1**

- [ ]* 10.2 Write property test for conversation context
  - **Property 3: Conversation context is maintained**
  - **Validates: Requirements 1.3**

- [x] 11. Implement HTTP API routes
  - Create api/routes.py with FastAPI router
  - Implement POST /chat endpoint that accepts ChatRequest and returns ChatResponse
  - Add request validation using Pydantic models
  - Implement error handling for validation errors (400), service errors (503), and system errors (500)
  - Add logging for all requests and responses
  - _Requirements: 1.2, 1.5, 8.2, 8.3, 8.4, 9.1_

- [ ]* 11.1 Write property test for HTTP endpoint acceptance
  - **Property 2: HTTP endpoint accepts valid requests**
  - **Validates: Requirements 1.2**

- [ ]* 11.2 Write property test for POST request acceptance
  - **Property 19: POST requests are accepted**
  - **Validates: Requirements 8.2**

- [ ]* 11.3 Write property test for request validation
  - **Property 20: Request validation occurs**
  - **Validates: Requirements 8.3**

- [ ]* 11.4 Write property test for JSON response format
  - **Property 4: Responses are valid JSON**
  - **Validates: Requirements 1.5**

- [ ]* 11.5 Write unit tests for API routes
  - Test request validation
  - Test response formatting
  - Test error responses
  - _Requirements: 1.2, 1.5, 8.2, 8.3, 8.4_

- [x] 12. Implement main application
  - Create main.py with FastAPI application initialization
  - Configure CORS middleware with appropriate headers
  - Add health check endpoints (/health, /health/ready)
  - Wire up routes from api/routes.py
  - Initialize AgentManager on startup
  - Add startup and shutdown event handlers with logging
  - _Requirements: 8.1, 8.5, 9.4_

- [ ]* 12.1 Write property test for CORS headers
  - **Property 21: CORS headers are present**
  - **Validates: Requirements 8.5**

- [x] 13. Implement logging for requests and tool executions
  - Add logging middleware to FastAPI application
  - Log incoming requests with message and session_id
  - Log outgoing responses
  - Log tool invocations in each custom tool
  - Log errors with context
  - Use security utilities to redact sensitive data
  - _Requirements: 9.1, 9.2, 9.3, 9.5_

- [ ]* 13.1 Write property test for request logging
  - **Property 22: Requests are logged**
  - **Validates: Requirements 9.1**

- [ ]* 13.2 Write property test for error logging
  - **Property 23: Errors are logged with context**
  - **Validates: Requirements 9.2**

- [ ]* 13.3 Write property test for tool execution logging
  - **Property 25: Tool executions are logged**
  - **Validates: Requirements 9.5**

- [x] 14. Create Docker configuration
  - Create Dockerfile with Python 3.11 base image
  - Install dependencies from requirements.txt
  - Copy source code
  - Set environment variables
  - Expose port 8000
  - Set CMD to run uvicorn server
  - _Requirements: 8.1_

- [x] 15. Create documentation
  - Update README.md with setup instructions, environment variable configuration, running the service, API documentation, and testing instructions
  - Document all environment variables in .env.example
  - Add API endpoint documentation with request/response examples
  - _Requirements: 2.1, 8.1, 8.2_

- [x] 16. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
