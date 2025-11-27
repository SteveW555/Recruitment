/**
 * Python AI Router Lifecycle Manager
 *
 * Manages the Python HTTP server as a child process of the backend.
 * Handles startup, health checks, logging, and graceful shutdown.
 */

import { spawn, spawnSync } from 'child_process';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { existsSync, mkdirSync, createWriteStream } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

/**
 * Find Python executable - checks common locations on Windows
 * @returns {string} Path to Python executable
 */
function getPythonCommand() {
  // 1. Check environment variable override
  if (process.env.PYTHON_PATH && existsSync(process.env.PYTHON_PATH)) {
    return process.env.PYTHON_PATH;
  }

  // 2. Check if 'python' is in PATH
  const pythonCheck = spawnSync('python', ['--version'], { shell: true, stdio: 'pipe' });
  if (pythonCheck.status === 0) {
    return 'python';
  }

  // 3. Check if 'python3' is in PATH (Linux/Mac)
  const python3Check = spawnSync('python3', ['--version'], { shell: true, stdio: 'pipe' });
  if (python3Check.status === 0) {
    return 'python3';
  }

  // 4. Check if 'py' launcher is available (Windows)
  const pyCheck = spawnSync('py', ['--version'], { shell: true, stdio: 'pipe' });
  if (pyCheck.status === 0) {
    return 'py';
  }

  // 5. Check common Windows installation paths
  const windowsPaths = [
    join(process.env.LOCALAPPDATA || '', 'Programs', 'Python', 'Python313', 'python.exe'),
    join(process.env.LOCALAPPDATA || '', 'Programs', 'Python', 'Python312', 'python.exe'),
    join(process.env.LOCALAPPDATA || '', 'Programs', 'Python', 'Python311', 'python.exe'),
    join(process.env.LOCALAPPDATA || '', 'Programs', 'Python', 'Python310', 'python.exe'),
    join(process.env.LOCALAPPDATA || '', 'Programs', 'Python', 'Python39', 'python.exe'),
    'C:\\Python313\\python.exe',
    'C:\\Python312\\python.exe',
    'C:\\Python311\\python.exe',
  ];

  for (const pythonPath of windowsPaths) {
    if (existsSync(pythonPath)) {
      console.log(`[Router Manager] Found Python at: ${pythonPath}`);
      return pythonPath;
    }
  }

  // Fallback to 'python' and let it fail with a clear error
  return 'python';
}

// Global state
let routerProcess = null;
let isReady = false;
let logStream = null;

const ROUTER_URL = 'http://localhost:8888';
const HEALTH_ENDPOINT = `${ROUTER_URL}/health`;
const STARTUP_TIMEOUT_MS = 30000; // 30 seconds
const HEALTH_CHECK_INTERVAL_MS = 1000; // 1 second

/**
 * Check if Python AI Router is already running
 */
async function isRouterRunning() {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2000);

    const response = await fetch(HEALTH_ENDPOINT, {
      signal: controller.signal
    });

    clearTimeout(timeoutId);
    return response.ok;
  } catch (error) {
    return false;
  }
}

/**
 * Ensure logs directory exists
 */
function ensureLogsDirectory() {
  const projectRoot = join(__dirname, '..');
  const logsDir = join(projectRoot, 'logs');

  if (!existsSync(logsDir)) {
    mkdirSync(logsDir, { recursive: true });
    console.log('[Router Manager] Created logs directory');
  }
}

/**
 * Start Python AI Router as child process
 *
 * @returns {Promise<boolean>} True if started successfully, false otherwise
 */
