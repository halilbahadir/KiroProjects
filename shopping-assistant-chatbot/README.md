# Shopping Assistant Chatbot Service

A conversational AI chatbot service for e-commerce platforms, powered by Amazon Bedrock Nova Pro and the Strands Agents SDK.

## Overview

The Shopping Assistant Chatbot Service provides natural language interaction capabilities for customers to:
- Browse and search products
- Manage shopping cart (add, view, remove items)
- Receive personalized product recommendations
- Get assistance with shopping decisions

## Features

- **Natural Language Processing**: Powered by Amazon Bedrock Nova Pro
- **Custom Tools**: Integrated with backend e-commerce APIs
- **RESTful API**: FastAPI-based HTTP server for frontend integration
- **Async Operations**: High-performance async/await architecture
- **Comprehensive Logging**: Structured logging with sensitive data redaction
- **Property-Based Testing**: Hypothesis-powered correctness validation

## Prerequisites

- Python 3.11 or higher
- AWS Account with Bedrock access
- AWS credentials with permissions for Bedrock Nova Pro
- Backend e-commerce API (running locally or remotely)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd shopping-assistant-chatbot
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` and provide your AWS credentials and configuration:

```env
# AWS Credentials (Required)
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-west-2

# Backend API Configuration (Required)
BACKEND_API_URL=http://localhost:3001

# Optional: Customize other settings as needed
```

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `AWS_ACCESS_KEY_ID` | AWS access key for Bedrock authentication | Yes | - |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key for Bedrock authentication | Yes | - |
| `AWS_SESSION_TOKEN` | AWS session token (for temporary credentials) | No | - |
| `AWS_REGION` | AWS region for Bedrock service | No | `us-west-2` |
| `BEDROCK_MODEL_ID` | Bedrock model identifier | No | `us.amazon.nova-pro-v1:0` |
| `BEDROCK_TEMPERATURE` | Model temperature (0.0-1.0) | No | `0.7` |
| `BEDROCK_MAX_TOKENS` | Maximum tokens in response | No | `2048` |
| `SERVER_HOST` | HTTP server host | No | `0.0.0.0` |
| `SERVER_PORT` | HTTP server port | No | `8000` |
| `BACKEND_API_URL` | E-commerce backend API base URL | Yes | - |
| `BACKEND_API_KEY` | Backend API authentication key | No | - |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | No | `INFO` |

## Running the Service

### Development Mode

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Docker

#### Build the Docker Image

```bash
docker build -t shopping-assistant-chatbot:latest .
```

#### Run with Docker

```bash
docker run -p 8000:8000 --env-file .env shopping-assistant-chatbot:latest
```

#### Using Docker Compose

For easier management with docker-compose:

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

#### Docker Environment Variables

When running with Docker, ensure your `.env` file contains all required variables, or pass them directly:

```bash
docker run -p 8000:8000 \
  -e AWS_ACCESS_KEY_ID=your_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret \
  -e AWS_REGION=us-west-2 \
  -e BACKEND_API_URL=http://host.docker.internal:3001 \
  shopping-assistant-chatbot:latest
```

**Note**: Use `host.docker.internal` instead of `localhost` when the backend API runs on your host machine.

## API Documentation

Once the service is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

### Base URL

All API endpoints are prefixed with `/api/v1`:
- Local: `http://localhost:8000/api/v1`
- Docker: `http://localhost:8000/api/v1`

### Endpoints

#### POST /api/v1/chat

Send a message to the chatbot and receive a response.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me available laptops",
    "session_id": "session-123",
    "user_id": "user-456"
  }'
