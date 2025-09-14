# EvoSec Chat API

## Overview
This API provides OpenAI-compatible chat completions powered by Cerebras LLM with integrated EvoSec context. Terminal-based CLI tools can use this endpoint exactly like they would use OpenAI's API.

## Endpoints

### POST /api/chat/completions
OpenAI-compatible chat completions endpoint.

**Request Format:**
```json
{
  "model": "llama3.1-8b",
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant."
    },
    {
      "role": "user", 
      "content": "Hello, how can you help me with cybersecurity?"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 1000
}
```

**Response Format:**
```json
{
  "id": "chatcmpl-1234567890-abc123",
  "object": "chat.completion",
  "created": 1677610602,
  "model": "llama3.1-8b",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "I can help you with various cybersecurity aspects including..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 50,
    "completion_tokens": 100,
    "total_tokens": 150
  }
}
```

### GET /api/chat/models
Lists available models.

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "llama3.1-8b",
      "object": "model",
      "created": 1677610602,
      "owned_by": "cerebras"
    },
    {
      "id": "llama3.1-70b", 
      "object": "model",
      "created": 1677610602,
      "owned_by": "cerebras"
    }
  ]
}
```

## Context Injection
The API automatically injects EvoSec context from `/backend/src/context/system_context.md` into every request. This provides the LLM with:

- EvoSec platform capabilities
- Subscription plan information  
- Technical architecture details
- Security features overview
- API capabilities

## Configuration

### Environment Variables
Add to your `/backend/.env` file:
```bash
CEREBRAS_API_KEY=your-cerebras-api-key-here
```

### Getting Cerebras API Key
1. Sign up at [Cerebras Cloud](https://cloud.cerebras.ai/)
2. Navigate to API Keys section
3. Generate a new API key
4. Add it to your environment variables

## CLI Integration Example

### Using curl:
```bash
curl -X POST http://localhost:3001/api/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.1-8b",
    "messages": [
      {
        "role": "user",
        "content": "What cybersecurity features does EvoSec offer?"
      }
    ],
    "temperature": 0.7,
    "max_tokens": 500
  }'
```

### Using Python OpenAI client:
```python
import openai

# Point to your local EvoSec endpoint
openai.api_base = "http://localhost:3001/api/chat"
openai.api_key = "not-needed" # Not used by our endpoint

response = openai.ChatCompletion.create(
    model="llama3.1-8b",
    messages=[
        {"role": "user", "content": "Tell me about EvoSec's enterprise features"}
    ]
)

print(response.choices[0].message.content)
```

### Using Node.js OpenAI client:
```javascript
import OpenAI from 'openai';

const openai = new OpenAI({
  baseURL: 'http://localhost:3001/api/chat',
  apiKey: 'not-needed' // Not used by our endpoint
});

const response = await openai.chat.completions.create({
  model: 'llama3.1-8b',
  messages: [
    { role: 'user', content: 'How does EvoSec handle threat detection?' }
  ]
});

console.log(response.choices[0].message.content);
```

## Error Handling

### 400 Bad Request
```json
{
  "error": {
    "message": "Invalid request: messages field is required and must be an array",
    "type": "invalid_request_error"
  }
}
```

### 500 Internal Server Error
```json
{
  "error": {
    "message": "Internal server error", 
    "type": "server_error"
  }
}
```

### Cerebras API Errors
```json
{
  "error": {
    "message": "Cerebras API error message",
    "type": "api_error",
    "code": "specific_error_code"
  }
}
```

## Context File Management

### Updating Context
Edit `/backend/src/context/system_context.md` to modify the context that gets injected into all requests. Changes take effect immediately on the next request.

### Context Structure
The context file should include:
- Company/product information
- Feature descriptions  
- Technical specifications
- Support information
- Any domain-specific knowledge

## Available Models

| Model | Description |
|-------|-------------|
| llama3.1-8b | Faster responses, good for general queries |
| llama3.1-70b | More capable, better for complex tasks |

## Rate Limiting
No rate limiting is currently implemented. For production use, consider adding rate limiting middleware.

## Security Notes
- No authentication is required for the chat endpoint
- For production, consider adding API key authentication
- The Cerebras API key should be kept secure
- Context files may contain sensitive information

## Debugging
Request IDs are generated for each request and logged to help with debugging:
```
[chatcmpl-1234567890-abc123] Processing chat completion request
[chatcmpl-1234567890-abc123] Context loaded: 1250 characters  
[chatcmpl-1234567890-abc123] Messages: 2
[chatcmpl-1234567890-abc123] Request completed successfully
```