async function startRouter() {
  console.log('[Router Manager] Checking if AI Router is running...');

  // Check if already running
  if (await isRouterRunning()) {
    console.log('[Router Manager] AI Router already running ✓');
    isReady = true;
    return true;
  }

  console.log('[Router Manager] Starting AI Router (~13 seconds for model load)...');

  return new Promise((resolve, reject) => {
    const projectRoot = join(__dirname, '..');

    // Ensure logs directory exists
    ensureLogsDirectory();

    // Find Python executable
    const pythonCmd = getPythonCommand();
    console.log(`[Router Manager] Using Python: ${pythonCmd}`);

    // Spawn Python process
    routerProcess = spawn(pythonCmd, ['-m', 'utils.ai_router.ai_router_api'], {
      cwd: projectRoot,
      env: {
        ...process.env,
        PYTHONIOENCODING: 'utf-8'
      },
      stdio: ['ignore', 'pipe', 'pipe']
    });

    // Set up log file
    const logPath = join(projectRoot, 'logs', 'ai-router.log');
    logStream = createWriteStream(logPath, { flags: 'a' });

    // Log startup
    const timestamp = new Date().toISOString();
    logStream.write(`\n${'='.repeat(80)}\n`);
    logStream.write(`[${timestamp}] AI Router starting...\n`);
    logStream.write(`${'='.repeat(80)}\n\n`);

    // Pipe output to log file
    routerProcess.stdout.pipe(logStream);
    routerProcess.stderr.pipe(logStream);

    // Also show important messages in console
    routerProcess.stderr.on('data', (data) => {
      const msg = data.toString().trim();

      // Show progress messages
      if (msg.includes('[*]') || msg.includes('[OK]') || msg.includes('[ERROR]') || msg.includes('Uvicorn running')) {
        console.log(`[Router Manager] ${msg}`);
      }
    });

    // Handle process exit
    routerProcess.on('exit', (code, signal) => {
      isReady = false;

      if (code !== 0 && code !== null) {
        console.error(`[Router Manager] AI Router exited with code ${code}`);
        if (logStream) {
          logStream.write(`\n[ERROR] Process exited with code ${code}\n`);
        }
      }

      if (signal) {
        console.log(`[Router Manager] AI Router terminated by signal ${signal}`);
        if (logStream) {
          logStream.write(`\n[INFO] Process terminated by signal ${signal}\n`);
        }
      }

      // Close log stream
      if (logStream) {
        logStream.end();
        logStream = null;
      }

      routerProcess = null;
    });

    // Handle process errors
    routerProcess.on('error', (error) => {
      console.error(`[Router Manager] Failed to start Python process: ${error.message}`);
      if (logStream) {
        logStream.write(`\n[ERROR] Failed to start: ${error.message}\n`);
        logStream.end();
        logStream = null;
      }
      reject(error);
    });

    // Wait for health endpoint to become available
    let retries = 0;
    const maxRetries = STARTUP_TIMEOUT_MS / HEALTH_CHECK_INTERVAL_MS;

    const checkHealth = setInterval(async () => {
      retries++;

      if (await isRouterRunning()) {
        clearInterval(checkHealth);
        isReady = true;
        console.log('[Router Manager] AI Router ready ✓');

        if (logStream) {
          logStream.write(`[${new Date().toISOString()}] Health check passed - router ready\n`);
        }

        resolve(true);
      } else if (retries >= maxRetries) {
        clearInterval(checkHealth);
        console.error('[Router Manager] AI Router failed to start (timeout after 30s)');

        if (logStream) {
          logStream.write(`[${new Date().toISOString()}] [ERROR] Startup timeout\n`);
          logStream.end();
          logStream = null;
        }

        // Kill the process if it's still running
        if (routerProcess) {
          routerProcess.kill();
        }

        reject(new Error('Router startup timeout'));
      }
    }, HEALTH_CHECK_INTERVAL_MS);
  });
}

/**
 * Stop Python AI Router gracefully
 */
function stopRouter() {
  if (routerProcess) {
    console.log('[Router Manager] Stopping AI Router...');

    if (logStream) {
      logStream.write(`\n[${new Date().toISOString()}] Shutting down...\n`);
      logStream.end();
      logStream = null;
    }

    routerProcess.kill('SIGTERM');
    routerProcess = null;
    isReady = false;
  }
}

/**
 * Get current status of the router
 *
 * @returns {Object} Status information
 */
function getStatus() {
  return {
    running: routerProcess !== null,
    ready: isReady,
    pid: routerProcess?.pid || null,
    url: isReady ? ROUTER_URL : null
  };
}

/**
 * Ensure router is running (start if needed)
 *
 * This is the main function to call from backend startup.
 *
 * @returns {Promise<boolean>} True if router is ready
 */
async function ensureRouterRunning() {
  if (isReady && routerProcess) {
    console.log('[Router Manager] Router already running');
    return true;
  }

  try {
    await startRouter();
    return true;
  } catch (error) {
    console.error('[Router Manager] Failed to start router:', error.message);
    return false;
  }
}

// Export public API
export {
  ensureRouterRunning,
  stopRouter,
  getStatus,
  isRouterRunning
};
