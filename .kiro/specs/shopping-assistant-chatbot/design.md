# Design Document

## Overview

The Shopping Assistant Chatbot Service is a Python-based conversational AI system that enables customers to interact with an e-commerce platform through natural language. The system leverages the Strands Agents SDK to build an intelligent agent powered by Amazon Bedrock Nova Pro, providing capabilities for product discovery, shopping cart management, and personalized recommendations.

The architecture follows a three-tier design:
1. **Frontend Layer**: A popup chatbot component that provides the user interface
2. **Service Layer**: An HTTP server that handles API requests and manages agent interactions
3. **Integration Layer**: Custom tools that interface with existing backend e-commerce APIs

The service is designed to be stateless at the HTTP layer, with conversation state managed by the Strands Agent framework. AWS credentials are configured via environment variables, ensuring secure authentication without hardcoded secrets.

## Architecture

### System Components

```
┌─────────────────────┐
│  Frontend Popup     │
│  Chatbot Component  │
└──────────┬──────────┘
           │ HTTP POST
           │ (JSON)
           ▼
┌─────────────────────┐
│   HTTP Server       │
│   (Flask/FastAPI)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Strands Agent      │
│  + Bedrock Nova Pro │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Custom Tools      │
│  - list_products    │
│  - add_to_cart      │
│  - view_cart        │
│  - remove_from_cart │
│  - recommend        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Backend APIs       │
│  (E-commerce)       │
└─────────────────────┘
```

### Technology Stack

- **Agent Framework**: Strands Agents SDK (latest version)
- **LLM Provider**: Amazon Bedrock with Nova Pro model (`us.amazon.nova-pro-v1:0`)
- **HTTP Server**: FastAPI (for async support and automatic OpenAPI documentation)
- **AWS SDK**: boto3 for Bedrock authentication
- **Testing**: pytest with pytest-asyncio for async testing
- **Property Testing**: Hypothesis for property-based testing
- **HTTP Client**: httpx for testing HTTP endpoints

### Deployment Considerations

- The service runs as a standalone Python application
- Environment variables provide AWS credentials and configuration
- The HTTP server listens on a configurable port (default: 8000)
- CORS headers are configured to allow frontend integration
- Logging is configured to stdout for container-friendly deployment

## Components and Interfaces

### 1. HTTP Server Component

**Responsibility**: Expose REST API endpoints for frontend communication

**Interface**:
```python
POST /chat
Content-Type: application/json

Request:
{
  "message": str,           # User's message
  "session_id": str,        # Optional session identifier
  "user_id": str           # Optional user identifier
}

Response:
{
  "response": str,          # Agent's response
  "session_id": str,        # Session identifier
  "status": "success" | "error",
  "error": str             # Optional error message
}
```

**Key Methods**:
- `create_app()`: Initialize FastAPI application with CORS and routes
- `chat_endpoint(request: ChatRequest)`: Handle incoming chat requests
- `health_check()`: Provide health status endpoint

### 2. Agent Manager Component

**Responsibility**: Initialize and manage the Strands Agent lifecycle

**Interface**:
```python
class AgentManager:
    def __init__(self, aws_credentials: AWSCredentials):
        """Initialize agent with Bedrock model and custom tools"""
        
    async def process_message(
        self, 
        message: str, 
        session_id: str,
        user_id: str
    ) -> AgentResponse:
        """Process user message and return agent response"""
        
    def get_agent(self) -> Agent:
        """Return the configured agent instance"""
```

**Configuration**:
- Model: Bedrock Nova Pro with streaming enabled
- Temperature: 0.7 (balanced creativity and consistency)
- Max tokens: 2048
- System prompt: Defines chatbot personality and capabilities

### 3. Custom Tools Component

**Responsibility**: Provide agent with capabilities to interact with backend APIs

**Tools**:

