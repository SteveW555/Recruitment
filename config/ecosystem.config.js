/**
 * PM2 Ecosystem Configuration for Elephant AI
 *
 * Professional process manager for production/team environments.
 *
 * Installation (one-time):
 *   npm install -g pm2
 *
 * Usage:
 *   pm2 start ecosystem.config.js    # Start all services
 *   pm2 status                        # Check status
 *   pm2 logs                          # View logs
 *   pm2 logs ai-router               # View specific service
 *   pm2 stop all                      # Stop all services
 *   pm2 restart all                   # Restart all services
 *   pm2 delete all                    # Remove all services
 *
 * Auto-start on boot:
 *   pm2 startup                       # Setup startup script
 *   pm2 save                          # Save current process list
 */

module.exports = {
  apps: [
    {
      name: 'ai-router',
      script: 'python',
      args: ['-m', 'utils.ai_router.ai_router_api'],
      cwd: 'd:/Recruitment',
      interpreter: 'none',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '2G',
      env: {
        PYTHONIOENCODING: 'utf-8',
        // API keys will be loaded from .env or environment
      },
      error_file: 'logs/ai-router-error.log',
      out_file: 'logs/ai-router-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true
    },
    {
      name: 'backend',
      script: 'npm',
      args: 'start',
      cwd: 'd:/Recruitment/backend-api',
      interpreter: 'none',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '512M',
      env: {
        BACKEND_PORT: '3002',
        NODE_ENV: 'development',
        // API keys will be loaded from .env
      },
      error_file: 'logs/backend-error.log',
      out_file: 'logs/backend-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true
    },
    {
      name: 'frontend',
      script: 'npm',
      args: 'start',
      cwd: 'd:/Recruitment/frontend',
      interpreter: 'none',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '512M',
      env: {
        NODE_ENV: 'development'
      },
      error_file: 'logs/frontend-error.log',
      out_file: 'logs/frontend-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true
    }
  ]
};
