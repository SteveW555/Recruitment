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

// AI Router HTTP Server URL
const AI_ROUTER_URL = process.env.AI_ROUTER_URL || 'http://localhost:8888';

// Health check endpoint
app.get('/health', async (req, res) => {
  // Check if Python AI Router is available
  let routerStatus = 'unavailable';
  try {
    const response = await fetch(`${AI_ROUTER_URL}/health`, { timeout: 2000 });
    if (response.ok) {
      routerStatus = 'healthy';
    }
  } catch (error) {
    console.warn('AI Router health check failed:', error.message);
  }

  res.json({
    status: 'ok',
    service: 'Elephant AI Backend',
    groq: !!process.env.GROQ_API_KEY,
    aiRouter: routerStatus,
    timestamp: new Date().toISOString()
  });
});

// Chat endpoint - Fast version using persistent Python server
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

    // Call persistent Python AI Router HTTP Server (FAST!)
    const startTime = Date.now();

    try {
      const response = await fetch(`${AI_ROUTER_URL}/route`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: message,
          session_id: sessionId,
          user_id: 'web-user'
        })
      });

      const responseTime = Date.now() - startTime;

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();

      console.log(`[${new Date().toISOString()}] AI Router response in ${responseTime}ms:`, {
        success: result.success,
        agent: result.agent,
        confidence: result.confidence,
        error: result.error || null
      });

      // Log low confidence warning if present
      if (result.low_confidence_warning) {
        console.warn(`[${new Date().toISOString()}] ${result.low_confidence_warning}`);
      }

      // Check if AI Router returned an error
      if (!result.success) {
        return res.json({
          success: false,
          error: result.error || 'AI Router returned an error',
          metadata: {
            agent: result.agent || agent,
            confidence: result.confidence || 0,
            processingTime: result.latency_ms || responseTime,
            sessionId
          }
        });
      }

      // Return successful response in format expected by frontend
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
          graph_analysis: result.metadata?.graph_analysis || undefined,
          lowConfidenceWarning: result.low_confidence_warning || null
        }
      });

    } catch (fetchError) {
      console.error(`[${new Date().toISOString()}] Failed to call AI Router:`, fetchError.message);

      res.status(503).json({
        success: false,
        error: 'AI Router service unavailable',
        details: 'Please ensure Python HTTP server is running: start-ai-router-server.bat'
      });
    }

  } catch (error) {
    console.error('Error in /api/chat:', error);
    res.status(500).json({
      success: false,
      error: error.message || 'Internal server error'
    });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`\n${'='.repeat(60)}`);
  console.log(`🚀 Backend API Server (FAST VERSION)`);
  console.log(`${'='.repeat(60)}`);
  console.log(`✅ Server running on port ${PORT}`);
  console.log(`✅ GROQ API Key: ${process.env.GROQ_API_KEY ? 'Configured' : 'Missing'}`);
  console.log(`✅ AI Router URL: ${AI_ROUTER_URL}`);
  console.log(`\n📋 IMPORTANT: Start Python server first!`);
  console.log(`   Run: start-ai-router-server.bat`);
  console.log(`\n🔗 Endpoints:`);
  console.log(`   Health: http://localhost:${PORT}/health`);
  console.log(`   Chat:   http://localhost:${PORT}/api/chat`);
  console.log(`${'='.repeat(60)}\n`);
});
