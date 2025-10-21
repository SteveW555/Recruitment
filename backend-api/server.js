import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import Groq from 'groq-sdk';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

// Load environment variables
dotenv.config({ path: '../.env' });

// Get directory paths
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Initialize Express app
const app = express();
const PORT = process.env.BACKEND_PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Initialize GROQ client
const groq = new Groq({
  apiKey: process.env.GROQ_API_KEY
});

// Load system prompt
let SYSTEM_PROMPT = '';
try {
  SYSTEM_PROMPT = readFileSync(
    join(__dirname, '../prompts/candidates_nl2sql_system_prompt.txt'),
    'utf-8'
  );
  console.log('✓ System prompt loaded successfully');
} catch (error) {
  console.error('✗ Failed to load system prompt:', error.message);
  process.exit(1);
}

// Store conversation history per session (in-memory for now)
const conversations = new Map();

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'Elephant AI Backend',
    groq: !!process.env.GROQ_API_KEY,
    timestamp: new Date().toISOString()
  });
});

// Chat endpoint
app.post('/api/chat', async (req, res) => {
  try {
    const { message, sessionId = 'default', useHistory = true } = req.body;

    if (!message || !message.trim()) {
      return res.status(400).json({
        error: 'Message is required'
      });
    }

    console.log(`[${new Date().toISOString()}] Chat request:`, {
      sessionId,
      message: message.substring(0, 100),
      useHistory
    });

    // Get or create conversation history
    if (!conversations.has(sessionId)) {
      conversations.set(sessionId, []);
    }
    const history = conversations.get(sessionId);

    // Build messages array for GROQ
    const messages = [
      {
        role: 'system',
        content: SYSTEM_PROMPT
      }
    ];

    // Add conversation history if enabled
    if (useHistory && history.length > 0) {
      messages.push(...history);
    }

    // Add current user message
    messages.push({
      role: 'user',
      content: message
    });

    // Call GROQ API
    const startTime = Date.now();
    const completion = await groq.chat.completions.create({
      model: 'llama-3.3-70b-versatile',
      messages: messages,
      temperature: 0.3, // Low temperature for consistent SQL generation
      max_tokens: 2000,
      top_p: 0.9
    });

    const responseTime = Date.now() - startTime;
    const assistantMessage = completion.choices[0].message.content;

    // Update conversation history
    if (useHistory) {
      history.push({
        role: 'user',
        content: message
      });
      history.push({
        role: 'assistant',
        content: assistantMessage
      });

      // Keep only last 10 exchanges (20 messages) to manage memory
      if (history.length > 20) {
        history.splice(0, history.length - 20);
      }
    }

    console.log(`[${new Date().toISOString()}] Response generated in ${responseTime}ms`);

    // Return response
    res.json({
      success: true,
      message: assistantMessage,
      metadata: {
        model: completion.model,
        tokens: {
          prompt: completion.usage.prompt_tokens,
          completion: completion.usage.completion_tokens,
          total: completion.usage.total_tokens
        },
        responseTime,
        sessionId,
        historyLength: history.length
      }
    });

  } catch (error) {
    console.error('Chat endpoint error:', error);

    res.status(500).json({
      success: false,
      error: 'Failed to process chat request',
      details: error.message
    });
  }
});

// Clear conversation history
app.post('/api/chat/clear', (req, res) => {
  const { sessionId = 'default' } = req.body;

  if (conversations.has(sessionId)) {
    conversations.delete(sessionId);
    console.log(`Cleared conversation history for session: ${sessionId}`);
  }

  res.json({
    success: true,
    message: 'Conversation history cleared',
    sessionId
  });
});

// Get conversation statistics
app.get('/api/chat/stats', (req, res) => {
  const stats = {
    totalSessions: conversations.size,
    sessions: Array.from(conversations.entries()).map(([id, history]) => ({
      sessionId: id,
      messageCount: history.length,
      lastActivity: new Date().toISOString() // Would track this in production
    }))
  };

  res.json(stats);
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err);
  res.status(500).json({
    success: false,
    error: 'Internal server error',
    details: err.message
  });
});

// Start server
app.listen(PORT, () => {
  console.log('');
  console.log('╔════════════════════════════════════════════════════════╗');
  console.log('║                                                        ║');
  console.log('║        🐘 ELEPHANT AI BACKEND SERVER RUNNING 🐘        ║');
  console.log('║                                                        ║');
  console.log('╚════════════════════════════════════════════════════════╝');
  console.log('');
  console.log(`  ✓ Server:      http://localhost:${PORT}`);
  console.log(`  ✓ Health:      http://localhost:${PORT}/health`);
  console.log(`  ✓ Chat API:    POST http://localhost:${PORT}/api/chat`);
  console.log(`  ✓ GROQ Model:  llama-3.3-70b-versatile`);
  console.log(`  ✓ System Prompt: NL2SQL for candidates database`);
  console.log('');
  console.log('  Ready to process queries! 🚀');
  console.log('');
});
