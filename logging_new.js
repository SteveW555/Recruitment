/**
 * Unified Logging System for ProActive People Recruitment System
 *
 * Provides consistent logging across Python backend and JavaScript frontend.
 * Logs to both terminal (with colors) and files.
 *
 * Usage:
 *     const { Logger } = require('./logging_new');
 *
 *     const logger = new Logger('backend-api');
 *     logger.info('Server started');
 *     logger.error('Connection failed', { host: 'localhost', port: 5432 });
 */

const fs = require('fs');
const path = require('path');

/**
 * ANSI color codes for terminal output
 */
const ColorCodes = {
    // Service colors
    FRONTEND: '\x1b[94m',      // Blue
    BACKEND: '\x1b[92m',       // Green
    PYTHON: '\x1b[93m',        // Yellow
    ROUTER: '\x1b[95m',        // Magenta
    DEFAULT: '\x1b[96m',       // Cyan

    // Log level colors
    DEBUG: '\x1b[37m',         // White
    INFO: '\x1b[97m',          // Bright White
    WARNING: '\x1b[93m',       // Yellow
    ERROR: '\x1b[91m',         // Red
    CRITICAL: '\x1b[95m\x1b[1m',  // Magenta Bold

    // Reset
    RESET: '\x1b[0m',
    BOLD: '\x1b[1m'
};

/**
 * Log levels (matching Python's logging module)
 */
const LogLevel = {
    DEBUG: 10,
    INFO: 20,
    WARNING: 30,
    ERROR: 40,
    CRITICAL: 50
};

/**
 * Get current time as HH:MM:SS
 */
function getTimeString() {
    const now = new Date();
    return now.toTimeString().split(' ')[0]; // HH:MM:SS
}

/**
 * Format log message with colors
 */
function formatMessage(serviceName, level, message, extraData, useColors = true) {
    const timestamp = getTimeString();

    // Map service names to colors
    const serviceColors = {
        'frontend': ColorCodes.FRONTEND,
        'backend': ColorCodes.BACKEND,
        'backend-api': ColorCodes.BACKEND,
        'python': ColorCodes.PYTHON,
        'router': ColorCodes.ROUTER,
        'ai-router': ColorCodes.ROUTER,
    };

    // Map log levels to colors
    const levelColors = {
        'DEBUG': ColorCodes.DEBUG,
        'INFO': ColorCodes.INFO,
        'WARNING': ColorCodes.WARNING,
        'ERROR': ColorCodes.ERROR,
        'CRITICAL': ColorCodes.CRITICAL,
    };

    // Get colors
    const serviceColor = serviceColors[serviceName.toLowerCase()] || ColorCodes.DEFAULT;
    const levelColor = levelColors[level] || ColorCodes.INFO;

    // Format extra data if present
    let fullMessage = message;
    if (extraData) {
        try {
            const extraJson = JSON.stringify(extraData, null, 2);
            fullMessage = `${message}\n${extraJson}`;
        } catch (err) {
            fullMessage = `${message}\n${extraData}`;
        }
    }

    if (useColors) {
        // Colored format for terminal
        return `${ColorCodes.BOLD}[${timestamp}]${ColorCodes.RESET} ${serviceColor}[${serviceName.toUpperCase()}]${ColorCodes.RESET} ${levelColor}[${level}]${ColorCodes.RESET} ${fullMessage}`;
    } else {
        // Plain format for files
        return `[${timestamp}] [${serviceName.toUpperCase()}] [${level}] ${fullMessage}`;
    }
}

/**
 * Append log message to file
 */
function appendToFile(filePath, message) {
    try {
        fs.appendFileSync(filePath, message + '\n', 'utf8');
    } catch (err) {
        // If we can't write to file, at least show it in console
        console.error(`Failed to write to log file ${filePath}:`, err.message);
    }
}

/**
 * Unified Logger class
 */
