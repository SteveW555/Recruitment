# ProActive People - Universal Recruitment Automation System

**Enterprise-grade recruitment automation platform for ProActive People, Bristol's leading independent recruitment agency.**

## Overview

This system provides comprehensive automation across all aspects of recruitment operations, from candidate sourcing and client management to job matching, placement, and financial operations. Built on a microservices architecture with AI-powered matching and workflow automation.

### Key Features

- **Intelligent Candidate Management**: CV parsing, skill extraction, automated profiling
- **Client Relationship Management**: 360° view, requirements tracking, relationship scoring
- **AI-Powered Job Matching**: Machine learning algorithms for optimal candidate-job pairing
- **Automated Workflows**: Streamlined recruitment pipeline with automated stage progressions
- **Multi-Platform Job Posting**: One-click posting to all major job boards via Broadbean
- **Smart Scheduling**: AI-powered interview scheduling with calendar integration
- **Financial Automation**: Invoice generation, rebate tracking, commission calculations
- **Real-time Analytics**: Comprehensive dashboards, KPI tracking, predictive analytics
- **Seamless Integrations**: Bullhorn, Broadbean, job boards, email, calendars

### Business Domains

- **Sales Jobs**: Business Development, Telesales, Field Sales, Fundraising
- **Technical Jobs**: IT Support, Cloud, Software Engineering, Development
- **Contact Centre**: Customer Service, Telesales, Charity Fundraising
- **Accountancy**: Corporate Tax, Audit, General Practice
- **Commercial**: Management, Office Support, Engineering, PR

## Quick Start

### Prerequisites

- Docker & Docker Compose 20+
- Node.js 18+ (for local development)
- Python 3.11+ (for ML services)
- PostgreSQL 15+
- MongoDB 6+
- Redis 7+
- Elasticsearch 8+

### Installation

```bash
# Clone the repository
git clone https://github.com/proactive-people/recruitment-automation.git
cd recruitment-automation

# Copy environment configuration
cp .env.example .env

# Edit .env with your configuration
nano .env

# Start all services
make setup
make start

# Access the application
# Web UI: http://localhost:3000
# API Gateway: http://localhost:8080
# Admin Portal: http://localhost:3001
```

### Development Mode

```bash
# Start specific services
make start-backend
make start-frontend
make start-mobile

# Run tests
make test

# View logs
make logs SERVICE=candidate-service

# Stop all services
make stop
```

## Architecture

### System Overview

```
┌─────────────────────────────────────────────┐
│         Presentation Layer                   │
│  Web UI | Mobile App | Client Portal        │
└─────────────┬───────────────────────────────┘
              │
┌─────────────▼───────────────────────────────┐
│          API Gateway & Auth                  │
└─────────────┬───────────────────────────────┘
              │
┌─────────────▼───────────────────────────────┐
│        Microservices Layer                   │
│  14 specialized services (see below)         │
└─────────────┬───────────────────────────────┘
              │
┌─────────────▼───────────────────────────────┐
│           Data Layer                         │
│  PostgreSQL | MongoDB | Redis | ES          │
└─────────────────────────────────────────────┘
```

### Core Microservices

1. **API Gateway**: Authentication, routing, rate limiting
2. **Candidate Service**: CV management, profiling, skills tracking
3. **Client Service**: Company profiles, contacts, requirements
4. **Job Service**: Job postings, applications, board management
5. **Matching Engine**: AI-powered candidate-job matching
6. **Workflow Service**: Pipeline automation, stage progression
7. **Scheduling Service**: Interview booking, calendar sync
8. **Communication Service**: Email, SMS, WhatsApp, notifications
9. **Placement Service**: Placement tracking, onboarding
10. **Finance Service**: Invoicing, payments, commissions
11. **Analytics Service**: KPIs, reports, predictive analytics
12. **Integration Hub**: Bullhorn, Broadbean, job boards
13. **Notification Service**: Real-time WebSocket notifications
14. **Search Service**: Elasticsearch-powered search

### Technology Stack

