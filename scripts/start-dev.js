#!/usr/bin/env node

/**
 * Cross-platform development startup script
 * Starts both backend API (port 3002) and frontend (port 5173)
 */

const { spawn } = require('child_process');
const path = require('path');
const chalk = require('chalk');

// Colors output
const blue = (str) => `\x1b[34m${str}\x1b[0m`;
const green = (str) => `\x1b[32m${str}\x1b[0m`;
const yellow = (str) => `\x1b[33m${str}\x1b[0m`;

console.log('\n' + blue('===================================='));
console.log(blue('  ELEPHANT RECRUITMENT - Dev Mode'));
console.log(blue('====================================\n'));

// Set environment variable for backend
process.env.BACKEND_PORT = '3002';

// Start backend
console.log(yellow('Starting backend API on port 3002...'));
const backend = spawn('npm', ['start'], {
  cwd: path.join(__dirname, '../backend-api'),
  stdio: 'inherit',
  shell: true
});

backend.on('error', (error) => {
  console.error('\x1b[31m✗ Backend failed to start:', error.message);
  process.exit(1);
});

// Wait a bit, then start frontend
setTimeout(() => {
  console.log(yellow('Starting frontend dev server on port 5173...'));
  const frontend = spawn('npm', ['run', 'dev'], {
    cwd: path.join(__dirname, '../frontend'),
    stdio: 'inherit',
    shell: true
  });

  frontend.on('error', (error) => {
    console.error('\x1b[31m✗ Frontend failed to start:', error.message);
    process.exit(1);
  });

  // Handle cleanup on exit
  process.on('SIGINT', () => {
    console.log('\n' + yellow('Stopping services...'));
    backend.kill();
    frontend.kill();
    process.exit(0);
  });
}, 3000);

console.log('\n' + green('✓ Services starting:'));
console.log(yellow('  - Backend:  http://localhost:3002/api/chat'));
console.log(yellow('  - Frontend: http://localhost:5173'));
console.log(yellow('  - Press Ctrl+C to stop both services\n'));
