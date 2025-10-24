# Redis Setup for Windows

## Why Redis?
Redis stores conversation context between chat messages, enabling:
- Multi-turn conversations with memory
- Session continuity ("Tell me more about that candidate")
- 30-minute auto-expiring sessions

## Installation Options

### Option 1: MSI Installer (Easiest)

1. **Download**:
   - URL: https://github.com/microsoftarchive/redis/releases/download/win-3.0.504/Redis-x64-3.0.504.msi
   - Size: ~6 MB
   - Free & Open Source

2. **Install**:
   - Run the MSI installer
   - ✅ Check "Add to PATH"
   - Accept default location: `C:\Program Files\Redis`
   - ✅ Check "Install as Windows Service" (recommended)

3. **Start Redis**:
   ```bash
   # Redis will auto-start as a Windows service
   # Or manually start:
   redis-server
   ```

4. **Test Connection**:
   ```bash
   redis-cli ping
   # Should return: PONG
   ```

### Option 2: Memurai (Modern, Recommended for Production)

1. **Download**: https://www.memurai.com/get-memurai
2. Select "Developer Edition" (free)
3. Install and it auto-starts as a service

### Option 3: Docker (If you have Docker Desktop)

```bash
docker run -d -p 6379:6379 --name redis redis:latest
```

## Verification

After installation, run:

```bash
# Test if Redis is running
redis-cli ping

# Expected output: PONG
```

Or test from your Recruitment project:

```bash
python -c "import redis; r = redis.Redis(host='localhost', port=6379); print('Connected!' if r.ping() else 'Failed')"
```

## Railway.app Deployment (Production)

When deploying to Railway:

1. In Railway dashboard: **New → Database → Redis**
2. Railway auto-provides these environment variables:
   - `REDIS_HOST`
   - `REDIS_PORT`
   - `REDIS_PASSWORD`
3. Your code already reads these! Zero changes needed.

## Configuration in This Project

Redis settings (already configured):
- **Host**: `localhost` (dev) / `$REDIS_HOST` (production)
- **Port**: `6379` (standard)
- **Database**: 0 (default)
- **TTL**: 30 minutes per session
- **Max Connections**: 10 (connection pooling)

Config file: `utils/ai_router/storage/session_store.py`

## If You Don't Want Redis

**Option**: Use in-memory mock store (loses context between server restarts)
- Good for: Initial testing
- Bad for: Multi-turn conversations, production use

Let me know if you want to use the mock instead!

## Cost

- **Development**: $0 (free)
- **Production**:
  - Railway Redis: ~$5-10/month (includes 256MB RAM)
  - Self-hosted: $0 (but you manage it)
  - Cloud Redis (AWS ElastiCache, etc.): ~$15-50/month

## Next Steps

1. Install Redis (5 minutes)
2. Start the service
3. Run `redis-cli ping` to verify
4. Restart your chat application (`npm start`)
5. Test chat - context will now persist! ✨
