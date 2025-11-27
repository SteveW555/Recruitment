import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import Groq from 'groq-sdk';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { spawn } from 'child_process';
import { ensureRouterRunning, stopRouter, getStatus } from './pythonRouterManager.js';
import { Logger } from '../logging_new.js';

// Load environment variables
dotenv.config({ path: '../.env' });

// Initialize logger
const logger = new Logger('backend-api');

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

// Invoice Builder endpoint - runs dump_usage.py script
app.post('/api/invoice-builder', async (req, res) => {
  logger.info(`*******/api/invoice-builder endpoint called*******`);

  const projectRoot = join(__dirname, '..');
  const scriptPath = join(projectRoot, 'backend', 'dump_usage.py');

  // Get model and csvPath from request body, with defaults
  const {
    model = 'groq/llama-3.3-70b-versatile',
    csvPath = 'ExamplesRealOnly/strat_messy.csv'
  } = req.body;

  // Resolve csvPath relative to project root
  const resolvedCsvPath = join(projectRoot, csvPath);

  console.log(`[${new Date().toISOString()}] Invoice Builder request`);
  console.log(`  Script: ${scriptPath}`);
  console.log(`  Model: ${model}`);
  console.log(`  CSV: ${resolvedCsvPath}`);

  // Pre-flight checks
  const fs = await import('fs');

  // Check if script exists
  if (!fs.existsSync(scriptPath)) {
    const error = `Script not found: ${scriptPath}`;
    console.error(`[${new Date().toISOString()}] ${error}`);
    return res.json({
      success: false,
      output: '',
      error: error,
      exitCode: -1
    });
  }

  // Check if CSV file exists
  if (!fs.existsSync(resolvedCsvPath)) {
    const error = `CSV file not found: ${resolvedCsvPath}`;
    console.error(`[${new Date().toISOString()}] ${error}`);
    return res.json({
      success: false,
      output: '',
      error: error,
      exitCode: -1
    });
  }

  try {
    const pythonProcess = spawn('python', [
      scriptPath,
      '-m', model,
      '-p',
      '-f', resolvedCsvPath,
      '-t'
    ], {
      cwd: projectRoot,
      env: { ...process.env }
    });

    let stdout = '';
    let stderr = '';

    pythonProcess.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    pythonProcess.on('close', (code) => {
      console.log(`[${new Date().toISOString()}] Invoice Builder completed with code ${code}`);

      if (code !== 0) {
        console.error(`[${new Date().toISOString()}] Invoice Builder failed:`);
        console.error(`  stdout: ${stdout.substring(0, 500)}`);
        console.error(`  stderr: ${stderr.substring(0, 500)}`);
      }

      res.json({
        success: code === 0,
        output: stdout,
        error: code !== 0 ? (stderr || stdout || `Process exited with code ${code}`) : null,
        exitCode: code,
        model,
        csvPath: resolvedCsvPath
      });
    });

    pythonProcess.on('error', (error) => {
      console.error(`[${new Date().toISOString()}] Invoice Builder spawn error:`, error);
      res.status(500).json({
        success: false,
        error: error.message
      });
    });

  } catch (error) {
    console.error('Error in /api/invoice-builder:', error);
    logger.error(`*** Error in /api/invoice-builder endpoint`, {
      error: error.message
    });

    res.status(500).json({
      success: false,
      error: error.message || 'Internal server error'
    });
  }
});