```python
@tool
async def list_products(
    category: str = None,
    search_query: str = None,
    limit: int = 10
) -> dict:
    """
    List available products from the e-shop catalog.
    
    Args:
        category: Optional product category filter
        search_query: Optional search term
        limit: Maximum number of products to return
    """

@tool
async def add_to_cart(
    product_id: str,
    quantity: int = 1,
    tool_context: ToolContext = None
) -> dict:
    """
    Add a product to the user's shopping cart.
    
    Args:
        product_id: Unique identifier of the product
        quantity: Number of items to add
        tool_context: Context containing user_id from invocation state
    """

@tool
async def view_cart(tool_context: ToolContext) -> dict:
    """
    View the contents of the user's shopping cart.
    
    Args:
        tool_context: Context containing user_id from invocation state
    """

@tool
async def remove_from_cart(
    product_id: str,
    tool_context: ToolContext
) -> dict:
    """
    Remove a product from the user's shopping cart.
    
    Args:
        product_id: Unique identifier of the product
        tool_context: Context containing user_id from invocation state
    """

@tool
async def recommend_products(
    user_preferences: str = None,
    limit: int = 5
) -> dict:
    """
    Get product recommendations based on the e-shop catalog.
    
    Args:
        user_preferences: Optional description of user preferences
        limit: Maximum number of recommendations
    """
```

### 4. Backend API Client Component

**Responsibility**: Handle HTTP communication with e-commerce backend

**Interface**:
```python
class BackendAPIClient:
    def __init__(self, base_url: str, api_key: str = None):
        """Initialize HTTP client with backend configuration"""
        
    async def get_products(
        self, 
        category: str = None, 
        search: str = None,
        limit: int = 10
    ) -> List[Product]:
        """Fetch products from backend"""
        
    async def get_cart(self, user_id: str) -> Cart:
        """Fetch user's shopping cart"""
        
    async def add_cart_item(
        self, 
        user_id: str, 
        product_id: str, 
        quantity: int
    ) -> Cart:
        """Add item to cart"""
        
    async def remove_cart_item(
        self, 
        user_id: str, 
        product_id: str
    ) -> Cart:
        """Remove item from cart"""
        
    async def get_recommendations(
        self, 
        preferences: str = None,
        limit: int = 5
    ) -> List[Product]:
        """Get product recommendations"""
```

### 5. Configuration Component

**Responsibility**: Manage application configuration from environment variables

**Interface**:
```python
class Config:
    # AWS Credentials
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_SESSION_TOKEN: str = None
    AWS_REGION: str = "us-west-2"
    
    # Bedrock Configuration
    BEDROCK_MODEL_ID: str = "us.amazon.nova-pro-v1:0"
    BEDROCK_TEMPERATURE: float = 0.7
    BEDROCK_MAX_TOKENS: int = 2048
    
    # Server Configuration
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    
    # Backend API Configuration
    BACKEND_API_URL: str
    BACKEND_API_KEY: str = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
```

## Data Models

### Request/Response Models

