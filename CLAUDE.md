# ProActive People - Recruitment Automation System

## Project Overview
Enterprise recruitment automation platform for ProActive People, Bristol's leading independent recruitment agency. Full-stack microservices architecture with AI-powered candidate matching and workflow automation.

## Key Technologies
- **Backend**: Node.js (NestJS), Python (FastAPI)
- **Frontend**: Next.js 14, React 18, TypeScript, Tailwind CSS
- **Mobile**: React Native
- **Databases**: PostgreSQL, MongoDB, Redis, Elasticsearch
- **AI/ML**: TensorFlow, spaCy, Hugging Face
- **Infrastructure**: Docker, Kubernetes, RabbitMQ/Kafka
- **Cloud**: AWS/Azure/GCP ready

## Core System Components

### 14 Microservices
1. API Gateway (auth, routing, rate limiting)
2. Candidate Service (CV parsing, profiling)
3. Client Service (company profiles, CRM)
4. Job Service (postings, applications)
5. Matching Engine (AI-powered matching)
6. Workflow Service (pipeline automation)
7. Scheduling Service (interview booking)
8. Communication Service (email/SMS/WhatsApp)
9. Placement Service (placement tracking)
10. Finance Service (invoicing, commissions)
11. Analytics Service (KPIs, predictive analytics)
12. Integration Hub (Bullhorn, Broadbean)
13. Notification Service (WebSocket real-time)
14. Search Service (Elasticsearch)

### Critical Integrations
- **Bullhorn ATS**: Bidirectional real-time sync (candidates, jobs, clients, placements)
- **Broadbean**: Multi-platform job posting (Indeed, Totaljobs, CV-Library, Reed, etc.)
- **Job Boards**: Direct API integrations with major platforms
- **Email/Calendar**: SendGrid/AWS SES, Google Calendar/Outlook sync

## Business Domains
- Sales Jobs (Business Development, Telesales, Field Sales, Fundraising)
- Technical Jobs (IT Support, Cloud, Software Engineering)
- Contact Centre (Customer Service, Telesales, Charity Fundraising)
- Accountancy (Corporate Tax, Audit, General Practice)
- Commercial (Management, Office Support, Engineering, PR)

## Recruitment Pipeline Stages
Sourced → Screening → Submitted → Interview → Offer → Placed → Follow-up

## Project Structure
```
recruitment-automation-system/
├── backend/services/     # 14 microservices
├── backend/shared/       # Shared libraries
├── frontend/             # Next.js web app
├── mobile/               # React Native app
├── data/                 # DB migrations/seeds
├── docs_root/            # Complete documentation (merged from docs/ and docs_project/)
├── prompts/              # LLM prompt templates (JSON format)
└── tests/                # System-wide tests
```

## Code Standards & Best Practices

### Prompt Management

**IMPORTANT**: All LLM prompts MUST be stored in the `prompts/` directory as JSON files, never hardcoded in source code.

**Prompt File Format:**
```json
{
  "version": "1.0",
  "name": "Descriptive Name",
  "description": "What this prompt does",
  "model": "model-name",
  "temperature": 0.3,
  "max_tokens": 200,
  "system_prompt": "The actual prompt text with {variable} placeholders",
  "variables": {
    "variable": "Description of what gets substituted"
  },
  "output_format": {
    "type": "json|text",
    "schema": {}
  }
}
```

**Benefits:**
- Version control for prompts
- Easy A/B testing and experimentation
- Centralized prompt management
- Separation of concerns (logic vs. prompts)
- Documentation of prompt purpose and variables

**Example:** `prompts/ai_router_classification.json` for query classification

## Development Commands
```bash
make setup              # Initialize environment
make start              # Start all services
make test               # Run test suite
make lint               # Code quality checks
make deploy-staging     # Deploy to staging
```

## Local Ports
- Web UI: http://localhost:3000
- API Gateway: http://localhost:8080
- Admin Portal: http://localhost:3001
- Grafana: http://localhost:3002
- Swagger/API Docs: http://localhost:8080/api/docs

## Authentication
All API endpoints use JWT bearer tokens. RBAC implemented across all services.

## Performance Targets
- API Response: <200ms (95th percentile)
- Matching Algorithm: <2s for 10,000 candidates
- Job Posting: <5s to all platforms
- Throughput: 1000+ req/s

## Security & Compliance
- GDPR compliant (data retention, right to erasure)
- SOC 2, ISO 27001 certified
- AES-256 encryption at rest, TLS 1.3 in transit
- Audit trails on all critical operations

## Project Phase (Current)
Phase 2 (Q2 2025): Integrations - Bullhorn sync, Broadbean integration, CV parsing

## Contact
ProActive People Ltd.
📞 0117 9377 199 | 📧 info@proactivepeople.com
