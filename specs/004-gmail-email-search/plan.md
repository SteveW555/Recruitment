# Implementation Plan: Gmail Email Search & CV Extraction

**Branch**: `004-gmail-email-search` | **Date**: 2025-11-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-gmail-email-search/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

**Primary Requirement**: Enable recruiters to search their personal Gmail accounts by date range, filter emails by sender/subject/body keywords, and extract/download CV attachments (PDF/DOC/DOCX files) with secure OAuth 2.0 authentication.

**Technical Approach**:
- **Backend**: Node.js/NestJS microservice using Gmail API with OAuth 2.0 authentication
- **Frontend**: Next.js 14 React application with server-side rendering for search UI
- **Storage**: PostgreSQL for session management, Redis for OAuth token caching, temporary file system storage for downloaded CVs with 24-hour TTL
- **Integration**: Google Cloud Platform OAuth 2.0 flow, Gmail API v1
- **Security**: Individual user authentication (no shared accounts), encrypted token storage, automatic 24-hour file cleanup

## Technical Context

**Language/Version**: Node.js 20 LTS (backend), TypeScript 5.3 (both), React 18 (frontend)
**Primary Dependencies**:
- Backend: NestJS 10.x, googleapis (Gmail API client), passport-google-oauth20, prisma (ORM), bull (job queue for file cleanup)
- Frontend: Next.js 14, React Query, Tailwind CSS, shadcn/ui components
**Storage**: PostgreSQL 15 (user sessions, OAuth tokens), Redis 7 (token cache, session store), File system (temporary CV storage with 24h TTL)
**Testing**: Jest (unit), Playwright (E2E), Supertest (API integration)
**Target Platform**: Docker containers on Linux (backend), Vercel/Node.js server (frontend)
**Project Type**: Web application (backend API + frontend SPA)
**Performance Goals**:
- Email search: <5s for any date range (SC-002)
- CV download: <3 clicks to access (SC-003)
- Bulk download: 50+ CVs in <30s (SC-009)
- API throughput: Handle 100 concurrent users per recruiter account
**Constraints**:
- Gmail API rate limits: 250 quota units/user/second
- OAuth token refresh: Automatic before expiration (no user interruption)
- File storage: 25MB max per file with warnings
- Session persistence: Until browser close (no timeout)
- GDPR compliance: 24-hour file retention maximum
**Scale/Scope**:
- Users: 50-100 recruiters initially
- Email volume: 10,000+ emails per search operation
- Concurrent searches: 20-30 active searches
- Storage: ~500GB temporary file storage (rotating 24h window)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Constitution Status**: No project constitution currently defined in `.specify/memory/constitution.md`. Template exists but principles not yet ratified.

**Recommended Future Constitution Principles** (for consideration):
1. **Microservices Architecture**: This feature integrates with existing 14-microservice system
2. **API-First Design**: RESTful API contracts before implementation
3. **Security by Default**: OAuth 2.0, encrypted storage, audit logging
4. **GDPR Compliance**: Data minimization, right to deletion, 24h retention
5. **Test Coverage**: Unit (>80%), Integration (critical paths), E2E (user journeys)

**Current Assessment**: ✅ PASS - No violations possible as constitution not yet defined. Feature aligns with ProActive People system architecture documented in project CLAUDE.md.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/services/gmail-service/
├── src/
│   ├── auth/
│   │   ├── oauth.controller.ts      # OAuth 2.0 flow endpoints
│   │   ├── oauth.service.ts         # Google OAuth integration
│   │   └── token.service.ts         # Token encryption & refresh
│   ├── gmail/
│   │   ├── gmail.controller.ts      # Email search API endpoints
│   │   ├── gmail.service.ts         # Gmail API client wrapper
│   │   └── email.transformer.ts     # Gmail API → internal model
│   ├── attachments/
│   │   ├── attachments.controller.ts # CV download endpoints
│   │   ├── attachments.service.ts    # File handling & MIME detection
│   │   └── cleanup.job.ts            # Bull queue for 24h cleanup
│   ├── sessions/
│   │   ├── sessions.controller.ts    # Session management
│   │   └── sessions.service.ts       # Session persistence
│   ├── database/
│   │   ├── prisma/
│   │   │   └── schema.prisma         # DB schema definition
│   │   └── migrations/               # Prisma migrations
│   └── main.ts
├── tests/
│   ├── unit/                         # Unit tests for services
│   ├── integration/                  # API endpoint tests
│   └── e2e/                          # End-to-end flows
└── docker/
    └── Dockerfile

frontend/
├── src/
│   ├── app/
│   │   ├── gmail-search/
│   │   │   ├── page.tsx              # Main search interface
│   │   │   └── layout.tsx
│   │   └── auth/
│   │       └── callback/
│   │           └── page.tsx          # OAuth callback handler
│   ├── components/
│   │   ├── search/
│   │   │   ├── SearchForm.tsx        # Date range & filter form
│   │   │   ├── EmailList.tsx         # Paginated results list
│   │   │   ├── EmailCard.tsx         # Individual email display
│   │   │   └── AttachmentList.tsx    # CV attachments display
│   │   └── ui/                       # shadcn/ui components
│   ├── lib/
│   │   ├── api/
│   │   │   ├── gmail.ts              # Gmail API client
│   │   │   └── auth.ts               # Auth API client
│   │   └── hooks/
│   │       ├── useEmailSearch.ts     # React Query hook
│   │       └── useAuth.ts            # Auth state hook
│   └── types/
│       └── gmail.ts                  # TypeScript interfaces
└── tests/
    ├── unit/                         # Component tests
    └── e2e/                          # Playwright E2E tests

shared/
└── contracts/
    └── gmail-api.yaml                # OpenAPI 3.1 spec
```

**Structure Decision**: Web application architecture with backend microservice and frontend SPA. The gmail-service backend follows NestJS module structure, while frontend uses Next.js 14 App Router. Shared contracts directory for API specification versioning.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations**: Constitution not yet defined. Feature follows existing ProActive People architecture patterns (microservices, REST API, React frontend).