**Backend**: Node.js (NestJS) / Python (FastAPI)
**Frontend**: Next.js 14, React 18, TypeScript, Tailwind CSS
**Mobile**: React Native, TypeScript
**Databases**: PostgreSQL, MongoDB, Redis, Elasticsearch
**Message Queue**: RabbitMQ / Apache Kafka
**AI/ML**: Python, TensorFlow, spaCy, Hugging Face
**Infrastructure**: Docker, Kubernetes, Terraform
**Cloud**: AWS / Azure / GCP
**Monitoring**: ELK Stack, Prometheus, Grafana

## Project Structure

```
recruitment-automation-system/
├── backend/              # Backend microservices
│   ├── services/         # 14 microservices
│   ├── shared/           # Shared libraries
│   └── infrastructure/   # IaC and K8s configs
├── frontend/             # Next.js web application
├── mobile/               # React Native mobile app
├── data/                 # Database migrations and seeds
├── docs/                 # Comprehensive documentation
├── scripts/              # Utility scripts
├── tests/                # System-wide tests
└── config/               # Environment configurations
```

See [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) for detailed structure.

## Key Workflows

### Candidate Journey

1. **Registration**: CV upload → Automated parsing → Profile creation
2. **Enrichment**: LinkedIn integration → Skills extraction → Assessment
3. **Matching**: AI algorithm → Job recommendations → Consultant review
4. **Application**: Submission → Screening → Interview scheduling
5. **Placement**: Offer → Onboarding → Post-placement tracking

### Client Workflow

1. **Onboarding**: Company profile → Contact details → Contract setup
2. **Job Creation**: Requirement gathering → Job description → Approval
3. **Posting**: Multi-platform posting → Application tracking
4. **Selection**: Candidate shortlist → Interview coordination → Feedback
5. **Placement**: Offer management → Start date → Invoice generation

### Recruitment Pipeline Stages

1. **Sourced**: Candidate identified
2. **Screening**: Initial CV review
3. **Submitted**: Sent to client
4. **Interview**: Scheduled or completed
5. **Offer**: Extended to candidate
6. **Placed**: Started employment
7. **Follow-up**: Post-placement check-in

## Integrations

### Bullhorn ATS
- **Type**: Bidirectional sync
- **Frequency**: Real-time webhooks + hourly sync
- **Data**: Candidates, jobs, clients, placements, notes
- **Documentation**: [docs/integrations/bullhorn-integration.md](./docs/integrations/bullhorn-integration.md)

### Broadbean
- **Type**: Job posting & application ingestion
- **Frequency**: Real-time posting, hourly applications
- **Boards**: Indeed, Totaljobs, CV-Library, Reed, Jobsite, Jobserve
- **Documentation**: [docs/integrations/broadbean-integration.md](./docs/integrations/broadbean-integration.md)

### Job Boards
- Direct API integrations for premium partners
- Application tracking and analytics
- Performance metrics per board

### Email & Calendar
- SendGrid / AWS SES for transactional emails
- Google Calendar / Outlook integration
- Automated reminders and scheduling

## API Documentation

Comprehensive API documentation is available at:
- **Swagger UI**: http://localhost:8080/api/docs
- **GraphQL Playground**: http://localhost:8080/graphql
- **OpenAPI Spec**: [docs/api/openapi.yaml](./docs/api/openapi.yaml)

### Authentication

All API requests require authentication via JWT tokens:

```bash
# Login
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Use token in subsequent requests
curl -X GET http://localhost:8080/api/candidates \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Configuration

### Environment Variables

Key environment variables (see `.env.example` for full list):

```env
# Application
NODE_ENV=development
PORT=8080

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=recruitment
POSTGRES_USER=admin
POSTGRES_PASSWORD=secret

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Message Queue
RABBITMQ_URL=amqp://localhost:5672

# External APIs
BULLHORN_API_KEY=your_key
BULLHORN_API_SECRET=your_secret
BROADBEAN_API_KEY=your_key

# Email
SENDGRID_API_KEY=your_key

# Auth
JWT_SECRET=your_secret
JWT_EXPIRY=24h

