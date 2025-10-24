# ProActive People - Universal Automation System Architecture

## Executive Summary

This document outlines the comprehensive architecture for a universal automation system designed for ProActive People, a Bristol-based recruitment agency with 20+ years of experience specializing in multi-sector recruitment.

## Business Analysis

### Core Business Operations

#### 1. **Job Categories (Candidate-Facing)**
- **Sales Jobs**: Business Development, Telesales, Field Sales, Recruitment Sales, Call Centre Sales, Fundraising
- **Technical Jobs**: IT Support, Cloud Networking, Hardware/Software Engineering, Development, Analysis, Project Management
- **Contact Centre Jobs**: Customer Service Advisors, Telesales Executives, Charity Fundraisers, Claims Handlers
- **Accountancy Jobs**: Corporate Tax, Audit, General Practice Accountancy
- **Commercial Jobs**: Management, Office Support, Business Support, PR, Account Directors, Claims Adjusters, Engineering

#### 2. **Service Offerings** (ProActive Solutions Group - Complete Talent Solutions)

**Core Recruitment Services:**
- **Permanent Placements**: Full-time positions with free replacement guarantee
- **Temporary Placements**: Short-term staffing solutions
- **Contract Roles**: Fixed-term project-based positions
- **Work From Home**: Remote position placements

**Additional Professional Services:**
- **Proactive Training**: Custom sales & customer service training, coaching, upskilling programs (Led by Stuart Pearce, published author)
- **Proactive Wellbeing**: Workplace health, employee support, stress management, return-to-work programs (Led by Emma Jane)
- **Proactive Assessment**: Remote employee profiling, psychometric testing, team fit assessment, bespoke assessments
- **Proactive Contact Centre**: Specialist contact centre recruitment, setup consultancy, expansion, performance turnaround (25+ years experience, Contact Centre Forum member)

#### 3. **Technology Stack (Current)**
- **Bullhorn**: ATS (Applicant Tracking System) - Primary recruitment CRM
- **Broadbean**: Job board aggregator and multi-posting platform
- **Job Board Partnerships**: Jobsite, Totaljobs, CV-Library, Jobserve, Reed
- **Joomla**: Website CMS

#### 4. **Core Business Processes**
1. **Client Acquisition & Management**
   - Client onboarding
   - Requirements gathering
   - Job specification creation
   - Contract negotiation
   - Ongoing relationship management

2. **Candidate Management**
   - CV registration and parsing
   - Candidate profiling and scoring
   - Skills assessment
   - Interview scheduling
   - Candidate tracking through pipeline

3. **Recruitment Workflow**
   - Job posting (multi-platform)
   - Candidate sourcing
   - CV screening and scoring
   - Interview coordination
   - Feedback collection (client & candidate)
   - Placement and onboarding
   - Rebate/replacement management

4. **Quality Assurance**
   - Candidate vetting process
   - Pre-screening
   - Assessment services
   - Employee profiling
   - Performance tracking

### Key Business Departments

1. **Sales & Business Development**
   - Client acquisition
   - Market research
   - Competitive analysis
   - Pricing strategy

2. **Recruitment Operations**
   - Candidate sourcing
   - Screening & interviews
   - Placement coordination
   - Relationship management

3. **Finance & Administration**
   - Invoicing (from start date)
   - Rebate management
   - Payroll (for temps/contractors)
   - Financial reporting

4. **Marketing**
   - Job board management
   - Social media presence
   - SEO/SEM
   - Email campaigns
   - Brand management

5. **HR & Compliance**
   - Employment law compliance
   - Data protection (GDPR)
   - Right to work checks
   - Contract management

6. **IT & Systems**
   - ATS maintenance
   - Website management
   - Data integration
   - Security

## System Architecture Design

### Architecture Principles

