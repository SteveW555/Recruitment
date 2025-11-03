# Gmail Service - Deployment Guide

Comprehensive deployment guide for the Gmail Email Search & CV Extraction service.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Database Migrations](#database-migrations)
7. [Monitoring & Observability](#monitoring--observability)
8. [Troubleshooting](#troubleshooting)
9. [Rollback Procedures](#rollback-procedures)

---

## Prerequisites

### Software Requirements

| Component | Version | Purpose |
|-----------|---------|---------|
| Node.js | 20.x LTS | Runtime environment |
| Docker | 24.x+ | Container runtime |
| Kubernetes | 1.28+ | Orchestration (production) |
| PostgreSQL | 15.x | Primary database |
| Redis | 7.x | Caching & sessions |
| kubectl | 1.28+ | K8s CLI |
| helm | 3.12+ | Package manager (optional) |

### Cloud Provider Accounts

- **Google Cloud Platform**: OAuth credentials
- **AWS/Azure/GCP**: Infrastructure hosting
- **Domain**: SSL certificate for HTTPS

### Access Requirements

- Database credentials
- Redis credentials
- Google OAuth client ID & secret
- SSL certificates (production)
- Container registry access

---

## Local Development

### 1. Install Dependencies

```bash
cd backend/services/gmail-service
npm install
```

### 2. Configure Environment

Create `.env` file:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
NODE_ENV=development
PORT=8080

# Database
DATABASE_URL=postgresql://gmail_user:gmail_password@localhost:5432/gmail_service

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Google OAuth
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8080/api/v1/auth/google/callback

# Session
SESSION_SECRET=generate-a-64-character-random-string

# Frontend
FRONTEND_URL=http://localhost:3000
```

### 3. Run Database Migrations

```bash
npx prisma migrate dev
```

### 4. Start Development Server

```bash
npm run start:dev
```

Service available at: http://localhost:8080
API Documentation: http://localhost:8080/api/docs

---

## Docker Deployment

### Using Docker Compose (Recommended for Development)

#### 1. Configure Environment Variables

Create `.env` file in the service directory:

```bash
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
SESSION_SECRET=your-64-char-secret
REDIS_PASSWORD=your-redis-password
```

#### 2. Start All Services

```bash
docker-compose up -d
```

This starts:
- Gmail Service (port 8080)
- PostgreSQL (port 5432)
- Redis (port 6379)

#### 3. View Logs

```bash
docker-compose logs -f gmail-service
```

#### 4. Stop Services

```bash
docker-compose down
```

### Optional: Start with Monitoring

```bash
docker-compose --profile monitoring up -d
```

This adds:
- Prometheus (port 9090)
- Grafana (port 3002)

Access Grafana: http://localhost:3002 (admin/admin)

### Building Production Image

```bash
# Build the image
docker build -t proactive-people/gmail-service:1.0.0 .

# Tag as latest
docker tag proactive-people/gmail-service:1.0.0 proactive-people/gmail-service:latest

# Push to registry
docker push proactive-people/gmail-service:1.0.0
docker push proactive-people/gmail-service:latest
```

---

## Kubernetes Deployment

### Prerequisites

1. Kubernetes cluster (1.28+)
2. kubectl configured
3. Container registry
4. Ingress controller (NGINX)
5. cert-manager for SSL

### Deployment Steps

#### 1. Create Namespace

```bash
kubectl apply -f k8s/namespace.yaml
```

#### 2. Create Secrets

**Important**: Never commit secrets to version control!

```bash
# Generate strong session secret
SESSION_SECRET=$(openssl rand -base64 48)

# Create Kubernetes secret
kubectl create secret generic gmail-service-secrets \
  --namespace=gmail-service \
  --from-literal=DATABASE_URL='postgresql://user:password@postgres-host:5432/gmail_service' \
  --from-literal=SESSION_SECRET="$SESSION_SECRET" \
  --from-literal=GOOGLE_CLIENT_ID='your-google-client-id' \
  --from-literal=GOOGLE_CLIENT_SECRET='your-google-client-secret' \
  --from-literal=REDIS_PASSWORD='your-redis-password'
```

#### 3. Apply ConfigMap

```bash
kubectl apply -f k8s/configmap.yaml
```

Review and update configuration values if needed.

#### 4. Create Service Account & RBAC

```bash
kubectl apply -f k8s/serviceaccount.yaml
```

#### 5. Create Persistent Volume Claims

```bash
kubectl apply -f k8s/pvc.yaml
```

Wait for PVCs to be bound:

```bash
kubectl get pvc -n gmail-service --watch
```

#### 6. Deploy Redis

```bash
kubectl apply -f k8s/redis-statefulset.yaml
kubectl apply -f k8s/service.yaml
```

Wait for Redis to be ready:

```bash
kubectl wait --for=condition=ready pod -l app=gmail-redis -n gmail-service --timeout=300s
```

#### 7. Deploy Gmail Service

```bash
kubectl apply -f k8s/deployment.yaml
```

The init container will run database migrations automatically.

Monitor deployment:

```bash
kubectl rollout status deployment/gmail-service -n gmail-service
```

#### 8. Create Service

```bash
kubectl apply -f k8s/service.yaml
```

#### 9. Create Ingress

Update `k8s/ingress.yaml` with your domain:

```bash
kubectl apply -f k8s/ingress.yaml
```

#### 10. Enable Autoscaling

```bash
kubectl apply -f k8s/hpa.yaml
```

### Verification

```bash
# Check all resources
kubectl get all -n gmail-service

# Check pod logs
kubectl logs -f deployment/gmail-service -n gmail-service

# Check health
kubectl get pods -n gmail-service
kubectl exec -it <pod-name> -n gmail-service -- wget -q -O- http://localhost:8080/health
```

---

## Environment Configuration

### Required Environment Variables

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| NODE_ENV | Environment | production | Yes |
| PORT | Service port | 8080 | Yes |
| DATABASE_URL | PostgreSQL connection | postgresql://... | Yes |
| REDIS_HOST | Redis hostname | redis-service | Yes |
| REDIS_PORT | Redis port | 6379 | Yes |
| REDIS_PASSWORD | Redis password | secret | No |
| GOOGLE_CLIENT_ID | OAuth client ID | xxx.apps.googleusercontent.com | Yes |
| GOOGLE_CLIENT_SECRET | OAuth secret | secret | Yes |
| GOOGLE_REDIRECT_URI | OAuth callback | https://api.../callback | Yes |
| SESSION_SECRET | Session secret (64+ chars) | random-string | Yes |
| FRONTEND_URL | Frontend origin | https://app.example.com | Yes |

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| STORAGE_PATH | File storage path | /app/storage/downloads |
| MAX_FILE_SIZE | Max file size (bytes) | 26214400 (25MB) |
| FILE_RETENTION_HOURS | Retention period | 24 |
| CLEANUP_CRON | Cleanup schedule | 0 * * * * |

---

## Database Migrations

### Development

```bash
# Create migration
npx prisma migrate dev --name description_of_changes

# Apply migrations
npx prisma migrate dev
```

### Production

Migrations run automatically via Kubernetes init container.

Manual migration:

```bash
# Inside container
kubectl exec -it <pod-name> -n gmail-service -- npx prisma migrate deploy

# From local machine
DATABASE_URL="postgresql://..." npx prisma migrate deploy
```

### Rollback Migration

```bash
# View migration history
npx prisma migrate status

# Rollback is manual - restore database backup or create new migration
```

---

## Monitoring & Observability

### Health Endpoints

| Endpoint | Purpose | Use Case |
|----------|---------|----------|
| GET /health | Liveness | K8s liveness probe |
| GET /health/ready | Readiness | K8s readiness probe |
| GET /health/detailed | Detailed status | Debugging |
| GET /health/metrics | Prometheus metrics | Monitoring |

### Prometheus Metrics

Access Prometheus: http://prometheus:9090

**Key Metrics**:
- `http_request_duration_seconds` - Request latency
- `http_requests_total` - Request count
- `database_query_duration_seconds` - Database query latency
- `redis_connection_status` - Redis connection health
- `rate_limit_rejections_total` - Rate limit rejections
- `authentication_failures_total` - Auth failures

### Grafana Dashboards

Access Grafana: http://grafana:3000

**Dashboards**:
1. Service Overview - Health, requests, errors
2. Performance - Latency, throughput
3. Database - Query performance, connections
4. Redis - Memory, hit rate
5. Security - Auth failures, rate limits

### Logs

```bash
# Real-time logs
kubectl logs -f deployment/gmail-service -n gmail-service

# Last 100 lines
kubectl logs --tail=100 deployment/gmail-service -n gmail-service

# Logs from all pods
kubectl logs -f -l app=gmail-service -n gmail-service

# Previous container logs (after restart)
kubectl logs --previous deployment/gmail-service -n gmail-service
```

### Alerts

Prometheus alerts defined in `monitoring/alerts.yml`:
- Service down
- High error rate
- Database connection failure
- High response time
- High CPU/memory usage
- Security events

---

## Troubleshooting

### Pod Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n gmail-service

# Check events
kubectl get events -n gmail-service --sort-by='.lastTimestamp'

# Check logs
kubectl logs <pod-name> -n gmail-service
```

**Common Issues**:
- Missing secrets: Create secrets before deployment
- PVC not bound: Check storage class availability
- Image pull errors: Verify registry credentials
- Init container failing: Check database connectivity

### Service Not Accessible

```bash
# Check service
kubectl get svc -n gmail-service

# Check endpoints
kubectl get endpoints gmail-service -n gmail-service

# Test from another pod
kubectl run test --rm -it --image=curlimages/curl -- curl http://gmail-service/health
```

### Database Connection Issues

```bash
# Test connection from pod
kubectl exec -it <pod-name> -n gmail-service -- sh
# Inside pod:
wget -q -O- http://localhost:8080/health/ready
```

Check:
- DATABASE_URL secret is correct
- PostgreSQL is accessible
- Network policies allow traffic

### High Memory Usage

```bash
# Check resource usage
kubectl top pod -n gmail-service

# Describe pod limits
kubectl describe pod <pod-name> -n gmail-service
```

Solutions:
- Increase memory limits
- Check for memory leaks
- Scale horizontally (HPA)

---

## Rollback Procedures

### Rollback Deployment

```bash
# View rollout history
kubectl rollout history deployment/gmail-service -n gmail-service

# Rollback to previous version
kubectl rollout undo deployment/gmail-service -n gmail-service

# Rollback to specific revision
kubectl rollout undo deployment/gmail-service --to-revision=2 -n gmail-service

# Verify rollback
kubectl rollout status deployment/gmail-service -n gmail-service
```

### Rollback Database Migration

1. Restore database backup
2. Or create new migration to reverse changes
3. Test thoroughly before deploying

### Emergency Procedures

**Service Completely Down**:
```bash
# Scale to 0 (stop all pods)
kubectl scale deployment/gmail-service --replicas=0 -n gmail-service

# Fix issues

# Scale back up
kubectl scale deployment/gmail-service --replicas=3 -n gmail-service
```

**Database Issues**:
```bash
# Restore from backup
# Test connection
# Restart service
kubectl rollout restart deployment/gmail-service -n gmail-service
```

---

## Performance Optimization

### Scaling

**Horizontal Scaling**:
```bash
# Manual scaling
kubectl scale deployment/gmail-service --replicas=5 -n gmail-service

# Auto-scaling (HPA already configured)
kubectl get hpa -n gmail-service
```

**Vertical Scaling**:
Update resource limits in deployment.yaml

### Caching

- Redis caching enabled for email previews (15-minute TTL)
- Session caching in Redis
- Rate limiting in Redis

### Database Optimization

- Connection pooling via Prisma
- Indexed queries
- Query optimization via Prisma

---

## Security Considerations

### Production Checklist

- [ ] SSL/TLS certificates installed
- [ ] Strong session secret (64+ characters)
- [ ] Secrets stored securely (not in version control)
- [ ] Rate limiting enabled
- [ ] Security headers enabled (Helmet)
- [ ] CORS configured correctly
- [ ] Database encryption at rest
- [ ] Regular security updates
- [ ] Audit logging enabled
- [ ] Backup procedures tested

### Network Security

- [ ] Network policies configured
- [ ] Ingress firewall rules
- [ ] DDoS protection enabled
- [ ] WAF configured (if applicable)

---

## Backup & Disaster Recovery

### Database Backups

```bash
# Automated backups (configure with cloud provider)
# Example for PostgreSQL
pg_dump -h $DB_HOST -U $DB_USER -d gmail_service -F c -f backup.dump

# Restore
pg_restore -h $DB_HOST -U $DB_USER -d gmail_service backup.dump
```

### Persistent Volume Backups

```bash
# Snapshot PVCs (cloud provider specific)
# AWS EBS snapshots
# Azure disk snapshots
# GCP persistent disk snapshots
```

### Redis Backups

Redis uses append-only file (AOF) persistence.
Regular snapshots created automatically.

---

## Support & Resources

### Documentation

- [SECURITY.md](./SECURITY.md) - Security documentation
- [TESTING.md](./TESTING.md) - Testing documentation
- [API Docs](http://localhost:8080/api/docs) - Swagger API documentation

### Monitoring

- Prometheus: http://prometheus:9090
- Grafana: http://grafana:3000
- Health Check: http://service/health

### Contact

- Support: info@proactivepeople.com
- Phone: 0117 9377 199

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-01-15 | Initial production release |

---

**Last Updated**: January 15, 2025
**Maintained By**: ProActive People DevOps Team