```

**Request Body:**
```json
{
  "message": "Show me available laptops",
  "session_id": "session-123",
  "user_id": "user-456"
}
```

**Fields:**
- `message` (required, string, 1-2000 chars): User's message to the chatbot
- `session_id` (optional, string): Session identifier for conversation continuity
- `user_id` (optional, string): User identifier for personalized responses

**Success Response (200 OK):**
```json
{
  "response": "I found 5 laptops in our catalog. Here are some options:\n\n1. **Dell XPS 13** - $999.99\n   - 13.3\" display, Intel i7, 16GB RAM\n   - In stock\n\n2. **MacBook Air M2** - $1,199.00\n   - 13.6\" Retina display, Apple M2 chip\n   - In stock\n\nWould you like more details about any of these?",
  "session_id": "session-123",
  "status": "success"
}
```

**Error Response (400 Bad Request):**
```json
{
  "response": "Invalid request format",
  "session_id": "",
  "status": "error",
  "error": "Message cannot be empty or only whitespace"
}
```

**Error Response (503 Service Unavailable):**
```json
{
  "response": "Service temporarily unavailable",
  "session_id": "",
  "status": "error",
  "error": "Bedrock service unavailable"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "response": "An internal error occurred",
  "session_id": "",
  "status": "error",
  "error": "System error occurred"
}
```

#### GET /api/v1/health

Check service health status.

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/health"
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "shopping-assistant-chatbot"
}
```

#### GET /api/v1/health/ready

Check service readiness (verifies agent manager is initialized).

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/health/ready"
```

**Response (200 OK):**
```json
{
  "status": "ready",
  "service": "shopping-assistant-chatbot",
  "agent_initialized": true
}
```

**Response (503 Service Unavailable):**
```json
{
  "detail": "Service not ready - agent manager not initialized"
}
```

#### GET /

Root endpoint providing service information.

**Request:**
```bash
curl -X GET "http://localhost:8000/"
```

**Response (200 OK):**
```json
{
  "service": "Shopping Assistant Chatbot",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs",
  "health": "/api/v1/health"
}
```

### Example Conversations

#### Product Search
```json
// Request
{
  "message": "I'm looking for a laptop under $1000",
  "session_id": "session-abc",
  "user_id": "user-123"
}

// Response
{
  "response": "I can help you find laptops under $1000! Let me search our catalog...\n\nI found 3 laptops in your price range:\n\n1. **Acer Aspire 5** - $649.99\n2. **HP Pavilion 15** - $799.99\n3. **Lenovo IdeaPad 3** - $899.99\n\nWould you like more details about any of these?",
  "session_id": "session-abc",
  "status": "success"
}
```

#### Add to Cart
```json
// Request
{
  "message": "Add the HP Pavilion 15 to my cart",
  "session_id": "session-abc",
  "user_id": "user-123"
}

// Response
{
  "response": "Great choice! I've added the HP Pavilion 15 ($799.99) to your cart. Your cart now has 1 item with a total of $799.99.\n\nWould you like to continue shopping or proceed to checkout?",
  "session_id": "session-abc",
  "status": "success"
}
```

#### View Cart
```json
// Request
{
  "message": "What's in my cart?",
  "session_id": "session-abc",
  "user_id": "user-123"
}

// Response
{
  "response": "Here's what's in your cart:\n\n1. HP Pavilion 15 - Quantity: 1 - $799.99\n\n**Total: $799.99** (1 item)\n\nWould you like to modify your cart or proceed to checkout?",
  "session_id": "session-abc",
  "status": "success"
}
```

#### Product Recommendations
```json
// Request
{
  "message": "Can you recommend some accessories for my laptop?",
  "session_id": "session-abc",
  "user_id": "user-123"
}