1. **Microservices-Based**: Loosely coupled services for scalability
2. **Event-Driven**: Real-time updates across the system
3. **API-First**: All services expose RESTful APIs
4. **Cloud-Native**: Containerized deployment with orchestration
5. **Data-Centric**: Single source of truth with data lake architecture
6. **AI-Powered**: Machine learning for matching, scoring, and predictions

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Presentation Layer                           │
├─────────────┬──────────────┬──────────────┬────────────────────┤
│   Web UI    │  Mobile App  │  Admin Portal│  Client Portal     │
└─────────────┴──────────────┴──────────────┴────────────────────┘
                              │
┌─────────────────────────────▼─────────────────────────────────┐
│                    API Gateway & Auth Layer                     │
│          (Kong/AWS API Gateway + OAuth2/JWT)                    │
└─────────────────────────────┬─────────────────────────────────┘
                              │
┌─────────────────────────────▼─────────────────────────────────┐
│                   Business Logic Layer                          │
│                   (Microservices)                               │
├──────────────┬──────────────┬──────────────┬─────────────────┤
│   Candidate  │    Client    │     Job      │   Placement     │
│   Service    │   Service    │   Service    │   Service       │
├──────────────┼──────────────┼──────────────┼─────────────────┤
│   Matching   │  Scheduling  │   Workflow   │   Finance       │
│   Engine     │   Service    │   Engine     │   Service       │
├──────────────┼──────────────┼──────────────┼─────────────────┤
│ Notification │  Analytics   │   Reporting  │   Integration   │
│   Service    │   Service    │   Service    │   Hub           │
└──────────────┴──────────────┴──────────────┴─────────────────┘
                              │
┌─────────────────────────────▼─────────────────────────────────┐
│                      Data Layer                                 │
├──────────────┬──────────────┬──────────────┬─────────────────┤
│  PostgreSQL  │   MongoDB    │   Redis      │  Elasticsearch  │
│  (Relational)│ (Documents)  │  (Cache)     │  (Search)       │
└──────────────┴──────────────┴──────────────┴─────────────────┘
                              │
