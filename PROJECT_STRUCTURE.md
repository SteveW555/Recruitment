# ProActive People - Universal Automation System
## Complete Project Directory Structure

```
recruitment-automation-system/
│
├── README.md                          # Project overview and quick start
├── ARCHITECTURE.md                    # Detailed architecture documentation
├── CONTRIBUTING.md                    # Contribution guidelines
├── LICENSE                            # Software license
├── .gitignore                         # Git ignore rules
├── docker-compose.yml                 # Local development environment
├── docker-compose.prod.yml            # Production deployment
├── Makefile                           # Common commands and shortcuts
│
├── docs/                              # Comprehensive documentation
│   ├── api/                          # API documentation
│   │   ├── openapi.yaml              # OpenAPI 3.0 specification
│   │   ├── graphql-schema.graphql    # GraphQL schema
│   │   ├── webhooks.md               # Webhook documentation
│   │   └── authentication.md         # Auth flows and security
│   ├── architecture/                 # Architecture diagrams
│   │   ├── system-overview.png
│   │   ├── microservices-diagram.png
│   │   ├── data-flow.png
│   │   ├── deployment-diagram.png
│   │   └── sequence-diagrams/
│   ├── business/                     # Business process documentation
│   │   ├── recruitment-workflow.md
│   │   ├── client-onboarding.md
│   │   ├── candidate-journey.md
│   │   ├── placement-process.md
│   │   └── financial-flows.md
│   ├── technical/                    # Technical guides
│   │   ├── development-setup.md
│   │   ├── deployment-guide.md
│   │   ├── testing-strategy.md
│   │   ├── coding-standards.md
│   │   └── troubleshooting.md
│   ├── integrations/                 # Integration guides
│   │   ├── bullhorn-integration.md
│   │   ├── broadbean-integration.md
│   │   ├── job-boards.md
│   │   └── third-party-apis.md
│   ├── user-guides/                  # End-user documentation
│   │   ├── consultant-manual.pdf
│   │   ├── admin-guide.pdf
│   │   ├── client-portal-guide.pdf
│   │   └── video-tutorials/
│   └── compliance/                   # Legal and compliance
│       ├── gdpr-compliance.md
│       ├── data-retention.md
│       ├── security-policies.md
│       └── audit-procedures.md
│
├── backend/                           # Backend services
│   ├── README.md
│   ├── package.json                  # Root dependencies (if monorepo)
│   ├── tsconfig.json                 # TypeScript configuration
│   ├── .eslintrc.js                  # Linting rules
│   ├── .prettierrc                   # Code formatting
│   │
│   ├── services/                     # Microservices
│   │   ├── api-gateway/              # API Gateway & Auth
│   │   │   ├── src/
│   │   │   │   ├── index.ts
│   │   │   │   ├── middleware/
│   │   │   │   │   ├── auth.ts
│   │   │   │   │   ├── rate-limit.ts
│   │   │   │   │   └── logging.ts
│   │   │   │   ├── routes/
│   │   │   │   └── config/
│   │   │   ├── tests/
│   │   │   ├── Dockerfile
│   │   │   ├── package.json
│   │   │   └── README.md
│   │   │
│   │   ├── candidate-service/        # Candidate Management
│   │   │   ├── src/
│   │   │   │   ├── controllers/
│   │   │   │   │   ├── candidate.controller.ts
│   │   │   │   │   ├── cv.controller.ts
│   │   │   │   │   ├── skills.controller.ts
│   │   │   │   │   └── assessment.controller.ts
│   │   │   │   ├── services/
│   │   │   │   │   ├── candidate.service.ts
│   │   │   │   │   ├── cv-parser.service.ts
│   │   │   │   │   ├── enrichment.service.ts
│   │   │   │   │   └── profile.service.ts
│   │   │   │   ├── models/
│   │   │   │   │   ├── candidate.model.ts
│   │   │   │   │   ├── cv.model.ts
│   │   │   │   │   ├── skill.model.ts
│   │   │   │   │   └── assessment.model.ts
│   │   │   │   ├── repositories/
│   │   │   │   ├── validators/
│   │   │   │   ├── events/
│   │   │   │   │   ├── candidate-created.event.ts
│   │   │   │   │   ├── candidate-updated.event.ts
│   │   │   │   │   └── cv-uploaded.event.ts
│   │   │   │   └── utils/
│   │   │   ├── tests/
│   │   │   │   ├── unit/
│   │   │   │   ├── integration/
│   │   │   │   └── e2e/
│   │   │   ├── Dockerfile
│   │   │   ├── package.json
│   │   │   └── README.md
│   │   │
│   │   ├── client-service/           # Client Management
│   │   │   ├── src/
│   │   │   │   ├── controllers/
│   │   │   │   │   ├── client.controller.ts
│   │   │   │   │   ├── contact.controller.ts
│   │   │   │   │   └── contract.controller.ts
│   │   │   │   ├── services/
│   │   │   │   │   ├── client.service.ts
│   │   │   │   │   ├── relationship.service.ts
│   │   │   │   │   └── compliance.service.ts
│   │   │   │   ├── models/
│   │   │   │   │   ├── client.model.ts
│   │   │   │   │   ├── contact.model.ts
│   │   │   │   │   ├── contract.model.ts
│   │   │   │   │   └── requirement.model.ts
│   │   │   │   ├── repositories/
│   │   │   │   └── events/
│   │   │   ├── tests/
│   │   │   ├── Dockerfile
│   │   │   ├── package.json
│   │   │   └── README.md
│   │   │
│   │   ├── job-service/              # Job Management
│   │   │   ├── src/
│   │   │   │   ├── controllers/
│   │   │   │   │   ├── job.controller.ts
│   │   │   │   │   ├── application.controller.ts
│   │   │   │   │   └── posting.controller.ts
│   │   │   │   ├── services/
│   │   │   │   │   ├── job.service.ts
│   │   │   │   │   ├── application.service.ts
│   │   │   │   │   ├── posting.service.ts
│   │   │   │   │   └── description-optimizer.service.ts
│   │   │   │   ├── models/
│   │   │   │   │   ├── job.model.ts
│   │   │   │   │   ├── application.model.ts
│   │   │   │   │   └── job-board.model.ts
│   │   │   │   ├── repositories/
│   │   │   │   └── events/
│   │   │   ├── tests/
│   │   │   ├── Dockerfile
│   │   │   ├── package.json
│   │   │   └── README.md
│   │   │
│   │   ├── matching-service/         # AI Matching Engine
│   │   │   ├── src/
│   │   │   │   ├── controllers/
│   │   │   │   │   └── matching.controller.ts
│   │   │   │   ├── services/
│   │   │   │   │   ├── matching-engine.service.ts
│   │   │   │   │   ├── skills-matcher.service.ts
│   │   │   │   │   ├── scoring.service.ts
│   │   │   │   │   └── recommendation.service.ts
│   │   │   │   ├── ml/
│   │   │   │   │   ├── models/
│   │   │   │   │   │   ├── candidate-job-matcher.py
│   │   │   │   │   │   ├── skill-embeddings.py
│   │   │   │   │   │   └── success-predictor.py
│   │   │   │   │   ├── training/
│   │   │   │   │   │   ├── train.py
│   │   │   │   │   │   ├── evaluate.py
│   │   │   │   │   │   └── datasets/
│   │   │   │   │   └── inference/
│   │   │   │   ├── algorithms/
│   │   │   │   │   ├── collaborative-filtering.ts
│   │   │   │   │   ├── content-based.ts
│   │   │   │   │   └── hybrid.ts
│   │   │   │   └── utils/
│   │   │   ├── tests/
│   │   │   ├── Dockerfile
│   │   │   ├── requirements.txt      # Python dependencies
│   │   │   ├── package.json
│   │   │   └── README.md
│   │   │
│   │   ├── workflow-service/         # Workflow Automation
│   │   │   ├── src/
│   │   │   │   ├── controllers/
│   │   │   │   │   ├── workflow.controller.ts
│   │   │   │   │   └── pipeline.controller.ts
│   │   │   │   ├── services/
│   │   │   │   │   ├── workflow-engine.service.ts
│   │   │   │   │   ├── state-machine.service.ts
│   │   │   │   │   └── automation.service.ts
│   │   │   │   ├── workflows/
│   │   │   │   │   ├── recruitment-pipeline.ts
│   │   │   │   │   ├── placement-workflow.ts
│   │   │   │   │   ├── onboarding.ts
│   │   │   │   │   └── offboarding.ts
│   │   │   │   ├── models/
│   │   │   │   └── rules/
│   │   │   ├── tests/
│   │   │   ├── Dockerfile
│   │   │   ├── package.json
│   │   │   └── README.md
│   │   │
│   │   ├── scheduling-service/       # Interview Scheduling
│   │   │   ├── src/
│   │   │   │   ├── controllers/
│   │   │   │   │   ├── schedule.controller.ts
│   │   │   │   │   └── availability.controller.ts
│   │   │   │   ├── services/
│   │   │   │   │   ├── scheduling.service.ts
│   │   │   │   │   ├── calendar-sync.service.ts
│   │   │   │   │   ├── timeslot.service.ts
│   │   │   │   │   └── reminder.service.ts
│   │   │   │   ├── integrations/
│   │   │   │   │   ├── google-calendar.ts
│   │   │   │   │   ├── outlook-calendar.ts
│   │   │   │   │   └── ical.ts
│   │   │   │   ├── models/
│   │   │   │   └── utils/
│   │   │   ├── tests/
│   │   │   ├── Dockerfile
│   │   │   ├── package.json
│   │   │   └── README.md
│   │   │
│   │   ├── communication-service/    # Multi-channel Communication
│   │   │   ├── src/
│   │   │   │   ├── controllers/
│   │   │   │   │   ├── email.controller.ts
│   │   │   │   │   ├── sms.controller.ts
│   │   │   │   │   └── notification.controller.ts
│   │   │   │   ├── services/
│   │   │   │   │   ├── email.service.ts
│   │   │   │   │   ├── sms.service.ts
│   │   │   │   │   ├── push-notification.service.ts
│   │   │   │   │   ├── whatsapp.service.ts
│   │   │   │   │   └── template.service.ts
│   │   │   │   ├── templates/
│   │   │   │   │   ├── email/
│   │   │   │   │   │   ├── candidate-welcome.html
│   │   │   │   │   │   ├── interview-invitation.html
│   │   │   │   │   │   ├── offer-letter.html
│   │   │   │   │   │   └── placement-confirmation.html
│   │   │   │   │   ├── sms/
│   │   │   │   │   └── whatsapp/
│   │   │   │   ├── models/
│   │   │   │   └── queue/
│   │   │   ├── tests/
│   │   │   ├── Dockerfile
│   │   │   ├── package.json
│   │   │   └── README.md
│   │   │
│   │   ├── placement-service/        # Placement Management
│   │   │   ├── src/
│   │   │   │   ├── controllers/
│   │   │   │   │   ├── placement.controller.ts
│   │   │   │   │   └── onboarding.controller.ts
│   │   │   │   ├── services/
│   │   │   │   │   ├── placement.service.ts
│   │   │   │   │   ├── rebate.service.ts
│   │   │   │   │   └── replacement.service.ts
│   │   │   │   ├── models/
│   │   │   │   │   ├── placement.model.ts
│   │   │   │   │   └── onboarding.model.ts
│   │   │   │   └── events/
│   │   │   ├── tests/
│   │   │   ├── Dockerfile
│   │   │   ├── package.json
│   │   │   └── README.md
│   │   │
│   │   ├── finance-service/          # Financial Operations
│   │   │   ├── src/
│   │   │   │   ├── controllers/
│   │   │   │   │   ├── invoice.controller.ts
│   │   │   │   │   ├── payment.controller.ts
│   │   │   │   │   └── commission.controller.ts
│   │   │   │   ├── services/
│   │   │   │   │   ├── invoice.service.ts
│   │   │   │   │   ├── payment.service.ts
│   │   │   │   │   ├── rebate.service.ts
│   │   │   │   │   ├── commission.service.ts
│   │   │   │   │   └── payroll.service.ts
│   │   │   │   ├── models/
│   │   │   │   │   ├── invoice.model.ts
│   │   │   │   │   ├── payment.model.ts
│   │   │   │   │   └── commission.model.ts
│   │   │   │   └── integrations/
│   │   │   │       ├── stripe.ts
│   │   │   │       ├── xero.ts
│   │   │   │       └── quickbooks.ts
│   │   │   ├── tests/
│   │   │   ├── Dockerfile
│   │   │   ├── package.json
│   │   │   └── README.md
│   │   │
│   │   ├── analytics-service/        # Analytics & Reporting
│   │   │   ├── src/
│   │   │   │   ├── controllers/
│   │   │   │   │   ├── analytics.controller.ts
│   │   │   │   │   ├── report.controller.ts
│   │   │   │   │   └── dashboard.controller.ts
│   │   │   │   ├── services/
│   │   │   │   │   ├── analytics.service.ts
│   │   │   │   │   ├── kpi.service.ts
│   │   │   │   │   ├── report-generator.service.ts
│   │   │   │   │   └── data-export.service.ts
│   │   │   │   ├── reports/
│   │   │   │   │   ├── time-to-fill.ts
│   │   │   │   │   ├── consultant-performance.ts
│   │   │   │   │   ├── revenue.ts
│   │   │   │   │   └── source-effectiveness.ts
│   │   │   │   ├── ml/
│   │   │   │   │   ├── predictive-analytics.py
│   │   │   │   │   └── forecasting.py
│   │   │   │   └── models/
│   │   │   ├── tests/
│   │   │   ├── Dockerfile
│   │   │   ├── package.json
│   │   │   └── README.md
│   │   │
│   │   ├── integration-hub/          # External Integrations
│   │   │   ├── src/
│   │   │   │   ├── controllers/
│   │   │   │   │   ├── sync.controller.ts
│   │   │   │   │   └── webhook.controller.ts
│   │   │   │   ├── integrations/
│   │   │   │   │   ├── bullhorn/
│   │   │   │   │   │   ├── bullhorn-client.ts
│   │   │   │   │   │   ├── sync-candidates.ts
│   │   │   │   │   │   ├── sync-jobs.ts
│   │   │   │   │   │   ├── sync-clients.ts
│   │   │   │   │   │   ├── sync-placements.ts
│   │   │   │   │   │   └── webhooks.ts
│   │   │   │   │   ├── broadbean/
│   │   │   │   │   │   ├── broadbean-client.ts
│   │   │   │   │   │   ├── post-job.ts
│   │   │   │   │   │   └── fetch-applications.ts
│   │   │   │   │   ├── job-boards/
│   │   │   │   │   │   ├── indeed.ts
│   │   │   │   │   │   ├── totaljobs.ts
│   │   │   │   │   │   ├── cv-library.ts
│   │   │   │   │   │   ├── jobsite.ts
│   │   │   │   │   │   └── reed.ts
│   │   │   │   │   ├── linkedin/
│   │   │   │   │   │   ├── linkedin-client.ts
│   │   │   │   │   │   └── profile-enrichment.ts
│   │   │   │   │   ├── background-checks/
│   │   │   │   │   │   ├── sterling.ts
│   │   │   │   │   │   └── checkr.ts
│   │   │   │   │   └── references/
│   │   │   │   │       └── skillsurvey.ts
│   │   │   │   ├── services/
│   │   │   │   │   ├── sync.service.ts
│   │   │   │   │   ├── mapping.service.ts
│   │   │   │   │   └── conflict-resolution.service.ts
│   │   │   │   ├── models/
│   │   │   │   └── queue/
│   │   │   ├── tests/
│   │   │   ├── Dockerfile
│   │   │   ├── package.json
│   │   │   └── README.md
│   │   │
│   │   ├── notification-service/     # Real-time Notifications
│   │   │   ├── src/
│   │   │   │   ├── controllers/
│   │   │   │   ├── services/
│   │   │   │   │   ├── notification.service.ts
│   │   │   │   │   ├── websocket.service.ts
│   │   │   │   │   └── push.service.ts
│   │   │   │   ├── models/
│   │   │   │   └── handlers/
│   │   │   ├── tests/
│   │   │   ├── Dockerfile
│   │   │   ├── package.json
│   │   │   └── README.md
│   │   │
│   │   └── search-service/           # Elasticsearch wrapper
│   │       ├── src/
│   │       │   ├── controllers/
│   │       │   │   ├── search.controller.ts
│   │       │   │   └── indexing.controller.ts
│   │       │   ├── services/
│   │       │   │   ├── search.service.ts
│   │       │   │   ├── indexing.service.ts
│   │       │   │   └── query-builder.service.ts
│   │       │   ├── indices/
│   │       │   │   ├── candidate-index.ts
│   │       │   │   ├── job-index.ts
│   │       │   │   └── client-index.ts
│   │       │   └── models/
│   │       ├── tests/
│   │       ├── Dockerfile
│   │       ├── package.json
│   │       └── README.md
│   │
│   ├── shared/                       # Shared libraries
│   │   ├── types/                    # Shared TypeScript types
│   │   │   ├── candidate.types.ts
│   │   │   ├── client.types.ts
│   │   │   ├── job.types.ts
│   │   │   └── common.types.ts
│   │   ├── utils/                    # Common utilities
│   │   │   ├── date-utils.ts
│   │   │   ├── validation.ts
│   │   │   ├── encryption.ts
│   │   │   └── logger.ts
│   │   ├── constants/                # Shared constants
│   │   │   ├── job-types.ts
│   │   │   ├── status-codes.ts
│   │   │   └── skills-taxonomy.ts
│   │   ├── middleware/               # Reusable middleware
│   │   │   ├── error-handler.ts
│   │   │   ├── request-logger.ts
│   │   │   └── cors.ts
│   │   └── events/                   # Event definitions
│   │       ├── base-event.ts
│   │       └── event-types.ts
│   │
│   └── infrastructure/               # Infrastructure as code
│       ├── kubernetes/               # K8s manifests
│       │   ├── namespaces/
│       │   ├── deployments/
│       │   ├── services/
│       │   ├── ingress/
│       │   ├── configmaps/
│       │   └── secrets/
│       ├── terraform/                # Infrastructure provisioning
│       │   ├── aws/
│       │   │   ├── main.tf
│       │   │   ├── vpc.tf
│       │   │   ├── eks.tf
│       │   │   ├── rds.tf
│       │   │   └── s3.tf
│       │   ├── azure/
│       │   └── modules/
│       └── helm/                     # Helm charts
│           └── recruitment-platform/
│               ├── Chart.yaml
│               ├── values.yaml
│               └── templates/
│
├── frontend/                         # Frontend application
│   ├── README.md
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.js               # Next.js configuration
│   ├── tailwind.config.js           # Tailwind CSS config
│   │
│   ├── public/                      # Static assets
│   │   ├── images/
│   │   ├── icons/
│   │   └── fonts/
│   │
│   ├── src/
│   │   ├── app/                     # Next.js 13+ app directory
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── (auth)/              # Auth routes group
│   │   │   │   ├── login/
│   │   │   │   ├── register/
│   │   │   │   └── forgot-password/
│   │   │   ├── (dashboard)/         # Dashboard routes
│   │   │   │   ├── layout.tsx
│   │   │   │   ├── overview/
│   │   │   │   ├── candidates/
│   │   │   │   │   ├── page.tsx
│   │   │   │   │   ├── [id]/
│   │   │   │   │   ├── new/
│   │   │   │   │   └── components/
│   │   │   │   ├── clients/
│   │   │   │   │   ├── page.tsx
│   │   │   │   │   ├── [id]/
│   │   │   │   │   ├── new/
│   │   │   │   │   └── components/
│   │   │   │   ├── jobs/
│   │   │   │   │   ├── page.tsx
│   │   │   │   │   ├── [id]/
│   │   │   │   │   ├── new/
│   │   │   │   │   └── components/
│   │   │   │   ├── placements/
│   │   │   │   ├── pipeline/
│   │   │   │   ├── analytics/
│   │   │   │   └── settings/
│   │   │   └── api/                 # API routes (if needed)
│   │   │
│   │   ├── components/              # Reusable components
│   │   │   ├── ui/                  # Basic UI components
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Input.tsx
│   │   │   │   ├── Card.tsx
│   │   │   │   ├── Modal.tsx
│   │   │   │   ├── Table.tsx
│   │   │   │   └── DataGrid.tsx
│   │   │   ├── forms/               # Form components
│   │   │   │   ├── CandidateForm.tsx
│   │   │   │   ├── ClientForm.tsx
│   │   │   │   ├── JobForm.tsx
│   │   │   │   └── validators/
│   │   │   ├── charts/              # Chart components
│   │   │   │   ├── LineChart.tsx
│   │   │   │   ├── BarChart.tsx
│   │   │   │   └── PieChart.tsx
│   │   │   ├── layouts/             # Layout components
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── Footer.tsx
│   │   │   └── shared/              # Shared components
│   │   │       ├── LoadingSpinner.tsx
│   │   │       ├── ErrorBoundary.tsx
│   │   │       └── NotificationToast.tsx
│   │   │
│   │   ├── hooks/                   # Custom React hooks
│   │   │   ├── useAuth.ts
│   │   │   ├── useCandidates.ts
│   │   │   ├── useJobs.ts
│   │   │   ├── useWebSocket.ts
│   │   │   └── useDebounce.ts
│   │   │
│   │   ├── lib/                     # Libraries and utilities
│   │   │   ├── api-client.ts        # API client
│   │   │   ├── auth.ts              # Auth utilities
│   │   │   ├── validation.ts
│   │   │   └── formatting.ts
│   │   │
│   │   ├── store/                   # State management (Redux)
│   │   │   ├── index.ts
│   │   │   ├── slices/
│   │   │   │   ├── auth.slice.ts
│   │   │   │   ├── candidates.slice.ts
│   │   │   │   ├── clients.slice.ts
│   │   │   │   ├── jobs.slice.ts
│   │   │   │   └── ui.slice.ts
│   │   │   ├── middleware/
│   │   │   └── selectors/
│   │   │
│   │   ├── types/                   # TypeScript types
│   │   │   ├── api.types.ts
│   │   │   ├── models.types.ts
│   │   │   └── props.types.ts
│   │   │
│   │   └── styles/                  # Global styles
│   │       ├── globals.css
│   │       └── variables.css
│   │
│   └── tests/                       # Frontend tests
│       ├── unit/
│       ├── integration/
│       └── e2e/
│           └── playwright.config.ts
│
├── mobile/                           # React Native mobile app
│   ├── README.md
│   ├── package.json
│   ├── app.json
│   ├── tsconfig.json
│   │
│   ├── src/
│   │   ├── navigation/              # Navigation setup
│   │   │   ├── RootNavigator.tsx
│   │   │   ├── AuthNavigator.tsx
│   │   │   └── AppNavigator.tsx
│   │   ├── screens/                 # Screen components
│   │   │   ├── auth/
│   │   │   ├── candidates/
│   │   │   ├── jobs/
│   │   │   ├── pipeline/
│   │   │   └── profile/
│   │   ├── components/              # Reusable components
│   │   ├── hooks/                   # Custom hooks
│   │   ├── services/                # API services
│   │   ├── store/                   # State management
│   │   ├── types/                   # TypeScript types
│   │   └── utils/                   # Utilities
│   │
│   ├── android/                     # Android-specific
│   ├── ios/                         # iOS-specific
│   └── tests/                       # Mobile tests
│
├── data/                            # Data and database
│   ├── migrations/                  # Database migrations
│   │   ├── postgres/
│   │   │   ├── 001_initial_schema.sql
│   │   │   ├── 002_add_candidates.sql
│   │   │   ├── 003_add_clients.sql
│   │   │   └── ...
│   │   └── mongodb/
│   ├── seeds/                       # Seed data
│   │   ├── development/
│   │   ├── staging/
│   │   └── test/
│   ├── schemas/                     # Schema definitions
│   │   ├── postgres/
│   │   │   ├── candidates.sql
│   │   │   ├── clients.sql
│   │   │   └── jobs.sql
│   │   └── mongodb/
│   │       └── documents.json
│   └── etl/                         # Data transformation scripts
│       ├── bullhorn-import.py
│       ├── data-cleanup.py
│       └── historical-migration.py
│
├── scripts/                         # Utility scripts
│   ├── setup/                       # Setup scripts
│   │   ├── install-dependencies.sh
│   │   ├── setup-dev-env.sh
│   │   └── init-databases.sh
│   ├── deployment/                  # Deployment scripts
│   │   ├── deploy-staging.sh
│   │   ├── deploy-production.sh
│   │   └── rollback.sh
│   ├── maintenance/                 # Maintenance scripts
│   │   ├── backup-database.sh
│   │   ├── cleanup-old-data.sh
│   │   └── reindex-elasticsearch.sh
│   ├── monitoring/                  # Monitoring scripts
│   │   ├── health-check.sh
│   │   └── generate-report.sh
│   └── testing/                     # Testing utilities
│       ├── load-test.js
│       └── seed-test-data.sh
│
├── tests/                           # System-wide tests
│   ├── integration/                 # Integration tests
│   │   ├── candidate-flow.test.ts
│   │   ├── job-posting-flow.test.ts
│   │   └── placement-flow.test.ts
│   ├── e2e/                         # End-to-end tests
│   │   ├── user-journeys/
│   │   └── critical-paths/
│   ├── performance/                 # Performance tests
│   │   ├── load-tests/
│   │   └── stress-tests/
│   └── security/                    # Security tests
│       ├── penetration/
│       └── vulnerability/
│
├── config/                          # Configuration files
│   ├── development.yaml
│   ├── staging.yaml
│   ├── production.yaml
│   ├── test.yaml
│   └── secrets.example.yaml
│
└── .github/                         # GitHub-specific
    ├── workflows/                   # CI/CD workflows
    │   ├── ci.yml
    │   ├── deploy-staging.yml
    │   ├── deploy-production.yml
    │   ├── security-scan.yml
    │   └── performance-test.yml
    ├── ISSUE_TEMPLATE/
    ├── PULL_REQUEST_TEMPLATE.md
    └── CODEOWNERS
```