// Response
{
  "response": "Based on your HP Pavilion 15, here are some great accessories:\n\n1. **Logitech MX Master 3 Mouse** - $99.99\n   - Ergonomic design, perfect for productivity\n\n2. **USB-C Hub 7-in-1** - $39.99\n   - Expand your connectivity options\n\n3. **Laptop Sleeve 15.6\"** - $24.99\n   - Protect your investment\n\nWould you like to add any of these to your cart?",
  "session_id": "session-abc",
  "status": "success"
}
```

### Chatbot Capabilities

The chatbot can help customers with the following tasks:

**Product Discovery:**
- List all available products
- Search products by name, category, or description
- Filter products by price range
- Get detailed product information

**Shopping Cart Management:**
- Add products to cart with specified quantities
- View current cart contents with prices and totals
- Remove products from cart
- Update product quantities in cart

**Product Recommendations:**
- Get personalized product recommendations
- Receive suggestions based on cart contents
- Discover complementary products (accessories, related items)

**Conversational Features:**
- Natural language understanding for shopping queries
- Context-aware responses across conversation
- Helpful error messages and guidance
- Multi-turn conversations with memory

### Request/Response Format Details

#### Request Validation

All requests are validated using Pydantic models. Invalid requests will return a 400 error with details:

**Validation Rules:**
- `message`: Required, 1-2000 characters, cannot be empty or only whitespace
- `session_id`: Optional string for conversation tracking
- `user_id`: Optional string for user identification

**Example Validation Error:**
```json
{
  "detail": "Request validation failed: Message cannot be empty or only whitespace"
}
```

#### Response Status Codes

| Status Code | Meaning | When It Occurs |
|-------------|---------|----------------|
| 200 OK | Success | Request processed successfully |
| 400 Bad Request | Client Error | Invalid request format or validation error |
| 500 Internal Server Error | Server Error | Unexpected system error |
| 503 Service Unavailable | Service Error | Bedrock unavailable or agent error |

#### Error Handling

The service implements comprehensive error handling:

1. **Validation Errors (400)**: Malformed requests, missing required fields
2. **Service Errors (503)**: Bedrock unavailable, backend API failures
3. **System Errors (500)**: Unexpected exceptions, configuration issues

All errors include:
- Human-readable error message
- Error status in response
- Detailed logging for debugging

### CORS Configuration

The service is configured with permissive CORS settings for development:

```python
allow_origins=["*"]  # All origins allowed
allow_credentials=True
allow_methods=["*"]  # All HTTP methods
allow_headers=["*"]  # All headers
```

**Production Recommendation**: Restrict `allow_origins` to your frontend domain(s):
```python
allow_origins=["https://yourdomain.com", "https://www.yourdomain.com"]
```

## Testing

The service includes comprehensive test coverage with three types of tests:

### Test Structure

```
tests/
├── unit/           # Unit tests for individual components
├── property/       # Property-based tests using Hypothesis
└── integration/    # End-to-end integration tests
```

### Run All Tests

```bash
pytest
```

### Run Unit Tests Only

```bash
pytest tests/unit/ -v
```

### Run Property-Based Tests

Property-based tests use Hypothesis to verify correctness properties across many inputs:

```bash
pytest tests/property/ -v
```

### Run Integration Tests

```bash
pytest tests/integration/ -v
```

### Run with Coverage

```bash
# Generate coverage report
pytest --cov=src --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Run Specific Test File

```bash
pytest tests/unit/test_config.py -v
```

### Run Tests with Detailed Output

```bash
pytest -vv --tb=short
```

### Testing Best Practices

1. **Mock External Services**: Tests mock Bedrock and backend API calls
2. **Property-Based Testing**: Validates correctness across random inputs
3. **Async Testing**: Uses pytest-asyncio for async function testing
4. **Fixtures**: Reusable test fixtures for common setup
5. **Coverage Goals**: Aim for >80% code coverage

## Project Structure

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
│   ├── unit/                   # Unit tests
│   ├── property/               # Property-based tests
│   └── integration/            # Integration tests
├── .env.example                # Example environment variables
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── Dockerfile                  # Container configuration
```

## Development

### Adding New Tools

1. Create a new tool file in `src/tools/`
2. Use the `@tool` decorator from Strands Agents SDK
3. Implement async functions that call backend APIs
4. Register the tool in `agent_manager.py`

### Adding New API Endpoints

1. Define routes in `src/api/routes.py`
2. Create request/response models in `src/api/models.py`
3. Add appropriate error handling and logging

### Logging

The service uses structured logging with automatic redaction of sensitive data:

```python
from src.utils.logging import logger

logger.info("Processing request", extra={"session_id": session_id})
logger.error("Backend API failed", extra={"error": str(e)})
```

## Troubleshooting

### Common Issues and Solutions

#### Installation Issues

**Issue**: `ModuleNotFoundError: No module named 'strands_agents'`

**Symptoms**: Import errors when starting the service

**Solutions**:
1. Ensure virtual environment is activated:
   ```bash
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate  # Windows
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Verify installation:
   ```bash
   pip list | grep strands-agents
   ```

