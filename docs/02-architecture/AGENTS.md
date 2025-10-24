# Repository Guidelines

## Project Structure & Module Organization
- `backend/` hosts the Node.js/NestJS microservices; each service lives under `backend/services/<service-name>/src` with domain-specific modules and matching `tests/`.
- `frontend/` contains the React/TypeScript dashboard (`src/`), static assets in `public/`, and UI tests in `tests/`.
- `mobile/` is the React Native app with platform builds (`android/`, `ios/`) and shared code in `src/`.
- `docs/` aggregates architecture diagrams, API specs, and process manuals; sync updates here whenever service contracts change.
- Configuration assets live in `config/` and deployment automation in `infrastructure/` and `scripts/`; seed data and fixtures reside in `data/` and `test_*` CSVs.

## Build, Test, and Development Commands
- `make setup` installs dependencies and prepares `.env`.
- `make start`, `make start-backend`, and `make start-frontend` launch Docker stacks or focused services; use `make stop`/`make restart` to cycle containers.
- `make dev-backend`, `make dev-frontend`, and `make dev-mobile` run hot-reload workflows inside their respective directories.
- `make test` executes the aggregated test suite; pair with `make lint`, `make format`, and `make build` before opening a PR.
- `make db-migrate`, `make db-seed`, and `make db-reset` manage local database state; back up with `make db-backup` prior to destructive tasks.

## Coding Style & Naming Conventions
- Backend services follow TypeScript with NestJS-style modules; keep files PascalCase for classes, camelCase for instances, and suffix DTOs, entities, and providers explicitly (e.g., `candidate.service.ts`).
- Frontend React components use PascalCase filenames (`CandidateTable.tsx`), hooks with `use` prefix, and colocate styles/tests beside components.
- Format code via Prettier (`npm run format`) and enforce ESLint rules (`npm run lint`); do not bypass CI linting.
- Shared interfaces belong in `backend/shared/` or `frontend/src/types/` to avoid duplication; update imports when contracts shift.

## Testing Guidelines
- Write unit tests under `tests/unit`, integration in `tests/integration`, and end-to-end flows in `tests/e2e`; use `*.spec.ts` or `*.test.tsx` naming.
- Run `make test` (or `npm test` within a service) before commits; include database-dependent tests behind feature flags or use Docker fixtures.
- Maintain coverage at or above current thresholds; expand fixtures in `data/` when adding edge cases and regenerate snapshots deliberately.

## Commit & Pull Request Guidelines
- Repository snapshots ship without Git history; adopt Conventional Commits (`feat(api-gateway): …`, `fix(matching): …`) to preserve clarity across services.
- Keep commits scoped and reversible; accompany functional changes with schema migrations, docs, and config updates in the same branch.
- Pull requests require: a concise summary, linked backlog ticket, test evidence (`make test` output), and screenshots or API examples for UI/API shifts.
- Seek two approvals and ensure CI passes; update relevant entries in `docs/` and note any follow-up tasks in the PR description.

## Security & Configuration Tips
- Never commit real secrets—use `.env.example` and `config/secrets.example.yaml` as templates; request vault access for production credentials.
- Verify service health with `make health` after significant backend edits and confirm external integrations via the `integration-hub` staging keys before merging.