```python
from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    """Incoming chat request from frontend"""
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    """Outgoing chat response to frontend"""
    response: str
    session_id: str
    status: str = "success"
    error: Optional[str] = None

class Product(BaseModel):
    """Product information from backend"""
    id: str
    name: str
    description: str
    price: float
    category: str
    in_stock: bool
    image_url: Optional[str] = None

class CartItem(BaseModel):
    """Item in shopping cart"""
    product_id: str
    product_name: str
    quantity: int
    price: float
    subtotal: float

class Cart(BaseModel):
    """Shopping cart contents"""
    user_id: str
    items: List[CartItem]
    total: float
    item_count: int

class AWSCredentials(BaseModel):
    """AWS authentication credentials"""
    access_key_id: str
    secret_access_key: str
    session_token: Optional[str] = None
    region: str = "us-west-2"
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Message processing returns responses
*For any* valid user message sent to the chatbot, the system should return a non-empty natural language response from Bedrock Nova Pro.
**Validates: Requirements 1.1**

### Property 2: HTTP endpoint accepts valid requests
*For any* properly formatted JSON payload containing a user message, the HTTP server should accept the POST request and return a 200 status code.
**Validates: Requirements 1.2**

### Property 3: Conversation context is maintained
*For any* sequence of related messages within a session, the agent's responses should demonstrate awareness of previous messages in the conversation.
**Validates: Requirements 1.3**

### Property 4: Responses are valid JSON
*For any* request that generates a response, the HTTP server should return valid JSON with appropriate status codes (200 for success, 4xx/5xx for errors).
**Validates: Requirements 1.5**

### Property 5: Credentials are read from environment
*For any* valid set of AWS credentials in environment variables, the Chatbot Service should successfully authenticate with Bedrock Nova Pro.
**Validates: Requirements 2.3**

### Property 6: Product listing tool is invoked
*For any* user request to list products, the Chatbot Service should invoke the list_products custom tool.
**Validates: Requirements 3.1**

### Property 7: Product data structure is complete
*For any* product returned by the list_products tool, the data should include name, price, description, and availability fields.
**Validates: Requirements 3.2**

### Property 8: Add to cart tool is invoked
*For any* user request to add a product to cart, the Chatbot Service should invoke the add_to_cart custom tool with the product identifier.
**Validates: Requirements 4.1**

### Property 9: Backend API is called for cart updates
*For any* add_to_cart tool invocation, the system should make an HTTP call to the Backend APIs to update the shopping cart.
**Validates: Requirements 4.2**

### Property 10: Cart addition is confirmed
*For any* successful product addition to cart, the agent's response should indicate that the action was completed successfully.
**Validates: Requirements 4.3**

### Property 11: View cart tool is invoked
*For any* user request to view their cart, the Chatbot Service should invoke the view_cart custom tool.
**Validates: Requirements 5.1**

### Property 12: Cart data structure is complete
*For any* cart returned by the view_cart tool, the data should include all items with quantities, prices, and total cost.
**Validates: Requirements 5.2**

### Property 13: Remove from cart tool is invoked
*For any* user request to remove a product from cart, the Chatbot Service should invoke the remove_from_cart custom tool with the product identifier.
**Validates: Requirements 6.1**

### Property 14: Backend API is called for cart removal
*For any* remove_from_cart tool invocation, the system should make an HTTP call to the Backend APIs to update the shopping cart.
**Validates: Requirements 6.2**

### Property 15: Cart removal is confirmed
*For any* successful product removal from cart, the agent's response should indicate that the action was completed successfully.
**Validates: Requirements 6.3**

### Property 16: Recommendation tool is invoked
*For any* user request for product recommendations, the Chatbot Service should invoke the recommend_products custom tool.
**Validates: Requirements 7.1**

### Property 17: Recommendations come from catalog
*For any* product recommendation returned, the product should exist in the e-shop product catalog from Backend APIs.
**Validates: Requirements 7.2**

### Property 18: Recommendation data is complete
*For any* product recommendation, the response should include product name, description, and reasoning for the recommendation.
**Validates: Requirements 7.3**

### Property 19: POST requests are accepted
*For any* valid POST request to the /chat endpoint, the HTTP server should accept and process the request.
**Validates: Requirements 8.2**

### Property 20: Request validation occurs
*For any* incoming request, the HTTP server should validate the JSON payload structure before processing.
**Validates: Requirements 8.3**

### Property 21: CORS headers are present
*For any* HTTP response, the server should include appropriate CORS headers for browser compatibility.
**Validates: Requirements 8.5**

### Property 22: Requests are logged
*For any* processed request, the system should create log entries for both the incoming message and generated response.
**Validates: Requirements 9.1**

### Property 23: Errors are logged with context
*For any* error that occurs, the system should log the error with sufficient context for debugging.
**Validates: Requirements 9.2**

### Property 24: Sensitive data is redacted
*For any* log entry, the system should not contain unredacted customer data or credentials.
**Validates: Requirements 9.3**

### Property 25: Tool executions are logged
*For any* custom tool invocation, the system should log the tool name and execution outcome.
**Validates: Requirements 9.5**

### Property 26: Tools use SDK decorators
*For any* custom tool implementation, the function should be decorated with the @tool decorator from Strands Agents SDK.
**Validates: Requirements 10.1**

### Property 27: Tools call backend APIs
*For any* custom tool invocation, the tool should make an HTTP call to the corresponding Backend APIs endpoint.
**Validates: Requirements 10.2**

### Property 28: Authentication headers are included
*For any* Backend API call that requires authentication, the request should include necessary authentication headers.
**Validates: Requirements 10.3**

### Property 29: Tools return structured data
*For any* API response received by a custom tool, the tool should parse and return structured data to the agent.
**Validates: Requirements 10.4**

## Error Handling

### Error Categories

1. **Authentication Errors**
   - Missing or invalid AWS credentials
   - Bedrock service unavailable
   - Invalid API keys for backend services
   - **Handling**: Log error, return 503 Service Unavailable, include retry guidance

2. **Validation Errors**
   - Malformed JSON requests
   - Missing required fields
   - Invalid data types
   - **Handling**: Return 400 Bad Request with specific validation errors

3. **Backend API Errors**
   - Product not found
   - Cart operation failures
   - Network timeouts
   - **Handling**: Log error, inform user gracefully, suggest alternatives

4. **Agent Errors**
   - Tool execution failures
   - LLM response errors
   - Context overflow
   - **Handling**: Log error, return fallback response, maintain conversation state

5. **System Errors**
   - Out of memory
   - Unexpected exceptions
   - **Handling**: Log full stack trace, return 500 Internal Server Error

### Error Response Format

```python
{
    "status": "error",
    "error": "Human-readable error message",
    "error_code": "ERROR_CODE",
    "session_id": "session-123",
    "timestamp": "2025-11-26T10:30:00Z"
}
```

### Retry Strategy

- **Transient Errors**: Implement exponential backoff for backend API calls
- **Rate Limiting**: Respect Bedrock throttling with appropriate delays
- **Circuit Breaker**: Disable failing backend endpoints temporarily after repeated failures

### Logging Strategy

All errors should be logged with:
- Timestamp
- Error type and message
- Stack trace (for system errors)
- Request context (session_id, user_id)
- Redacted request/response data

## Testing Strategy

### Unit Testing

**Framework**: pytest with pytest-asyncio

**Coverage Areas**:
1. **Configuration Loading**
   - Test environment variable parsing
   - Test default value handling
   - Test validation of required fields

2. **HTTP Endpoints**
   - Test request validation
   - Test response formatting
   - Test CORS header inclusion
   - Test error responses

3. **Custom Tools**
   - Test tool decorator application
   - Test parameter extraction
   - Test backend API calls (mocked)
   - Test error handling

4. **Backend API Client**
   - Test HTTP request formatting
   - Test response parsing
   - Test authentication header inclusion
   - Test timeout handling

5. **Agent Manager**
   - Test agent initialization
   - Test message processing
   - Test session management

**Example Unit Test**:
```python
@pytest.mark.asyncio
async def test_list_products_tool_calls_backend():
    """Test that list_products tool calls backend API"""
    # Arrange
    mock_client = Mock(spec=BackendAPIClient)
    mock_client.get_products.return_value = [
        Product(id="1", name="Test", price=10.0, ...)
    ]
    
    # Act
    result = await list_products()
    
    # Assert
    mock_client.get_products.assert_called_once()
    assert len(result["products"]) > 0