// Chat endpoint - Fast version using persistent Python server
app.post('/api/chat', async (req, res) => {
  logger.info(`*******/api/chat endpoint called*******`);

  try {
    logger.info(`*** Trying...`);
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

    logger.info(`*** Chat request received`, {
      sessionId,
      agent,
      messageLength: message.length,
      useHistory
    });

    //=====================================================
    // Call persistent Python AI Router HTTP Server (FAST!)
    //=====================================================

    const startTime = Date.now();
    logger.info(`*** Calling AI Router at ${AI_ROUTER_URL}/route`);

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
        suggested_table: result.suggested_table || null,
        fallback_triggered: result.fallback_triggered,
        error: result.error || null
      });

      logger.info(`*** AI Router response received in ${responseTime}ms`, {
        agent: result.agent,
        confidence: result.confidence,
        suggested_table: result.suggested_table || null,
        success: result.success
      });

      // Log low confidence warning if present
      if (result.low_confidence_warning) {
        console.warn(`[${new Date().toISOString()}] ${result.low_confidence_warning}`);
        logger.warn(`*** Low confidence warning from AI Router`, {
          warning: result.low_confidence_warning,
          sessionId
        });
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

      // Log metadata for debugging
      if (result.metadata) {
        console.log(`[${new Date().toISOString()}] Result metadata keys:`, Object.keys(result.metadata));
        if (result.metadata.sql_query) {
          console.log(`[${new Date().toISOString()}] SQL query in result.metadata:`, result.metadata.sql_query.substring(0, 100) + '...');
        }
        if (result.metadata.result_count !== undefined) {
          console.log(`[${new Date().toISOString()}] Result count in result.metadata:`, result.metadata.result_count);
        }
      }

      // Return successful response in format expected by frontend
      res.json({
        success: true,
        message: result.content || '',
        metadata: {
          agent: result.agent || agent,
          confidence: result.confidence || 0.8,
          reasoning: result.reasoning || null,  // Classification reasoning from GroqClassifier
          system_prompt: result.system_prompt || null,  // Full system prompt sent to GroqClassifier
          agent_prompt: result.metadata?.agent_prompt || null,  // Agent's prompt sent to LLM
          sql_query: result.metadata?.sql_query || null,  // SQL query generated (for INFORMATION_RETRIEVAL)
          sql_results: result.metadata?.sql_results || null,  // SQL results (for INFORMATION_RETRIEVAL)
          result_count: result.metadata?.result_count || null,  // Number of results (for INFORMATION_RETRIEVAL)
          classification_latency_ms: result.classification_latency_ms || null,
          fallback_triggered: result.fallback_triggered || false,
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
      logger.error(`*** Failed to call AI Router`, {
        error: fetchError.message,
        url: AI_ROUTER_URL
      });

      res.status(503).json({
        success: false,
        error: 'AI Router service unavailable',
        details: 'Please ensure Python HTTP server is running: start-ai-router-server.bat'
      });
    }

  } catch (error) {
    console.error('Error in /api/chat:', error);
    logger.error(`*** Error in /api/chat endpoint`, {
      error: error.message,
      stack: error.stack?.substring(0, 200)
    });

    res.status(500).json({
      success: false,
      error: error.message || 'Internal server error'
    });
  }
});

// Initialize and start server
async function initializeServer() {
  console.log(`\n${'='.repeat(60)}`);
  console.log(`🚀 Backend API Server (FAST VERSION)`);
  console.log(`${'='.repeat(60)}`);

  try {
    // Start AI Router (or verify it's running)
    console.log(`\n[*] Initializing AI Router...`);
    const routerStarted = await ensureRouterRunning();

    if (!routerStarted) {
      console.error(`\n❌ Failed to start AI Router`);
      console.error(`   Please check logs/ai-router.log for details`);
      process.exit(1);
    }

    // Start Express server
    app.listen(PORT, () => {
      console.log(`\n${'='.repeat(60)}`);
      console.log(`✅ Backend server running on port ${PORT}`);
      console.log(`✅ GROQ API Key: ${process.env.GROQ_API_KEY ? 'Configured' : 'Missing'}`);
      console.log(`✅ AI Router: Ready on ${AI_ROUTER_URL}`);
      console.log(`\n🔗 Endpoints:`);
      console.log(`   Health: http://localhost:${PORT}/health`);
      console.log(`   Chat:   http://localhost:${PORT}/api/chat`);
      console.log(`${'='.repeat(60)}\n`);

      // Log to unified logging system
      logger.info(`Backend API server started on port ${PORT} (fast version)`);
    });

  } catch (error) {
    console.error(`\n❌ Failed to initialize server:`, error.message);
    console.error(`   Check logs/ai-router.log for details`);
    process.exit(1);
  }
}

// Clean shutdown handlers
process.on('SIGINT', () => {
  console.log('\n\nShutting down gracefully...');
  stopRouter();
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\n\nReceived SIGTERM, shutting down...');
  stopRouter();
  process.exit(0);
});

process.on('exit', () => {
  stopRouter();
});

// Handle uncaught errors
process.on('uncaughtException', (error) => {
  console.error('\n❌ Uncaught exception:', error);
  stopRouter();
  process.exit(1);
});

// Start everything
initializeServer();
