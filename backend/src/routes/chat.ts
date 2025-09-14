import express from 'express';
import { Cerebras } from '@cerebras/cerebras_cloud_sdk';
import fs from 'fs';
import path from 'path';

const router = express.Router();

// Initialize Cerebras client lazily to avoid startup errors
let cerebras: Cerebras | null = null;

function getCerebrasClient(): Cerebras {
  if (!cerebras) {
    if (!process.env.CEREBRAS_API_KEY) {
      throw new Error('CEREBRAS_API_KEY environment variable is required');
    }
    cerebras = new Cerebras({
      apiKey: process.env.CEREBRAS_API_KEY,
    });
  }
  return cerebras;
}

// Interface definitions for OpenAI-compatible API
interface OpenAIMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

interface OpenAIRequest {
  model: string;
  messages: OpenAIMessage[];
  temperature?: number;
  max_tokens?: number;
  stream?: boolean;
}

interface OpenAIResponse {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: Array<{
    index: number;
    message: {
      role: string;
      content: string;
    };
    finish_reason: string;
  }>;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

// Load context from .md file
function loadContextFile(): string {
  try {
    const contextPath = path.join(__dirname, '..', 'context', 'system_context.md');
    if (fs.existsSync(contextPath)) {
      return fs.readFileSync(contextPath, 'utf-8');
    }
    console.warn('Context file not found, using empty context');
    return '';
  } catch (error) {
    console.error('Error loading context file:', error);
    return '';
  }
}

// Transform OpenAI request to Cerebras format with context injection
function transformToCerebrasRequest(openAIRequest: OpenAIRequest, context: string) {
  const messages = [...openAIRequest.messages];
  
  // Inject context as system message if we have context
  if (context) {
    // Check if there's already a system message
    const hasSystemMessage = messages.some(msg => msg.role === 'system');
    
    if (hasSystemMessage) {
      // Append context to existing system message
      const systemMessageIndex = messages.findIndex(msg => msg.role === 'system');
      messages[systemMessageIndex].content += '\n\n' + context;
    } else {
      // Add new system message with context
      messages.unshift({
        role: 'system',
        content: context
      });
    }
  }

  // Transform messages to Cerebras format
  const cerebrasMessages = messages.map(msg => ({
    role: msg.role,
    content: msg.content
  }));

  return {
    model: 'llama3.1-8b', // Default Cerebras model
    messages: cerebrasMessages,
    temperature: openAIRequest.temperature || 0.7,
    max_tokens: openAIRequest.max_tokens || 1000,
    stream: false as const // Explicitly type as const false
  };
}

// Transform Cerebras response to OpenAI format
function transformToOpenAIResponse(cerebrasResponse: any, requestId: string): OpenAIResponse {
  return {
    id: requestId,
    object: 'chat.completion',
    created: Math.floor(Date.now() / 1000),
    model: cerebrasResponse.model || 'llama3.1-8b',
    choices: [
      {
        index: 0,
        message: {
          role: 'assistant',
          content: cerebrasResponse.choices[0]?.message?.content || ''
        },
        finish_reason: cerebrasResponse.choices[0]?.finish_reason || 'stop'
      }
    ],
    usage: {
      prompt_tokens: cerebrasResponse.usage?.prompt_tokens || 0,
      completion_tokens: cerebrasResponse.usage?.completion_tokens || 0,
      total_tokens: cerebrasResponse.usage?.total_tokens || 0
    }
  };
}

// Generate unique request ID
function generateRequestId(): string {
  return `chatcmpl-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

// POST /api/chat/completions - OpenAI-compatible endpoint
router.post('/completions', async (req, res) => {
  try {
    const openAIRequest: OpenAIRequest = req.body;
    
    // Validate request
    if (!openAIRequest.messages || !Array.isArray(openAIRequest.messages)) {
      return res.status(400).json({
        error: {
          message: 'Invalid request: messages field is required and must be an array',
          type: 'invalid_request_error'
        }
      });
    }

    // Load context file
    const context = loadContextFile();
    
    // Transform request for Cerebras
    const cerebrasRequest = transformToCerebrasRequest(openAIRequest, context);
    
    // Generate request ID
    const requestId = generateRequestId();
    
    console.log(`[${requestId}] Processing chat completion request`);
    console.log(`[${requestId}] Context loaded: ${context.length} characters`);
    console.log(`[${requestId}] Messages: ${cerebrasRequest.messages.length}`);
    
    // Get Cerebras client and call API
    const cerebrasClient = getCerebrasClient();
    const cerebrasResponse = await cerebrasClient.chat.completions.create(cerebrasRequest);
    
    // Transform response to OpenAI format
    const openAIResponse = transformToOpenAIResponse(cerebrasResponse, requestId);
    
    console.log(`[${requestId}] Request completed successfully`);
    
    res.json(openAIResponse);
    
  } catch (error: any) {
    console.error('Error in chat completions:', error);
    
    // Handle different types of errors
    if (error.status) {
      // Cerebras API error
      return res.status(error.status).json({
        error: {
          message: error.message || 'Cerebras API error',
          type: 'api_error',
          code: error.code
        }
      });
    }
    
    // General server error
    res.status(500).json({
      error: {
        message: 'Internal server error',
        type: 'server_error'
      }
    });
  }
});

// GET /api/chat/models - List available models (OpenAI-compatible)
router.get('/models', (req, res) => {
  res.json({
    object: 'list',
    data: [
      {
        id: 'llama3.1-8b',
        object: 'model',
        created: 1677610602,
        owned_by: 'cerebras'
      },
      {
        id: 'llama3.1-70b',
        object: 'model',
        created: 1677610602,
        owned_by: 'cerebras'
      }
    ]
  });
});

export default router;