**Issue**: `Python version incompatibility`

**Symptoms**: Syntax errors or import failures

**Solutions**:
1. Check Python version (requires 3.11+):
   ```bash
   python --version
   ```
2. Install correct Python version:
   ```bash
   # macOS with Homebrew
   brew install python@3.11
   
   # Ubuntu/Debian
   sudo apt-get install python3.11
   ```

#### AWS and Bedrock Issues

**Issue**: `Authentication failed with Bedrock`

**Symptoms**: 503 errors, "Bedrock service unavailable" messages

**Solutions**:
1. Verify AWS credentials are set:
   ```bash
   echo $AWS_ACCESS_KEY_ID
   echo $AWS_SECRET_ACCESS_KEY
   ```
2. Check credentials have Bedrock permissions:
   ```bash
   aws bedrock list-foundation-models --region us-west-2
   ```
3. Verify region supports Bedrock:
   - Supported regions: us-east-1, us-west-2, eu-west-1, ap-southeast-1
4. Check IAM policy includes required permissions:
   - `bedrock:InvokeModel`
   - `bedrock:InvokeModelWithResponseStream`

**Issue**: `Model not found or access denied`

**Symptoms**: Errors mentioning model ID or access

**Solutions**:
1. Verify model ID is correct:
   ```bash
   # List available models
   aws bedrock list-foundation-models --region us-west-2
   ```
2. Request model access in AWS Console:
   - Go to Bedrock console → Model access
   - Request access to Nova Pro model
   - Wait for approval (usually instant)

**Issue**: `Rate limit exceeded`

**Symptoms**: 429 errors, throttling messages

**Solutions**:
1. Implement exponential backoff in client code
2. Request quota increase in AWS Service Quotas
3. Reduce request frequency
4. Consider using Nova Lite for higher throughput

#### Backend API Issues

**Issue**: `Connection refused to backend API`

**Symptoms**: 503 errors, "Backend API unavailable" messages

**Solutions**:
1. Verify backend API is running:
   ```bash
   curl http://localhost:3001/health
   ```
2. Check `BACKEND_API_URL` in `.env`:
   ```bash
   cat .env | grep BACKEND_API_URL
   ```
3. For Docker, use `host.docker.internal`:
   ```env
   BACKEND_API_URL=http://host.docker.internal:3001
   ```
4. Check firewall rules and network connectivity

**Issue**: `Backend API timeout`

**Symptoms**: Slow responses, timeout errors

**Solutions**:
1. Increase timeout in backend client configuration
2. Check backend API performance and logs
3. Verify network latency between services
4. Consider implementing caching

#### Configuration Issues

**Issue**: `Required environment variable missing`

**Symptoms**: Service fails to start with validation error

**Solutions**:
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Fill in all required variables:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `BACKEND_API_URL`
3. Verify `.env` file is in the correct location (project root)

**Issue**: `Invalid configuration value`

**Symptoms**: Validation errors on startup

**Solutions**:
1. Check value formats:
   - `BEDROCK_TEMPERATURE`: 0.0 to 1.0
   - `SERVER_PORT`: 1 to 65535
   - `BACKEND_API_URL`: Must start with http:// or https://
2. Remove quotes from values in `.env` file
3. Check for typos in variable names

#### Docker Issues

**Issue**: `Docker container exits immediately`

**Symptoms**: Container starts then stops

**Solutions**:
1. Check container logs:
   ```bash
   docker logs shopping-assistant-chatbot
   ```
2. Verify environment variables are passed:
   ```bash
   docker run --env-file .env shopping-assistant-chatbot:latest
   ```
3. Check for port conflicts:
   ```bash
   lsof -i :8000  # macOS/Linux
   netstat -ano | findstr :8000  # Windows
   ```

**Issue**: `Cannot connect to backend from Docker`

**Symptoms**: Backend API connection refused in Docker

