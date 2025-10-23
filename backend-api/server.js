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

// Load system prompts for different agents from separate files
let SYSTEM_PROMPTS = {};
const PROMPT_DIR = join(__dirname, 'prompts/agent-system-prompts');
const AGENT_TYPES = ['general-chat', 'information-retrieval', 'problem-solving', 'automation', 'report-generation', 'industry-knowledge'];

// Load each agent's system prompt from its own file
for (const agentType of AGENT_TYPES) {
  try {
    const promptPath = join(PROMPT_DIR, `${agentType}.txt`);
    SYSTEM_PROMPTS[agentType] = readFileSync(promptPath, 'utf-8');
    console.log(`✓ Loaded ${agentType} prompt`);
  } catch (error) {
    console.error(`✗ Failed to load ${agentType} prompt:`, error.message);
  }
}

let DEFAULT_SYSTEM_PROMPT = SYSTEM_PROMPTS['general-chat'] || 'You are a helpful AI assistant.';

try {
  // Try to load the NL2SQL prompt for data queries
  const nl2sqlPrompt = readFileSync(
    join(__dirname, '../prompts/candidates_nl2sql_system_prompt.txt'),
    'utf-8'
  );
  SYSTEM_PROMPTS['data-query'] = nl2sqlPrompt;
  console.log('✓ NL2SQL system prompt loaded successfully');
} catch (error) {
  console.log('ℹ NL2SQL prompt not found, using default');
}

console.log(`\n✓ System prompts loaded for ${Object.keys(SYSTEM_PROMPTS).length} agent types\n`);

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
    const { message, sessionId = 'default', useHistory = true, agent = 'auto' } = req.body;

    if (!message || !message.trim()) {
      return res.status(400).json({
        error: 'Message is required'
      });
    }

    console.log(`[${new Date().toISOString()}] Chat request:`, {
      sessionId,
      agent,
      message: message.substring(0, 100),
      useHistory
    });

    // Call Python AI Router
    const startTime = Date.now();
    const { spawn } = require('child_process');
    const path = require('path');

    const pythonPath = 'python'; // Use 'python3' on Linux/Mac if needed
    const routerPath = path.join(__dirname, '..', 'utils', 'ai_router', 'cli.py');

    // Convert agent type from frontend format to router format
    const agentMap = {
      'information-retrieval': 'INFORMATION_RETRIEVAL',
      'report-generation': 'REPORT_GENERATION',
      'problem-solving': 'PROBLEM_SOLVING',
      'automation': 'AUTOMATION',
      'industry-knowledge': 'INDUSTRY_KNOWLEDGE',
      'general-chat': 'GENERAL_CHAT',
      'data-operations': 'DATA_OPERATIONS',
      'auto': 'auto'
    };

    const routerAgent = agentMap[agent] || 'auto';

    const pythonArgs = [
      routerPath,
      message,
      '--session-id', sessionId,
      '--user-id', 'web-user',
      '--json'
    ];

    // Only add agent filter if not 'auto'
    if (routerAgent !== 'auto') {
      pythonArgs.push('--agent', routerAgent);
    }

    console.log(`[${new Date().toISOString()}] Calling Python AI Router:`, {
      python: pythonPath,
      script: routerPath,
      agent: routerAgent
    });

    const pythonProcess = spawn(pythonPath, pythonArgs);

    let stdout = '';
    let stderr = '';

    pythonProcess.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    pythonProcess.on('close', (code) => {
      const responseTime = Date.now() - startTime;

      if (code === 0) {
        try {
          // Parse JSON output from Python CLI
          const result = JSON.parse(stdout);

          console.log(`[${new Date().toISOString()}] Python AI Router response in ${responseTime}ms:`, {
            success: result.success,
            agent: result.agent,
            confidence: result.confidence,
            hasGraphAnalysis: result.metadata?.graph_analysis !== undefined
          });

          // Return response in format expected by frontend
          res.json({
            success: true,
            message: result.content || '',
            metadata: {
              agent: result.agent || agent,
              confidence: result.confidence || 0.8,
              model: result.metadata?.llm_model || 'llama-3-70b-8192',
              tokens: result.metadata?.tokens || {},
              processingTime: result.latency_ms || responseTime,
              sessionId,
              historyLength: 0,
              // ✨ Graph analysis from ReportGenerationAgent!
              graph_analysis: result.metadata?.graph_analysis || undefined
            }
          });

        } catch (parseError) {
          console.error(`[${new Date().toISOString()}] Failed to parse Python output:`, parseError);
          console.error('Python stdout:', stdout.substring(0, 500));

          res.status(500).json({
            success: false,
            error: 'Failed to parse AI Router response'
          });
        }
      } else {
        console.error(`[${new Date().toISOString()}] Python AI Router error (code ${code}):`, stderr);

        res.status(500).json({
          success: false,
          error: 'AI Router execution failed',
          details: stderr.substring(0, 200)
        });
      }
    });

    // Timeout after 30 seconds
    setTimeout(() => {
      pythonProcess.kill();
      res.status(504).json({
        success: false,
        error: 'AI Router timeout'
      });
    }, 30000);

  } catch (error) {
    console.error(`[${new Date().toISOString()}] Error in /api/chat:`, error);
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
