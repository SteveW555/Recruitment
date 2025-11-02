# Infrastructure Directory

This directory contains deployment, orchestration, and infrastructure-as-code configurations.

## Structure

```
infrastructure/
├── docker/              # Docker configurations
│   ├── .dockerignore   # Docker build ignore patterns
│   ├── docker-compose.yml  # Multi-container orchestration
│   └── Dockerfile.ai-router  # AI Router service container
├── railway.toml        # Railway deployment configuration
└── README.md           # This file
```

## Docker

### docker-compose.yml
Multi-service orchestration for local development and testing.

**Usage:**
```bash
# Start all services
docker-compose -f infrastructure/docker/docker-compose.yml up

# Stop all services
docker-compose -f infrastructure/docker/docker-compose.yml down
```

### Dockerfile.ai-router
Container definition for the Python AI Router service.

**Build:**
```bash
docker build -f infrastructure/docker/Dockerfile.ai-router -t ai-router .
```

## Railway Deployment

### railway.toml
Configuration for Railway.app cloud deployment.

**Deploy:**
```bash
railway up
```

## PM2 (Production Process Management)

If `ecosystem.config.js` exists in this directory, it defines PM2 configuration for production process management.

**Usage:**
```bash
pm2 start infrastructure/ecosystem.config.js
pm2 status
pm2 logs
pm2 stop all
```

## Other Infrastructure

Additional infrastructure configurations may include:
- Kubernetes manifests (future)
- Terraform configurations (future)
- CI/CD pipelines (future)

## See Also

- [scripts/Makefile](../scripts/Makefile) - Build and deployment automation
- [docs_root/deployment/](../docs_root/) - Deployment guides