**Solutions**:
1. Use `host.docker.internal` instead of `localhost`:
   ```env
   BACKEND_API_URL=http://host.docker.internal:3001
   ```
2. Or use Docker network:
   ```bash
   docker network create chatbot-network
   docker run --network chatbot-network ...
   ```

#### Runtime Issues

**Issue**: `Memory errors or OOM (Out of Memory)`

**Symptoms**: Service crashes, memory errors

**Solutions**:
1. Reduce `BEDROCK_MAX_TOKENS` to lower memory usage
2. Limit concurrent requests
3. Increase container/server memory allocation
4. Monitor memory usage:
   ```bash
   docker stats shopping-assistant-chatbot
   ```

**Issue**: `Slow response times`

**Symptoms**: High latency, timeouts

**Solutions**:
1. Check Bedrock region latency
2. Verify backend API performance
3. Enable debug logging to identify bottlenecks:
   ```bash
   export LOG_LEVEL=DEBUG
   ```
4. Monitor with performance profiling
5. Consider using Nova Lite for faster responses

### Debug Mode

Enable debug logging for detailed troubleshooting:

```bash
# Set environment variable
export LOG_LEVEL=DEBUG

# Run with debug logging
uvicorn src.main:app --reload --log-level debug

# Or in .env file
LOG_LEVEL=DEBUG
```

Debug logs include:
- Detailed request/response data
- Tool invocation details
- Backend API call traces
- Agent decision-making process
- Timing information for each step

### Getting Help

If you're still experiencing issues:

1. **Check Logs**: Review application logs for error details
   ```bash
   # Docker logs
   docker logs shopping-assistant-chatbot --tail 100
   
   # Local logs
   tail -f logs/chatbot.log
   ```

2. **Verify Configuration**: Double-check all environment variables
   ```bash
   # Print configuration (redacted)
   python -c "from src.config import get_config; print(get_config())"
   ```

3. **Test Components Individually**:
   ```bash
   # Test AWS credentials
   aws sts get-caller-identity
   
   # Test Bedrock access
   aws bedrock list-foundation-models --region us-west-2
   
   # Test backend API
   curl http://localhost:3001/api/products
   ```

4. **Create an Issue**: Include:
   - Error messages and stack traces
   - Configuration (with credentials redacted)
   - Steps to reproduce
   - Environment details (OS, Python version, Docker version)

## FAQ

### General Questions

**Q: What is the Shopping Assistant Chatbot?**

A: It's a conversational AI service that helps customers interact with an e-commerce platform through natural language. It can list products, manage shopping carts, and provide recommendations.

**Q: What AI model does it use?**

A: The service uses Amazon Bedrock Nova Pro, a large language model optimized for conversational AI and reasoning tasks.

**Q: Does it store conversation history?**

A: The service maintains conversation context within a session but doesn't persist conversations to a database. Session state is managed in memory by the Strands Agent framework.

**Q: Can I use a different AI model?**

A: Yes! You can change the `BEDROCK_MODEL_ID` environment variable to use other Bedrock models like Nova Lite or Nova Micro. You may need to adjust temperature and token settings.

### Technical Questions

**Q: How do I integrate this with my frontend?**

A: Make POST requests to `/api/v1/chat` with a JSON payload containing the user's message. See the API Documentation section for examples.

**Q: Can I deploy this to AWS Lambda?**

A: Yes, but you'll need to use the Mangum adapter to wrap the FastAPI application. See the Deployment section for details.

**Q: How do I scale this for production?**

A: Run multiple workers with uvicorn (`--workers 4`), use a load balancer, and consider deploying to ECS/Fargate or Kubernetes for auto-scaling.

**Q: What's the expected latency?**

A: Typical response times are 1-3 seconds, depending on:
- Bedrock model (Nova Lite is faster than Nova Pro)
- Backend API latency
- Network conditions
- Message complexity

**Q: How much does it cost to run?**

A: Costs depend on:
- Bedrock token usage (~$0.003 per 1K tokens for Nova Pro)
- AWS infrastructure (EC2, ECS, Lambda)
- Backend API costs
- Network data transfer

**Q: Can I use this without AWS?**