## Key Files and Their Purpose

### Root Level
- **docker-compose.yml**: Local development environment with all services
- **Makefile**: Common commands (start, stop, test, deploy, etc.)
- **.gitignore**: Ignore node_modules, .env, build artifacts
- **README.md**: Project overview, quick start guide

### Backend Services
Each microservice follows a consistent structure:
- **controllers/**: HTTP request handlers
- **services/**: Business logic layer
- **models/**: Data models and schemas
- **repositories/**: Data access layer
- **events/**: Event definitions for pub/sub
- **tests/**: Unit, integration, and E2E tests
- **Dockerfile**: Container definition
- **package.json**: Dependencies and scripts
- **README.md**: Service-specific documentation

### Frontend
- **Next.js 13+ App Router**: Modern routing with server components
- **Component-based architecture**: Reusable UI components
- **Redux Toolkit**: State management
- **TypeScript**: Type safety throughout
- **Tailwind CSS**: Utility-first styling

### Data Layer
- **migrations/**: Version-controlled database changes
- **seeds/**: Sample data for different environments
- **schemas/**: Database schema definitions
- **etl/**: Data transformation and migration scripts

### Infrastructure
- **kubernetes/**: K8s manifests for service deployment
- **terraform/**: Infrastructure as code
- **helm/**: Package manager for K8s

### Testing
- **Unit tests**: In each service's test directory
- **Integration tests**: Cross-service testing
- **E2E tests**: Full user journey testing
- **Performance tests**: Load and stress testing

## Development Workflow

1. **Local Development**:
   ```bash
   make setup          # Initialize development environment
   make start          # Start all services with docker-compose
   make test           # Run all tests
   make lint           # Check code quality
   ```

2. **Service Development**:
   ```bash
   cd backend/services/candidate-service
   npm install
   npm run dev         # Start service in watch mode
   npm test            # Run service tests
   ```

3. **Frontend Development**:
   ```bash
   cd frontend
   npm install
   npm run dev         # Start Next.js dev server
   npm run build       # Production build
   npm test            # Run tests
   ```

## Configuration Management

All configuration is environment-specific:
- **development.yaml**: Local development
- **staging.yaml**: Staging environment
- **production.yaml**: Production environment
- **secrets.example.yaml**: Template for secrets (not committed)

Secrets are managed via:
- Environment variables
- Kubernetes secrets
- AWS Secrets Manager / Azure Key Vault

## Deployment Strategy

1. **Development**: Automatic deployment on merge to `develop` branch
2. **Staging**: Automatic deployment on merge to `staging` branch
3. **Production**: Manual approval required, tagged releases

## Monitoring & Observability

- **Logging**: Centralized via ELK Stack
- **Metrics**: Prometheus + Grafana
- **Tracing**: Jaeger for distributed tracing
- **Alerts**: PagerDuty integration for critical issues

## Security

- **Authentication**: OAuth2 with JWT tokens
- **Authorization**: Role-based access control (RBAC)
- **Encryption**: TLS for transit, AES-256 for at rest
- **Secrets**: Never committed to repository
- **Scanning**: Automated security scanning in CI/CD

## Best Practices

1. **Code Quality**: ESLint, Prettier, SonarQube
2. **Testing**: Minimum 80% code coverage
3. **Documentation**: Keep docs up-to-date with code
4. **Git Flow**: Feature branches, pull requests, code reviews
5. **Semantic Versioning**: For all releases
6. **API Versioning**: v1, v2, etc. in URL paths
