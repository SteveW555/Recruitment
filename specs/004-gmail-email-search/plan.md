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

---

## Phase Completion Summary

### ✅ Phase 0: Research & Technology Decisions (Complete)

**Artifacts Generated**:
- [research.md](./research.md) - Comprehensive technology research and decisions

**Key Decisions**:
- Gmail API integration using googleapis npm package
- OAuth 2.0 with passport-google-oauth20
- File system storage with Bull queue cleanup
- Redis-backed rate limiting
- AES-256-GCM token encryption
- PostgreSQL + Prisma ORM

**Status**: All technical unknowns resolved ✅

---

### ✅ Phase 1: Design & Contracts (Complete)

**Artifacts Generated**:
1. [data-model.md](./data-model.md) - Complete data models, schemas, validation rules
2. [contracts/gmail-api.yaml](./contracts/gmail-api.yaml) - OpenAPI 3.1 specification
3. [quickstart.md](./quickstart.md) - Developer getting started guide

**Models Defined**:
- User (recruiter authentication)
- UserToken (encrypted OAuth tokens)
- EmailMessage (transient, not persisted)
- Attachment (CV files)
- DownloadedFile (24h retention tracking)
- SearchQuery (audit/analytics)
- AuditLog (compliance logging)

**API Endpoints**:
- Authentication: `/auth/google`, `/auth/google/callback`, `/auth/logout`, `/auth/status`
- Email Search: `/emails/search`, `/emails/{messageId}`
- Attachments: `/emails/{messageId}/attachments/{attachmentId}`, `/attachments/bulk-download`, `/attachments/history`
- Sessions: `/sessions/current`

**Agent Context**: Updated CLAUDE.md with Node.js 20, TypeScript 5.3, PostgreSQL 15, Redis 7 ✅

**Status**: Design complete, contracts defined, ready for task breakdown ✅

---

### ⏭️ Phase 2: Task Breakdown (Next Step)

**Next Command**: `/speckit.tasks`

This will generate actionable implementation tasks based on the plan, breaking down the work into:
- User stories from spec.md (US-001 to US-004)
- Ordered tasks with dependencies
- Acceptance criteria per task
- Estimated complexity/effort

---

## Implementation Readiness Checklist

- ✅ Technical research complete
- ✅ Technology stack decided
- ✅ Data models defined
- ✅ API contracts specified
- ✅ Database schema designed
- ✅ Security approach documented
- ✅ Rate limiting strategy defined
- ✅ File cleanup strategy defined
- ✅ Quickstart guide created
- ✅ Agent context updated
- ⏭️ Tasks generated (run `/speckit.tasks`)
- ⏭️ Implementation started
- ⏭️ Tests written (TDD approach)
- ⏭️ Code review completed
- ⏭️ Deployed to staging
- ⏭️ Production deployment

---

## Planning Artifacts Summary

| Artifact | Location | Purpose | Status |
|----------|----------|---------|--------|
| **Implementation Plan** | [plan.md](./plan.md) | Overall implementation strategy | ✅ Complete |
| **Research Document** | [research.md](./research.md) | Technology decisions & best practices | ✅ Complete |
| **Data Model** | [data-model.md](./data-model.md) | Database schemas & validation | ✅ Complete |
| **API Contract** | [contracts/gmail-api.yaml](./contracts/gmail-api.yaml) | OpenAPI 3.1 specification | ✅ Complete |
| **Quickstart Guide** | [quickstart.md](./quickstart.md) | Developer setup instructions | ✅ Complete |
| **Feature Spec** | [spec.md](./spec.md) | Original requirements | ✅ Complete |
| **Tasks Breakdown** | [tasks.md](./tasks.md) | Implementation tasks | ⏭️ Generate with `/speckit.tasks` |

---

## Success Metrics (from Specification)

These metrics will be validated during implementation and testing:

- **SC-001**: Gmail OAuth connection < 1 minute ⏱️
- **SC-002**: Email search results < 5 seconds ⏱️
- **SC-003**: CV access within 3 clicks 🖱️
- **SC-004**: Handle 10,000+ emails without degradation 📊
- **SC-005**: 95% CV extraction success rate ✅
- **SC-006**: 70%+ result reduction with filters 🔍
- **SC-007**: Stable under Gmail API rate limits ⚡
- **SC-008**: Zero data exposure incidents 🔒
- **SC-009**: Bulk download 50+ CVs < 30 seconds ⏬

---

**Planning Phase Status**: ✅ COMPLETE - Ready for `/speckit.tasks` command

**Branch**: `004-gmail-email-search`
**Spec**: [spec.md](./spec.md)
**Estimated Implementation Time**: 3-4 weeks (1 backend dev + 1 frontend dev)
**Next Command**: `/speckit.tasks`
