# Railway.app Deployment Guide - AI Router

## Model Handling Strategy

The `all-MiniLM-L6-v2` model is **pre-downloaded during Docker build** to avoid runtime delays.

### How It Works

1. **Build Time**: Model downloads into Docker image (~25MB)
2. **Runtime**: Model loads instantly from image (no download)
3. **Result**: Fast cold starts, no network dependency

---

## Deployment Steps

### 1. Install Railway CLI

```bash
npm install -g @railway/cli
railway login
```

### 2. Create Railway Project

```bash
# In your project directory
railway init

# Link to existing project (if you have one)
railway link
```

### 3. Set Environment Variables

```bash
# Required
railway variables set GROQ_API_KEY=your_key_here
railway variables set ANTHROPIC_API_KEY=your_key_here

# Optional
railway variables set PORT=8000
railway variables set CONFIDENCE_THRESHOLD=0.7
```

Or via Railway Dashboard:
- Go to your project
- Variables tab
- Add each variable

### 4. Deploy

```bash
railway up
```

**What happens:**
1. Railway builds Docker image
2. `RUN python -c "from sentence_transformers..."` downloads model (~30 seconds)
3. Model is baked into image
4. Image deployed
5. App starts with model already loaded

---

## Railway Configuration

### Using `railway.toml`

The included `railway.toml` configures:
- ✅ Dockerfile path
- ✅ Health check endpoint
- ✅ Restart policy

### Using Railway Dashboard

Alternatively, configure in the UI:
1. **Settings** → Dockerfile Path: `Dockerfile.ai-router`
2. **Settings** → Health Check Path: `/health`
3. **Settings** → Port: `8000`

---

## Resource Requirements

### Minimum (for AI Router + Model)

- **Memory**: 512MB (model ~200MB in memory)
- **CPU**: 0.5 vCPU
- **Storage**: 150MB (image + model)

### Recommended

- **Memory**: 1GB (handles concurrent requests)
- **CPU**: 1 vCPU
- **Storage**: 200MB

Railway typically provides:
- **Hobby Plan**: 512MB RAM, 0.5 vCPU
- **Developer Plan**: 8GB RAM, 8 vCPU

---

## Build Times

| Step | Time | Notes |
|------|------|-------|
| Python deps install | ~30s | Cached after first build |
| Model download | ~30s | Cached in image layer |
| Copy code | ~1s | Fast |
| **Total First Build** | ~60s | Subsequent: ~5-10s (cached layers) |

---

## Cold Start Performance

### With Baked-in Model (Current Setup)
- **Cold start**: 2-5 seconds (just Python startup)
- **First request**: <100ms (model already loaded)

### Without Baked-in Model (Alternative)
- **Cold start**: 30-60 seconds (downloads model)
- **First request**: <100ms after download

---

## Environment Variables

```bash
# Required for AI Router
GROQ_API_KEY=gsk_...                    # Groq API key
ANTHROPIC_API_KEY=sk-ant-...            # Anthropic API key

# Optional configuration
PORT=8000                                # Server port (Railway auto-assigns)
CONFIDENCE_THRESHOLD=0.7                 # Classification threshold
CONFIG_PATH=config/agents.json          # Agent configuration

# Database (for logging)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your_key

# Redis (for session management)
REDIS_URL=redis://...
```

---

## Monitoring on Railway

### View Logs
```bash
railway logs
```

Or in Dashboard → Deployments → Logs

### Check Model Loading

Look for these startup logs:
```
Loading sentence-transformers model: all-MiniLM-L6-v2...
[OK] Model loaded successfully
Loading example queries from config/agents.json...
[OK] Loaded and encoded examples for 6 categories
Server starting on port 8000...
```

---

## Cost Optimization

### Model Size Impact

**Without baked-in model:**
- Image: ~125MB
- RAM: ~300MB

**With baked-in model (current):**
- Image: ~150MB (+25MB)
- RAM: ~300MB (same, model loaded either way)

**Cost difference**: Negligible on Railway

---

## Deployment Checklist

- [ ] `Dockerfile.ai-router` exists
- [ ] `railway.toml` configured
- [ ] Environment variables set
- [ ] `config/agents.json` has example queries
- [ ] Test locally with Docker:
  ```bash
  docker build -f Dockerfile.ai-router -t ai-router .
  docker run -p 8000:8000 ai-router
  ```
- [ ] Deploy to Railway:
  ```bash
  railway up
  ```
- [ ] Test deployed endpoint:
  ```bash
  curl https://your-app.railway.app/health
  curl -X POST https://your-app.railway.app/classify \
    -H "Content-Type: application/json" \
    -d '{"query": "What are GDPR requirements?"}'
  ```

---

## Troubleshooting

### Issue: "Model not found" error

**Cause**: Model didn't download during build

**Fix**: Check Dockerfile has:
```dockerfile
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

Rebuild:
```bash
railway up --force
```

---

### Issue: Slow cold starts (30+ seconds)

**Cause**: Model downloading at runtime (not baked in)

**Fix**: Ensure Dockerfile has model download step (see above)

---

### Issue: Out of memory

**Cause**: Railway Hobby plan (512MB) might be tight

**Solution 1**: Upgrade to Developer plan

**Solution 2**: Use smaller model:
```python
model = SentenceTransformer('all-MiniLM-L6-v2')  # 25MB
# vs
model = SentenceTransformer('all-mpnet-base-v2')  # 420MB
```

---

### Issue: Build timeout

**Cause**: Network slow during model download

**Fix**: Railway build timeout is 10 minutes (plenty for 25MB model)

If it times out, check Railway status or try:
```bash
railway up --force
```

---

## Alternative: Railway Template

Create a `railway.json` for one-click deploy:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile.ai-router"
  },
  "deploy": {
    "startCommand": "python app.py",
    "healthcheckPath": "/health",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

---

## Scaling Considerations

### Horizontal Scaling
- Railway supports multiple replicas
- Each replica has its own model instance (no sharing)
- Load balanced automatically

### Model Loading
- Each replica: +200MB RAM
- Each replica: 2s startup (model already in image)

---

## Next Steps

1. **Test locally with Docker**:
   ```bash
   docker build -f Dockerfile.ai-router -t ai-router .
   docker run -p 8000:8000 ai-router
   ```

2. **Deploy to Railway**:
   ```bash
   railway up
   ```

3. **Test deployed endpoint**:
   ```bash
   curl https://your-app.railway.app/classify \
     -H "Content-Type: application/json" \
     -d '{"query": "Test query"}'
   ```

4. **Monitor logs**:
   ```bash
   railway logs --follow
   ```

---

## Summary

✅ **Model is baked into Docker image**
✅ **No download at runtime**
✅ **Fast cold starts (2-5s)**
✅ **No persistent storage needed**
✅ **Railway-optimized configuration**

The model deployment is **fully automated** and optimized for Railway.app!
