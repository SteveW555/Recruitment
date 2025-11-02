# Obsolete Scripts Directory

## Purpose

This directory contains batch files and shell scripts that are no longer used in the
current development workflow but have been preserved for reference.

## What's Here

### Obsolete Startup Scripts (Replaced by `npm start`)

These scripts were used before the lifecycle management system was implemented:

- **start-ai-router-server.bat** - Manual Python router startup
- **start-ai-router-server.bat.template** - Template for router startup
- **start-all.bat** - Started all 3 services manually
- **start-dev.bat** - Development startup script
- **stop-all.bat** - Manual shutdown script
- **status-check.bat** - Process status checker
- **dev.bat / dev.sh** - Old development scripts

## Why They're Obsolete

As of October 2025, the "Best Of" lifecycle management plan was implemented:
- Backend now automatically manages the Python router
- Single command startup: `npm start` (uses concurrently)
- Graceful shutdown with Ctrl+C
- No manual process management needed

See: `.claude/session-artifacts/LIFECYCLE_MANAGEMENT_APPROACH.md`

## Current Startup Method

```bash
# Start everything (backend + frontend + Python router)
npm start

# Stop everything
Ctrl+C (once)
```

The backend automatically:
1. Checks if Python router is running
2. Starts it if needed (13s first time)
3. Waits for health check
4. Kills it on shutdown

## If You Need These Scripts

These scripts are preserved in case:
- You need to understand the old workflow
- You want to run services manually for debugging
- You need to reference startup logic

For production deployment, use:
- PM2: `ecosystem.config.js` (still valid)
- Docker: `docker-compose.yml`
- Railway: `railway.toml`

---

Last Updated: 2025-11-02
Replaced By: Backend lifecycle management (pythonRouterManager.js)
