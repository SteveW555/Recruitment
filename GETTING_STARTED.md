# Getting Started with ProActive People Recruitment Automation System

This guide will help you set up and run the recruitment automation system on your local machine.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Running the Application](#running-the-application)
4. [Accessing Services](#accessing-services)
5. [Development Workflow](#development-workflow)
6. [Common Tasks](#common-tasks)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

Before you begin, ensure you have the following installed:

1. **Docker Desktop** (20.10+)
   - Windows: https://docs.docker.com/desktop/windows/install/
   - Mac: https://docs.docker.com/desktop/mac/install/
   - Linux: https://docs.docker.com/engine/install/

2. **Node.js** (18.x or higher)
   - Download from: https://nodejs.org/
   - Verify installation: `node --version`

3. **npm** or **Yarn** (comes with Node.js)
   - Verify installation: `npm --version`

4. **Git**
   - Download from: https://git-scm.com/
   - Verify installation: `git --version`

5. **Python** (3.11+) - For ML services
   - Download from: https://www.python.org/
   - Verify installation: `python --version`

### Optional but Recommended

- **Visual Studio Code**: https://code.visualstudio.com/
- **Postman** or **Insomnia**: For API testing
- **DBeaver** or **pgAdmin**: For database management
- **Make**: For using Makefile commands
  - Windows: `choco install make`
  - Mac: Already included
  - Linux: `sudo apt-get install build-essential`

## Initial Setup

### 1. Clone the Repository

```bash
git clone https://github.com/proactive-people/recruitment-automation.git
cd recruitment-automation
```

### 2. Environment Configuration

Copy the example environment file and configure it:

```bash
# Copy the example file
cp .env.example .env

# Edit the .env file with your preferred editor
nano .env
# or
code .env
```

**Important**: Update the following values in `.env`:
- Change all passwords from defaults
- Add your Bullhorn API credentials
- Add your Broadbean API credentials
- Add your email service credentials (SendGrid, AWS SES, or SMTP)
- Add job board API keys (Indeed, Totaljobs, CV-Library, etc.)

### 3. Install Dependencies

Using Make (recommended):
```bash
make setup
```

Or manually:
```bash
# Backend
cd backend
npm install
cd ..

# Frontend
cd frontend
npm install
cd ..

# Mobile (optional)
cd mobile
npm install
cd ..
```

### 4. Start Infrastructure Services

This will start all required services (databases, message queue, etc.):

```bash
make start
```

Or with Docker Compose directly:
```bash
docker-compose up -d
```

Wait for all services to be healthy (check with `docker-compose ps`).

### 5. Initialize Database

```bash
# Run migrations
make db-migrate

# Seed with sample data (development only)
make db-seed
```

## Running the Application

### Full Stack (All Services)

```bash
make start
```

This starts:
- PostgreSQL (port 5432)
- MongoDB (port 27017)
- Redis (port 6379)
- Elasticsearch (port 9200)
- RabbitMQ (port 5672, management UI: 15672)
- API Gateway (port 8080)
- Candidate Service (port 8081)
- Client Service (port 8082)
- Job Service (port 8083)
- Other microservices
- Frontend (port 3000)
- Prometheus (port 9090)
- Grafana (port 3002)
- Kibana (port 5601)

### Backend Only

```bash
make start-backend
```

### Frontend Only

```bash
make start-frontend
```

### Development Mode (Hot Reload)

For backend service:
```bash
cd backend/services/candidate-service
npm run dev
```

For frontend:
```bash
cd frontend
npm run dev
```

## Accessing Services

### Web Applications

| Service | URL | Default Credentials |
|---------|-----|---------------------|
| Frontend | http://localhost:3000 | admin@example.com / admin123 |
| API Gateway | http://localhost:8080 | - |
| API Documentation | http://localhost:8080/api/docs | - |
| GraphQL Playground | http://localhost:8080/graphql | - |
| Grafana | http://localhost:3002 | admin / admin |
| Kibana | http://localhost:5601 | - |
| RabbitMQ Management | http://localhost:15672 | admin / dev_password_change_in_prod |

### API Endpoints

#### Authentication
```bash
# Login
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123"
  }'

# Response: { "token": "eyJhbGc...", "refreshToken": "..." }
```

#### Candidates
```bash
# Get all candidates
curl -X GET http://localhost:8080/api/candidates \
  -H "Authorization: Bearer YOUR_TOKEN"

# Create candidate
curl -X POST http://localhost:8080/api/candidates \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@example.com",
    "phone": "+441234567890"
  }'

# Upload CV
curl -X POST http://localhost:8080/api/candidates/123/cv \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/cv.pdf"
```

#### Jobs
```bash
# Get all jobs
curl -X GET http://localhost:8080/api/jobs \
  -H "Authorization: Bearer YOUR_TOKEN"

# Create job
curl -X POST http://localhost:8080/api/jobs \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Software Engineer",
    "clientId": "456",
    "description": "Looking for experienced engineer...",
    "salary": {
      "min": 60000,
      "max": 80000,
      "currency": "GBP"
    },
    "location": "Bristol, UK",
    "type": "permanent"
  }'

# Post job to boards (via Broadbean)
curl -X POST http://localhost:8080/api/jobs/789/post \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "boards": ["indeed", "totaljobs", "cv-library"]
  }'
```

## Development Workflow

### 1. Creating a New Feature

```bash
# Create feature branch
git checkout -b feature/candidate-assessment

# Make changes
# ... code changes ...

# Run tests
make test

# Check code quality
make lint
make typecheck

# Commit changes
git add .
git commit -m "Add candidate assessment feature"

# Push to remote
git push origin feature/candidate-assessment

# Create Pull Request on GitHub
```

### 2. Running Tests

```bash
# All tests
make test

# Specific test suites
make test-unit
make test-integration
make test-e2e

# With coverage
make test-coverage

# Watch mode
cd backend/services/candidate-service
npm run test:watch
```

### 3. Database Operations

```bash
# Create migration
cd backend
npm run migration:create -- AddAssessmentTable

# Edit migration file in data/migrations/postgres/

# Run migration
make db-migrate

# Rollback last migration
npm run migration:down

# Reset database (WARNING: deletes all data)
make db-reset

# Backup database
make db-backup

# Restore database
make db-restore FILE=backups/backup_20250120_120000.sql
```

### 4. Working with Services

```bash
# View logs for all services
make logs

# View logs for specific service
make logs-service SERVICE=candidate-service

# Restart specific service
make restart-service SERVICE=matching-service

# Open shell in service container
make shell-service SERVICE=candidate-service

# Check service health
make health
```

## Common Tasks

### Adding a New Microservice

1. Create service directory:
```bash
mkdir -p backend/services/new-service/src/{controllers,services,models}
```

2. Copy structure from existing service (e.g., candidate-service)

3. Add service to `docker-compose.yml`:
```yaml
new-service:
  build:
    context: ./backend/services/new-service
    dockerfile: Dockerfile
  ports:
    - "8090:8090"
  environment:
    PORT: 8090
    # ... other env vars
```

4. Update API Gateway routing

5. Add service documentation

### Integrating a New Job Board

1. Create integration file:
```bash
touch backend/services/integration-hub/src/integrations/job-boards/newboard.ts
```

2. Implement job board client:
```typescript
export class NewBoardClient {
  async postJob(job: Job): Promise<void> {
    // Implementation
  }

  async fetchApplications(): Promise<Application[]> {
    // Implementation
  }
}
```

3. Register in integration hub

4. Add API credentials to `.env`

5. Test integration

### Customizing Email Templates

1. Edit template files in:
```
backend/services/communication-service/src/templates/email/
```

2. Use template variables:
```html
<p>Dear {{candidateName}},</p>
<p>You have been invited to interview for {{jobTitle}} at {{clientName}}.</p>
```

3. Test template rendering

4. Update documentation

### Adding a New ML Model

1. Train model:
```bash
cd backend/services/matching-service/src/ml/training
python train.py --data /data/training/candidates.csv
```

2. Save model:
```python
model.save('/models/candidate_matcher_v2.h5')
```

3. Update inference code:
```python
model = load_model('/models/candidate_matcher_v2.h5')
```

4. Test model performance

5. Deploy to production

## Troubleshooting

### Services Won't Start

**Problem**: Docker containers fail to start

**Solutions**:
1. Check Docker is running: `docker ps`
2. Check ports aren't already in use: `netstat -an | grep 8080`
3. Check logs: `docker-compose logs`
4. Reset Docker: `make clean && make start`

### Database Connection Errors

**Problem**: "Connection refused" or timeout errors

**Solutions**:
1. Verify database is running: `docker-compose ps postgres`
2. Check credentials in `.env`
3. Wait for database to be healthy: `docker-compose ps`
4. Check network: `docker network inspect recruitment_recruitment-network`

### API Returns 401 Unauthorized

**Problem**: API requests fail with authentication error

**Solutions**:
1. Ensure you're including the JWT token in Authorization header
2. Check token hasn't expired (default: 24h)
3. Refresh token or re-login
4. Verify JWT_SECRET matches between services

### Bullhorn Sync Failing

**Problem**: Data not syncing with Bullhorn

**Solutions**:
1. Verify API credentials in `.env`
2. Check rate limits (Bullhorn has strict limits)
3. Review logs: `make logs-service SERVICE=integration-hub`
4. Test Bullhorn connection manually
5. Check webhook secret matches

### Slow Matching Performance

**Problem**: Candidate-job matching takes too long

**Solutions**:
1. Check Elasticsearch is running and indexed
2. Rebuild indices: `make reindex-elasticsearch`
3. Verify ML model is loaded
4. Check Redis cache is working
5. Review matching algorithm parameters

### Frontend Build Errors

**Problem**: Next.js build fails

**Solutions**:
1. Clear `.next` directory: `rm -rf frontend/.next`
2. Reinstall dependencies: `cd frontend && rm -rf node_modules && npm install`
3. Check TypeScript errors: `cd frontend && npm run typecheck`
4. Verify environment variables are set

### Tests Failing

**Problem**: Test suite fails

**Solutions**:
1. Ensure test database is clean: `npm run test:db:reset`
2. Check test environment variables
3. Run tests individually to isolate issue
4. Check for port conflicts
5. Update snapshots if UI changed: `npm run test:update-snapshots`

## Getting Help

If you encounter issues not covered here:

1. **Check the documentation**: See `docs/` directory
2. **Review logs**: `make logs`
3. **Search existing issues**: GitHub Issues
4. **Contact support**:
   - Email: support@proactivepeople.com
   - Phone: 0117 9377 199
5. **Create an issue**: Provide logs, steps to reproduce, expected vs actual behavior

## Next Steps

Now that you have the system running:

1. **Explore the UI**: http://localhost:3000
2. **Review API docs**: http://localhost:8080/api/docs
3. **Read architecture docs**: [ARCHITECTURE.md](./ARCHITECTURE.md)
4. **Set up integrations**: Configure Bullhorn, Broadbean, job boards
5. **Customize workflows**: Adapt recruitment pipeline to your process
6. **Train ML models**: Use your historical data
7. **Configure notifications**: Set up email templates and SMS
8. **Set up monitoring**: Configure Grafana dashboards
9. **Plan deployment**: Review deployment guide in `docs/technical/`

Happy coding! 🚀