┌─────────────────────────────▼─────────────────────────────────┐
│                   Integration Layer                             │
├──────────────┬──────────────┬──────────────┬─────────────────┤
│   Bullhorn   │  Broadbean   │  Job Boards  │   Email         │
│   API        │   API        │  APIs        │   Service       │
└──────────────┴──────────────┴──────────────┴─────────────────┘
```

### Core Microservices

#### 1. Candidate Management Service
- CV parsing and storage
- Candidate profiling
- Skills taxonomy management
- Availability tracking
- Communication history
- Document management
- Assessment results

#### 2. Client Management Service
- Client onboarding
- Company profiles
- Contact management
- Contract templates
- Requirements tracking
- Billing preferences
- Relationship scoring

#### 3. Job Management Service
- Job requisition creation
- Multi-platform posting (via Broadbean)
- Job board synchronization
- Job status tracking
- Application management
- Job analytics

#### 4. Matching Engine (AI/ML)
- Candidate-job matching algorithm
- Skills matching
- Salary expectation matching
- Location/commute analysis
- Cultural fit scoring
- Availability alignment
- Success prediction

#### 5. Workflow Engine
- Recruitment pipeline automation
- Stage progression rules
- Task automation
- Approval workflows
- SLA monitoring
- Escalation rules

#### 6. Scheduling Service
- Interview scheduling
- Calendar integration (Google/Outlook)
- Automated reminders
- Rescheduling logic
- Availability management
- Timezone handling

#### 7. Communication Service
- Email templates
- SMS notifications
- WhatsApp integration
- In-app messaging
- Communication tracking
- Multi-channel orchestration

#### 8. Finance Service
- Invoice generation
- Rebate calculation
- Payment tracking
- Payroll integration (temps/contractors)
- Commission calculation
- Financial reporting

#### 9. Analytics & Reporting Service
- KPI dashboards
- Recruitment metrics
- Time-to-fill analytics
- Source effectiveness
- Revenue reporting
- Predictive analytics

#### 10. Integration Hub
- Bullhorn bidirectional sync
- Broadbean job posting
- Job board API integrations
- Email service (SendGrid/AWS SES)
- Document storage (S3/Azure Blob)
- Calendar APIs
- Background check services
- Reference checking platforms

### Cross-Cutting Concerns

1. **Authentication & Authorization**
   - Role-based access control (RBAC)
   - SSO integration
   - API key management
   - Multi-tenancy support

2. **Logging & Monitoring**
   - Centralized logging (ELK Stack)
   - Application Performance Monitoring (APM)
   - Error tracking (Sentry)
   - Uptime monitoring

3. **Data Governance**
   - GDPR compliance engine
   - Data retention policies
   - Audit trails
   - Data encryption (at rest & in transit)

4. **Event Bus**
   - RabbitMQ / Apache Kafka
   - Event-driven architecture
   - Pub/Sub patterns
   - Event sourcing for critical operations

## Technology Stack Recommendations

### Backend
- **Language**: Python (FastAPI/Django) or Node.js (NestJS)
- **API**: GraphQL + REST
- **Authentication**: OAuth2/JWT with Auth0 or Keycloak
- **Message Queue**: RabbitMQ or Apache Kafka
- **Task Queue**: Celery (Python) or Bull (Node.js)

### Frontend
- **Framework**: React with TypeScript or Next.js
- **State Management**: Redux Toolkit or Zustand
- **UI Library**: Material-UI or Ant Design
- **Mobile**: React Native or Flutter

### Databases
- **Primary DB**: PostgreSQL 15+
- **Document Store**: MongoDB (for CVs, documents)
- **Cache**: Redis 7+
- **Search**: Elasticsearch 8+
- **Time-Series**: TimescaleDB (for analytics)

### AI/ML
- **Framework**: TensorFlow or PyTorch
- **NLP**: spaCy, Hugging Face Transformers
- **CV Parsing**: Sovren, Textkernel, or custom ML model
- **Matching**: Custom neural network or Sentence-BERT

### Infrastructure
- **Container**: Docker
- **Orchestration**: Kubernetes or AWS ECS
- **CI/CD**: GitHub Actions or GitLab CI
- **Cloud**: AWS, Azure, or GCP
- **IaC**: Terraform

### DevOps & Monitoring
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Monitoring**: Prometheus + Grafana
- **APM**: New Relic or Datadog
- **Error Tracking**: Sentry

## Data Models

### Core Entities

1. **Candidate**
   - Personal information
   - Contact details
   - CV/Resume (parsed & raw)
   - Skills matrix
   - Work history
   - Education
   - Certifications
   - Preferences (salary, location, job type)
   - Availability
   - Assessment scores
   - Communication history

2. **Client**
   - Company information
   - Industry sector
   - Contacts (multiple)
   - Billing details
   - Contract terms
   - Preferences
   - Relationship score
   - Historical placements

3. **Job/Vacancy**
   - Job title & description
   - Client reference
   - Required skills
   - Salary range
   - Location
   - Job type (permanent/temp/contract)
   - Status
   - Applications
   - Posting platforms
   - Hiring manager

4. **Application/Submission**
   - Candidate reference
   - Job reference
   - Stage (applied, screening, interview, offer, placed)
   - Status
   - Submission date
   - Consultant notes
   - Interview feedback
   - Rejection reason

5. **Placement**
   - Candidate reference
   - Client reference
   - Job reference
   - Start date
   - End date (if temp/contract)
   - Salary/rate
   - Fee structure
   - Rebate period
   - Status
   - Invoice details

### Relationships & Cross-References

```
Client 1:N Jobs
Job 1:N Applications
Candidate 1:N Applications
Application N:1 Job
Application N:1 Candidate
Placement 1:1 Application
Placement N:1 Client
Placement N:1 Candidate
```

## Automation Opportunities

### High-Priority Automations

1. **Intelligent CV Parsing & Enrichment**
   - Automatic skills extraction
   - Experience level calculation
   - Salary expectation inference
   - LinkedIn profile enrichment

2. **Smart Job-Candidate Matching**
   - Automated candidate shortlisting
   - Scoring and ranking
   - Push notifications to consultants
   - Email campaigns to suitable candidates

3. **Multi-Platform Job Posting**
   - One-click posting to all job boards
   - Automatic job description optimization
   - Platform-specific formatting
   - Performance tracking

4. **Interview Scheduling Automation**
   - AI-powered time slot suggestions
   - Automated calendar invitations
   - Reminder sequences
   - Rescheduling workflows

5. **Communication Automation**
   - Personalized email sequences
   - SMS reminders
   - Status update notifications
   - Drip campaigns

6. **Document Generation**
   - Contract auto-generation
   - Offer letters
   - Job descriptions
   - Client proposals

7. **Reporting & Analytics**
   - Automated daily/weekly reports
   - KPI dashboards
   - Consultant performance tracking
   - Revenue forecasting

8. **Compliance & Audit**
   - Right-to-work verification
   - GDPR consent management
   - Data retention automation
   - Audit trail generation

9. **Financial Automation**
   - Invoice generation on start dates
   - Rebate period tracking
   - Commission calculations
   - Payment reminders

10. **Feedback Loop Automation**
    - Post-interview feedback requests
    - Post-placement surveys
    - Client satisfaction tracking
    - Continuous improvement insights

## Integration Strategy

### Bullhorn Integration
- **Type**: Bidirectional sync
- **Method**: REST API
- **Frequency**: Real-time webhooks + scheduled sync
- **Data Flow**:
  - Push: New candidates, applications, notes
  - Pull: Job updates, client data, placements
- **Conflict Resolution**: Bullhorn as source of truth (initially)

### Broadbean Integration
- **Type**: Job posting & application ingestion
- **Method**: API + XML feeds
- **Frequency**: Real-time job posting, hourly application sync
- **Data Flow**: Jobs out, applications in

### Job Board Integrations
- Individual APIs for premium partners
- Broadbean for bulk posting
- Application tracking pixels
- Performance analytics

## Phased Implementation Roadmap

### Phase 1: Foundation (Months 1-3)
- Core infrastructure setup
- Database design & implementation
- API gateway & authentication
- Candidate Management Service
- Client Management Service
- Job Management Service
- Basic UI (candidate & job listing)

### Phase 2: Integration (Months 4-6)
- Bullhorn bidirectional sync
- Broadbean integration
- CV parsing engine
- Document storage
- Email service integration
- Basic workflow engine

### Phase 3: Intelligence (Months 7-9)
- Matching algorithm (ML)
- Scheduling service
- Advanced workflow automation
- Analytics dashboard
- Reporting engine

### Phase 4: Optimization (Months 10-12)
- Mobile app
- Advanced AI features
- Predictive analytics
- Performance optimization
- User feedback integration

### Phase 5: Scale (Ongoing)
- Advanced integrations
- Industry-specific features
- White-label capability
- API for third parties
- Continuous improvement

## Success Metrics

### Operational KPIs
- Time-to-fill reduction (target: 30% improvement)
- Candidate-job match accuracy (target: 85%+)
- Interview-to-placement ratio (target: 1:3)
- Client satisfaction score (target: 4.5/5)
- Consultant productivity (placements per month)

### Technical KPIs
- API response time (target: <200ms)
- System uptime (target: 99.9%)
- Data sync latency (target: <5 minutes)
- Error rate (target: <0.1%)

### Business KPIs
- Revenue per consultant
- Cost per hire reduction
- Rebate/replacement rate reduction
- Client retention rate
- Candidate database growth

## Risk Management

### Technical Risks
- Bullhorn API limitations → Mitigation: Queue-based sync with retry logic
- Data migration complexity → Mitigation: Phased migration with rollback plan
- Performance at scale → Mitigation: Horizontal scaling, caching strategy

### Business Risks
- User adoption resistance → Mitigation: Change management, training, gradual rollout
- Data quality issues → Mitigation: Data validation, cleansing pipeline
- Compliance violations → Mitigation: Built-in compliance checks, audit trails

## Conclusion

This architecture provides a comprehensive, scalable foundation for automating ProActive People's recruitment operations. The microservices-based approach ensures flexibility, maintainability, and the ability to evolve with business needs while maintaining seamless integration with existing tools like Bullhorn and Broadbean.