# ML Models
MODEL_PATH=/models
```

## Development

### Code Quality

```bash
# Linting
make lint

# Format code
make format

# Type checking
make typecheck

# Run all checks
make check
```

### Testing

```bash
# Unit tests
make test-unit

# Integration tests
make test-integration

# E2E tests
make test-e2e

# All tests with coverage
make test-coverage
```

### Database Migrations

```bash
# Create migration
npm run migration:create -- AddCandidatesTable

# Run migrations
npm run migration:up

# Rollback migration
npm run migration:down
```

## Deployment

### Staging

```bash
# Deploy to staging
make deploy-staging

# Check deployment status
make status-staging

# View logs
make logs-staging
```

### Production

```bash
# Create release tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# Deploy (requires approval)
make deploy-production

# Rollback if needed
make rollback-production
```

## Monitoring & Observability

### Dashboards

- **Grafana**: http://localhost:3002 (Metrics and system health)
- **Kibana**: http://localhost:5601 (Logs and search)
- **Jaeger**: http://localhost:16686 (Distributed tracing)

### Health Checks

```bash
# Check all services
make health

# Check specific service
curl http://localhost:8080/health/candidate-service
```

### Logs

```bash
# View all logs
make logs

# View specific service logs
make logs SERVICE=matching-service

# Follow logs
make logs-follow SERVICE=workflow-service
```

## Performance

### Benchmarks

- API Response Time: <200ms (95th percentile)
- Matching Algorithm: <2s for 10,000 candidates
- Job Posting: <5s to all platforms
- System Throughput: 1000+ requests/second

### Optimization Tips

1. Enable Redis caching for frequently accessed data
2. Use Elasticsearch for complex searches
3. Implement pagination for large datasets
4. Use CDN for static assets
5. Enable HTTP/2 and compression

## Security

### Best Practices

- All data encrypted at rest (AES-256) and in transit (TLS 1.3)
- Role-based access control (RBAC) on all endpoints
- Regular security scans via CI/CD
- GDPR-compliant data handling
- Audit trails for all critical operations
- Regular penetration testing

### Compliance

- **GDPR**: Data retention policies, right to erasure, consent management
- **SOC 2**: Security controls, audit logs, access management
- **ISO 27001**: Information security management

## Troubleshooting

### Common Issues

**Issue**: Services fail to start
**Solution**: Check Docker is running, ports are available

**Issue**: Database connection errors
**Solution**: Verify database credentials in `.env`

**Issue**: Bullhorn sync failing
**Solution**: Check API credentials and rate limits

**Issue**: Slow matching performance
**Solution**: Rebuild Elasticsearch indices

See [docs/technical/troubleshooting.md](./docs/technical/troubleshooting.md) for more.

## Contributing

We welcome contributions! Please read [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

### Development Workflow

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Code Review Process

- All PRs require 2 approvals
- All tests must pass
- Code coverage must not decrease
- Documentation must be updated

## Support

- **Email**: support@proactivepeople.com
- **Phone**: 0117 9377 199 / 01934 319 490
- **Documentation**: [docs/](./docs/)
- **Issue Tracker**: GitHub Issues

## Roadmap

### Phase 1 (Q1 2025) - Foundation ✓
- Core microservices
- Database setup
- Basic UI

### Phase 2 (Q2 2025) - Integration
- Bullhorn sync
- Broadbean integration
- CV parsing

### Phase 3 (Q3 2025) - Intelligence
- AI matching algorithm
- Workflow automation
- Analytics dashboard

### Phase 4 (Q4 2025) - Optimization
- Mobile app
- Performance tuning
- Advanced features

## License

Proprietary - ProActive People Ltd. All rights reserved.

## Team

- **Project Lead**: [Name]
- **Backend Lead**: [Name]
- **Frontend Lead**: [Name]
- **ML Engineer**: [Name]
- **DevOps Lead**: [Name]

---

**Built with ❤️ by ProActive People**

**Bristol's Foremost Independent Recruitment Agency**

📞 0117 9377 199 | 📧 info@proactivepeople.com | 🌐 www.proactivepeople.com