class Logger {
    /**
     * Initialize logger
     *
     * @param {string} serviceName - Name of the service (frontend, backend, python, router, etc.)
     * @param {string} logDir - Directory to store log files
     */
    constructor(serviceName = 'backend', logDir = 'logs') {
        this.serviceName = serviceName;
        this.logDir = logDir;

        // Create logs directory if it doesn't exist
        if (!fs.existsSync(this.logDir)) {
            fs.mkdirSync(this.logDir, { recursive: true });
        }

        // Log file paths
        this.combinedLog = path.join(this.logDir, 'combined.log');
        this.serviceLog = path.join(this.logDir, `${serviceName}.log`);
        this.errorLog = path.join(this.logDir, 'errors.log');
    }

    /**
     * Internal logging method
     */
    _log(level, levelName, message, extraData = null) {
        // Format messages
        const coloredMessage = formatMessage(this.serviceName, levelName, message, extraData, true);
        const plainMessage = formatMessage(this.serviceName, levelName, message, extraData, false);

        // Write to console (with colors)
        console.log(coloredMessage);

        // Write to files (without colors)
        appendToFile(this.combinedLog, plainMessage);
        appendToFile(this.serviceLog, plainMessage);

        // Write to error log if ERROR or CRITICAL
        if (level >= LogLevel.ERROR) {
            appendToFile(this.errorLog, plainMessage);
        }
    }

    /**
     * Log debug message
     */
    debug(message, extraData = null) {
        this._log(LogLevel.DEBUG, 'DEBUG', message, extraData);
    }

    /**
     * Log info message
     */
    info(message, extraData = null) {
        this._log(LogLevel.INFO, 'INFO', message, extraData);
    }

    /**
     * Log warning message
     */
    warning(message, extraData = null) {
        this._log(LogLevel.WARNING, 'WARNING', message, extraData);
    }

    /**
     * Log warning message (alias)
     */
    warn(message, extraData = null) {
        this.warning(message, extraData);
    }

    /**
     * Log error message
     */
    error(message, extraData = null) {
        this._log(LogLevel.ERROR, 'ERROR', message, extraData);
    }

    /**
     * Log critical message
     */
    critical(message, extraData = null) {
        this._log(LogLevel.CRITICAL, 'CRITICAL', message, extraData);
    }
}

/**
 * Singleton instances for common services
 */
const frontendLogger = new Logger('frontend');
const backendLogger = new Logger('backend-api');
const routerLogger = new Logger('ai-router');
const pythonLogger = new Logger('python');

/**
 * Test function
 */
function testLogger() {
    console.log('\n=== Testing Unified Logging System (JavaScript) ===\n');

    // Test different services
    const services = [
        ['frontend', 'Frontend application started'],
        ['backend-api', 'Backend API server listening on port 3002'],
        ['ai-router', 'AI Router initialized successfully'],
        ['python', 'Python service ready'],
    ];

    for (const [serviceName, message] of services) {
        const logger = new Logger(serviceName);
        logger.info(message);
    }

    console.log();

    // Test different log levels
    const testLogger = new Logger('test-service');
    testLogger.debug('This is a debug message');
    testLogger.info('This is an info message');
    testLogger.warning('This is a warning message');
    testLogger.error('This is an error message');
    testLogger.critical('This is a critical message');

    console.log();

    // Test with extra data
    testLogger.info('Database connection established', {
        host: 'localhost',
        port: 5432,
        database: 'recruitment'
    });

    testLogger.error('API request failed', {
        endpoint: '/api/candidates',
        status_code: 500,
        error: 'Internal server error'
    });

    console.log('\n=== Log files created in logs/ directory ===');
    console.log('  - logs/combined.log (all services)');
    console.log('  - logs/errors.log (errors only)');
    console.log('  - logs/<service-name>.log (per service)');
    console.log();
}

// Export the Logger class and singletons
module.exports = {
    Logger,
    LogLevel,
    frontendLogger,
    backendLogger,
    routerLogger,
    pythonLogger,
    testLogger
};

// Run test if executed directly
if (require.main === module) {
    testLogger();
}