```

### Property-Based Testing

**Framework**: Hypothesis

**Configuration**: Each property test should run a minimum of 100 iterations to ensure comprehensive coverage of the input space.

**Property Tests**:

Each property-based test must be tagged with a comment explicitly referencing the correctness property from the design document using this format: `**Feature: shopping-assistant-chatbot, Property {number}: {property_text}**`

1. **Property 1: Message processing returns responses**
   - Generate random valid user messages
   - Verify all messages receive non-empty responses
   - **Feature: shopping-assistant-chatbot, Property 1: Message processing returns responses**

2. **Property 2: HTTP endpoint accepts valid requests**
   - Generate random valid JSON payloads
   - Verify all receive 200 status codes
   - **Feature: shopping-assistant-chatbot, Property 2: HTTP endpoint accepts valid requests**

3. **Property 7: Product data structure is complete**
   - Generate random product data
   - Verify all products have required fields
   - **Feature: shopping-assistant-chatbot, Property 7: Product data structure is complete**

4. **Property 12: Cart data structure is complete**
   - Generate random cart data
   - Verify all carts have required fields
   - **Feature: shopping-assistant-chatbot, Property 12: Cart data structure is complete**

5. **Property 24: Sensitive data is redacted**
   - Generate random log entries with sensitive data
   - Verify credentials and PII are redacted
   - **Feature: shopping-assistant-chatbot, Property 24: Sensitive data is redacted**

**Example Property Test**:
```python
from hypothesis import given, strategies as st