A: The service requires AWS Bedrock for the AI model. However, you could modify it to use other LLM providers (OpenAI, Anthropic, etc.) by replacing the Bedrock integration.

### Security Questions

**Q: Is my data secure?**

A: Yes. The service:
- Redacts sensitive data from logs
- Uses HTTPS for API communication (in production)
- Doesn't store conversation history
- Follows AWS security best practices

**Q: How do I protect my AWS credentials?**

A: 
- Never commit `.env` files to version control
- Use IAM roles when deploying to AWS
- Rotate credentials regularly
- Use AWS Secrets Manager for production
- Implement least-privilege IAM policies

**Q: Does it comply with GDPR/privacy regulations?**

A: The service doesn't store personal data, but you should:
- Implement proper consent mechanisms in your frontend
- Add data retention policies
- Provide privacy notices to users
- Ensure backend API compliance

### Development Questions

**Q: How do I add new chatbot capabilities?**

A: Create new tools in `src/tools/` using the `@tool` decorator. See the Development section for details.

**Q: Can I customize the chatbot's personality?**

A: Yes! Modify the system prompt in `src/agent_manager.py` to change the chatbot's tone, style, and behavior.

**Q: How do I test my changes?**

A: Run the test suite with `pytest`. Add new tests in the appropriate directory (unit, property, or integration).

**Q: Can I use this with a different e-commerce backend?**

A: Yes! Update the `BackendAPIClient` in `src/backend/client.py` to match your backend's API structure.

## Deployment

### Production Deployment Checklist

Before deploying to production, ensure you:

1. **Security**
   - [ ] Use IAM roles instead of access keys (when deploying to AWS)
   - [ ] Restrict CORS origins to your frontend domain(s)
   - [ ] Enable HTTPS/TLS for all connections
   - [ ] Set up AWS Secrets Manager for credential management
   - [ ] Configure security groups and network ACLs
   - [ ] Enable AWS CloudTrail for audit logging

2. **Configuration**
   - [ ] Set `LOG_LEVEL=INFO` or `WARNING` (not DEBUG)
   - [ ] Configure appropriate `BEDROCK_MAX_TOKENS` for your use case
   - [ ] Set up environment-specific `.env` files
   - [ ] Configure backend API URL for production environment
   - [ ] Set appropriate timeout values for API calls

3. **Monitoring**
   - [ ] Set up CloudWatch alarms for errors and latency
   - [ ] Configure log aggregation (CloudWatch Logs, ELK, etc.)
   - [ ] Monitor Bedrock token usage and costs
   - [ ] Set up health check monitoring
   - [ ] Configure alerting for service degradation

4. **Performance**
   - [ ] Run with multiple workers: `--workers 4`
   - [ ] Configure connection pooling for backend API
   - [ ] Enable Bedrock prompt caching
   - [ ] Set up load balancing for high availability
   - [ ] Configure auto-scaling based on traffic

5. **Reliability**
   - [ ] Implement retry logic with exponential backoff
   - [ ] Set up circuit breakers for backend API calls
   - [ ] Configure health checks for load balancers
   - [ ] Test failover scenarios
   - [ ] Document incident response procedures

### Deployment Options

#### AWS ECS/Fargate

```bash
# Build and push Docker image to ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-west-2.amazonaws.com
docker build -t shopping-assistant-chatbot:latest .
docker tag shopping-assistant-chatbot:latest <account-id>.dkr.ecr.us-west-2.amazonaws.com/shopping-assistant-chatbot:latest
docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/shopping-assistant-chatbot:latest

# Deploy to ECS using task definition
aws ecs update-service --cluster my-cluster --service chatbot-service --force-new-deployment
```

#### AWS Lambda (with Function URLs)

For serverless deployment, use AWS Lambda with Mangum adapter:

```python
# lambda_handler.py
from mangum import Mangum
from src.main import app

handler = Mangum(app)
```

