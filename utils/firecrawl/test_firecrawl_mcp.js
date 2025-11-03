// Test script to verify Firecrawl MCP installation
// Run this with: env FIRECRAWL_API_KEY=your-api-key node test_firecrawl_mcp.js

console.log('Testing Firecrawl MCP Server installation...');

// Check if firecrawl-mcp is available
const { spawn } = require('child_process');

const testCommand = spawn('npx', ['-y', 'firecrawl-mcp', '--version'], {
    stdio: 'inherit',
    env: {
        ...process.env,
        FIRECRAWL_API_KEY: process.env.FIRECRAWL_API_KEY || 'test-key'
    }
});

testCommand.on('close', (code) => {
    if (code === 0) {
        console.log('✅ Firecrawl MCP server is installed and accessible');
    } else {
        console.log('❌ There might be an issue with the installation');
    }
});

testCommand.on('error', (error) => {
    console.error('❌ Error running Firecrawl MCP:', error.message);
});