@given(
    message=st.text(min_size=1, max_size=2000),
    session_id=st.uuids().map(str)
)
@pytest.mark.asyncio
async def test_property_message_processing_returns_responses(
    message: str, 
    session_id: str
):
    """
    **Feature: shopping-assistant-chatbot, Property 1: Message processing returns responses**
    
    For any valid user message, the system should return a non-empty response.
    """
    # Arrange
    agent_manager = AgentManager(test_credentials)
    
    # Act
    response = await agent_manager.process_message(message, session_id, "test-user")
    
    # Assert
    assert response.response is not None
    assert len(response.response) > 0
    assert response.status == "success"
```

### Integration Testing

**Scope**: Test end-to-end flows with mocked backend APIs

**Test Scenarios**:
1. Complete shopping flow: list products → add to cart → view cart → checkout
2. Error recovery: backend failure → retry → success
3. Session management: multiple messages in same session
4. Concurrent requests: multiple users simultaneously

### Manual Testing

**Test Cases**:
1. Frontend integration with popup component
2. Conversation quality and naturalness
3. Recommendation relevance
4. Error message clarity

## Implementation Notes

### Dependencies

```
strands-agents>=1.0.0
fastapi>=0.104.0
uvicorn>=0.24.0
boto3>=1.34.0
httpx>=0.25.0
pydantic>=2.5.0
python-dotenv>=1.0.0
pytest>=7.4.0
pytest-asyncio>=0.21.0
hypothesis>=6.92.0
```

### Project Structure

```
shopping-assistant-chatbot/
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── agent_manager.py        # Agent initialization and management
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── product_tools.py    # Product listing and search tools
│   │   ├── cart_tools.py       # Shopping cart tools
│   │   └── recommendation_tools.py  # Recommendation tools
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py           # HTTP endpoints
│   │   └── models.py           # Request/response models
│   ├── backend/
│   │   ├── __init__.py
│   │   └── client.py           # Backend API client
│   └── utils/
│       ├── __init__.py
│       ├── logging.py          # Logging configuration
│       └── security.py         # Security utilities (redaction)
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_tools.py
│   │   ├── test_api.py
│   │   └── test_backend_client.py
│   ├── property/
│   │   ├── test_properties.py
│   │   └── test_data_structures.py
│   └── integration/
│       └── test_flows.py
├── .env.example                # Example environment variables
├── requirements.txt            # Python dependencies
├── README.md                   # Setup and usage instructions
└── Dockerfile                  # Container configuration
```

### Security Considerations

1. **Credential Management**
   - Never log AWS credentials
   - Use environment variables exclusively
   - Rotate credentials regularly

2. **Input Validation**
   - Validate all user inputs
   - Sanitize messages before logging
   - Limit message length to prevent abuse

3. **Rate Limiting**
   - Implement per-user rate limits
   - Protect against DDoS attacks
   - Monitor for unusual patterns

4. **Data Privacy**
   - Redact PII from logs
   - Don't store conversation history without consent
   - Comply with data retention policies

### Performance Considerations

1. **Async Operations**
   - Use async/await for all I/O operations
   - Leverage FastAPI's async capabilities
   - Implement connection pooling for backend APIs

2. **Caching**
   - Cache product catalog data (5-minute TTL)
   - Cache user sessions in memory
   - Use Bedrock prompt caching for system prompts

3. **Resource Limits**
   - Set max concurrent requests
   - Implement request timeouts
   - Monitor memory usage

### Monitoring and Observability

1. **Metrics to Track**
   - Request rate and latency
   - Error rates by type
   - Tool invocation frequency
   - Bedrock token usage
   - Backend API response times

2. **Logging Levels**
   - DEBUG: Detailed tool execution
   - INFO: Request/response summaries
   - WARNING: Recoverable errors
   - ERROR: System failures

3. **Health Checks**
   - `/health`: Basic liveness check
   - `/health/ready`: Readiness check (includes Bedrock connectivity)
   - `/metrics`: Prometheus-compatible metrics endpoint