#### Kubernetes

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: shopping-assistant-chatbot
spec:
  replicas: 3
  selector:
    matchLabels:
      app: chatbot
  template:
    metadata:
      labels:
        app: chatbot
    spec:
      containers:
      - name: chatbot
        image: shopping-assistant-chatbot:latest
        ports:
        - containerPort: 8000
        env:
        - name: AWS_ACCESS_KEY_ID
          valueFrom:
            secretKeyRef:
              name: aws-credentials
              key: access-key-id
        # ... other environment variables
```

### Environment-Specific Configuration

Create separate `.env` files for each environment:

```bash
.env.development  # Local development
.env.staging      # Staging environment
.env.production   # Production environment
```

Load the appropriate file based on environment:

```bash
# Development
cp .env.development .env

# Staging
cp .env.staging .env

# Production
cp .env.production .env
```

## Security

### Best Practices

1. **Credential Management**
   - Never commit `.env` files or AWS credentials to version control
   - Use AWS IAM roles when deploying to AWS infrastructure
   - Rotate credentials regularly (every 90 days minimum)
   - Use AWS Secrets Manager or Parameter Store for production
   - Implement least-privilege IAM policies

2. **Network Security**
   - Use HTTPS/TLS for all API communications
   - Implement rate limiting to prevent abuse
   - Configure Web Application Firewall (WAF) rules
   - Restrict CORS origins to known frontend domains
   - Use VPC endpoints for AWS service access

3. **Data Protection**
   - Sensitive data is automatically redacted from logs
   - Implement encryption at rest and in transit
   - Don't log customer PII or payment information
   - Comply with data retention policies
   - Regular security audits and penetration testing

4. **Monitoring & Alerting**
   - Monitor CloudWatch logs for suspicious activity
   - Set up alerts for authentication failures
   - Track unusual API usage patterns
   - Monitor for potential DDoS attacks
   - Regular review of access logs

### Required AWS IAM Permissions

Minimum IAM policy for the service:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "arn:aws:bedrock:*:*:model/us.amazon.nova-pro-v1:0"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:log-group:/aws/chatbot/*"
    }
  ]
}
```

## Performance

### Optimization Strategies

1. **Async Operations**
   - The service uses async/await for non-blocking I/O
   - All backend API calls are asynchronous
   - Concurrent request handling with FastAPI
   - Connection pooling for HTTP clients

2. **Caching**
   - Bedrock prompt caching reduces latency for repeated queries
   - Consider caching product catalog data (5-minute TTL)
   - Cache user sessions in memory or Redis
   - Implement CDN for static assets

3. **Scaling**
   - Horizontal scaling with multiple workers
   - Load balancing across multiple instances
   - Auto-scaling based on CPU/memory metrics
   - Consider serverless deployment for variable traffic

4. **Resource Limits**
   - Set max concurrent requests per worker
   - Implement request timeouts (30s default)
   - Monitor memory usage and set limits
   - Configure connection pool sizes

### Performance Metrics

Monitor these key metrics:

- **Latency**: P50, P95, P99 response times
- **Throughput**: Requests per second
- **Error Rate**: Percentage of failed requests
- **Bedrock Token Usage**: Tokens per request, cost per request
- **Backend API Latency**: Time spent waiting for backend
- **Memory Usage**: Per worker and total
- **CPU Usage**: Per worker and total

### Benchmarking

Test performance under load:

```bash
# Install Apache Bench
apt-get install apache2-utils  # Ubuntu/Debian
brew install httpd  # macOS

# Run load test
ab -n 1000 -c 10 -p request.json -T application/json http://localhost:8000/api/v1/chat

# Or use wrk for more advanced testing
wrk -t4 -c100 -d30s --latency http://localhost:8000/api/v1/health
```

## Contributing

1. Create a feature branch
2. Implement changes with tests
3. Ensure all tests pass: `pytest`
4. Submit a pull request with clear description

## License

[Your License Here]

## Support

For issues and questions:
- Create an issue in the repository
- Contact the development team
- Check the API documentation at `/docs`

## Changelog

### Version 1.0.0 (Initial Release)
- Natural language chat interface
- Product listing and search
- Shopping cart management
- Product recommendations
- Integration with backend e-commerce APIs
- Comprehensive logging and monitoring
- Property-based testing suite
