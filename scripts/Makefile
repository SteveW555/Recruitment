.PHONY: help setup start stop restart logs clean test lint format build deploy

# Default target
.DEFAULT_GOAL := help

# Color output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Variables
DOCKER_COMPOSE := docker-compose
DOCKER_COMPOSE_PROD := docker-compose -f docker-compose.prod.yml

help: ## Show this help message
	@echo "$(BLUE)ProActive People - Universal Recruitment Automation System$(NC)"
	@echo "$(GREEN)Available commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

# ===== Setup & Installation =====

setup: ## Initial setup (install dependencies, create env files)
	@echo "$(BLUE)Setting up development environment...$(NC)"
	@cp -n .env.example .env || true
	@echo "$(GREEN)✓ Environment file created$(NC)"
	@$(MAKE) install-backend
	@$(MAKE) install-frontend
	@echo "$(GREEN)✓ Setup complete!$(NC)"

install-backend: ## Install backend dependencies
	@echo "$(BLUE)Installing backend dependencies...$(NC)"
	@cd backend && npm install
	@echo "$(GREEN)✓ Backend dependencies installed$(NC)"

install-frontend: ## Install frontend dependencies
	@echo "$(BLUE)Installing frontend dependencies...$(NC)"
	@cd frontend && npm install
	@echo "$(GREEN)✓ Frontend dependencies installed$(NC)"

install-mobile: ## Install mobile dependencies
	@echo "$(BLUE)Installing mobile dependencies...$(NC)"
	@cd mobile && npm install
	@echo "$(GREEN)✓ Mobile dependencies installed$(NC)"

# ===== Docker Commands =====

start: ## Start all services with Docker Compose
	@echo "$(BLUE)Starting all services...$(NC)"
	@$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✓ All services started$(NC)"
	@echo "$(YELLOW)Web UI: http://localhost:3000$(NC)"
	@echo "$(YELLOW)API Gateway: http://localhost:8080$(NC)"
	@echo "$(YELLOW)Grafana: http://localhost:3002$(NC)"

start-backend: ## Start only backend services
	@echo "$(BLUE)Starting backend services...$(NC)"
	@$(DOCKER_COMPOSE) up -d postgres mongodb redis elasticsearch rabbitmq api-gateway candidate-service client-service job-service
	@echo "$(GREEN)✓ Backend services started$(NC)"

start-frontend: ## Start only frontend service
	@echo "$(BLUE)Starting frontend...$(NC)"
	@$(DOCKER_COMPOSE) up -d frontend
	@echo "$(GREEN)✓ Frontend started at http://localhost:3000$(NC)"

stop: ## Stop all services
	@echo "$(BLUE)Stopping all services...$(NC)"
	@$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✓ All services stopped$(NC)"

restart: stop start ## Restart all services

restart-service: ## Restart specific service (usage: make restart-service SERVICE=candidate-service)
	@echo "$(BLUE)Restarting $(SERVICE)...$(NC)"
	@$(DOCKER_COMPOSE) restart $(SERVICE)
	@echo "$(GREEN)✓ $(SERVICE) restarted$(NC)"

logs: ## View logs for all services
	@$(DOCKER_COMPOSE) logs -f

logs-service: ## View logs for specific service (usage: make logs-service SERVICE=candidate-service)
	@$(DOCKER_COMPOSE) logs -f $(SERVICE)

ps: ## Show running containers
	@$(DOCKER_COMPOSE) ps

# ===== Database Commands =====

db-migrate: ## Run database migrations
	@echo "$(BLUE)Running database migrations...$(NC)"
	@cd backend && npm run migration:up
	@echo "$(GREEN)✓ Migrations complete$(NC)"

db-seed: ## Seed database with test data
	@echo "$(BLUE)Seeding database...$(NC)"
	@cd backend && npm run seed:dev
	@echo "$(GREEN)✓ Database seeded$(NC)"

db-reset: ## Reset database (drop, recreate, migrate, seed)
	@echo "$(RED)⚠ This will delete all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(MAKE) db-drop && $(MAKE) db-create && $(MAKE) db-migrate && $(MAKE) db-seed; \
	fi

db-drop: ## Drop database
	@echo "$(BLUE)Dropping database...$(NC)"
	@$(DOCKER_COMPOSE) exec postgres psql -U admin -c "DROP DATABASE IF EXISTS recruitment;"
	@echo "$(GREEN)✓ Database dropped$(NC)"

db-create: ## Create database
	@echo "$(BLUE)Creating database...$(NC)"
	@$(DOCKER_COMPOSE) exec postgres psql -U admin -c "CREATE DATABASE recruitment;"
	@echo "$(GREEN)✓ Database created$(NC)"

db-backup: ## Backup database
	@echo "$(BLUE)Backing up database...$(NC)"
	@mkdir -p backups
	@$(DOCKER_COMPOSE) exec -T postgres pg_dump -U admin recruitment > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✓ Database backed up$(NC)"

db-restore: ## Restore database from backup (usage: make db-restore FILE=backups/backup.sql)
	@echo "$(BLUE)Restoring database from $(FILE)...$(NC)"
	@$(DOCKER_COMPOSE) exec -T postgres psql -U admin recruitment < $(FILE)
	@echo "$(GREEN)✓ Database restored$(NC)"

# ===== Testing =====

test: ## Run all tests
	@echo "$(BLUE)Running all tests...$(NC)"
	@$(MAKE) test-backend
	@$(MAKE) test-frontend
	@echo "$(GREEN)✓ All tests passed$(NC)"

test-backend: ## Run backend tests
	@echo "$(BLUE)Running backend tests...$(NC)"
	@cd backend && npm test
	@echo "$(GREEN)✓ Backend tests passed$(NC)"

test-frontend: ## Run frontend tests
	@echo "$(BLUE)Running frontend tests...$(NC)"
	@cd frontend && npm test
	@echo "$(GREEN)✓ Frontend tests passed$(NC)"

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	@cd backend && npm run test:unit
	@echo "$(GREEN)✓ Unit tests passed$(NC)"

test-integration: ## Run integration tests
	@echo "$(BLUE)Running integration tests...$(NC)"
	@cd backend && npm run test:integration
	@echo "$(GREEN)✓ Integration tests passed$(NC)"

test-e2e: ## Run end-to-end tests
	@echo "$(BLUE)Running E2E tests...$(NC)"
	@cd frontend && npm run test:e2e
	@echo "$(GREEN)✓ E2E tests passed$(NC)"

test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	@cd backend && npm run test:coverage
	@cd frontend && npm run test:coverage
	@echo "$(GREEN)✓ Coverage reports generated$(NC)"

# ===== Code Quality =====

lint: ## Run linters
	@echo "$(BLUE)Running linters...$(NC)"
	@cd backend && npm run lint
	@cd frontend && npm run lint
	@echo "$(GREEN)✓ Linting complete$(NC)"

format: ## Format code with Prettier
	@echo "$(BLUE)Formatting code...$(NC)"
	@cd backend && npm run format
	@cd frontend && npm run format
	@echo "$(GREEN)✓ Code formatted$(NC)"

typecheck: ## Run TypeScript type checking
	@echo "$(BLUE)Type checking...$(NC)"
	@cd backend && npm run typecheck
	@cd frontend && npm run typecheck
	@echo "$(GREEN)✓ Type checking complete$(NC)"

check: lint typecheck test ## Run all quality checks

# ===== Build =====

build: ## Build all services
	@echo "$(BLUE)Building all services...$(NC)"
	@$(DOCKER_COMPOSE) build
	@echo "$(GREEN)✓ Build complete$(NC)"

build-backend: ## Build backend services
	@echo "$(BLUE)Building backend...$(NC)"
	@cd backend && npm run build
	@echo "$(GREEN)✓ Backend built$(NC)"

build-frontend: ## Build frontend
	@echo "$(BLUE)Building frontend...$(NC)"
	@cd frontend && npm run build
	@echo "$(GREEN)✓ Frontend built$(NC)"

build-mobile: ## Build mobile app
	@echo "$(BLUE)Building mobile app...$(NC)"
	@cd mobile && npm run build:android && npm run build:ios
	@echo "$(GREEN)✓ Mobile app built$(NC)"

# ===== Deployment =====

deploy-staging: ## Deploy to staging environment
	@echo "$(BLUE)Deploying to staging...$(NC)"
	@./scripts/deployment/deploy-staging.sh
	@echo "$(GREEN)✓ Deployed to staging$(NC)"

deploy-production: ## Deploy to production (requires approval)
	@echo "$(RED)⚠ Deploying to PRODUCTION!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		./scripts/deployment/deploy-production.sh; \
	fi

rollback-staging: ## Rollback staging deployment
	@echo "$(BLUE)Rolling back staging...$(NC)"
	@./scripts/deployment/rollback.sh staging
	@echo "$(GREEN)✓ Staging rolled back$(NC)"

rollback-production: ## Rollback production deployment
	@echo "$(RED)⚠ Rolling back PRODUCTION!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		./scripts/deployment/rollback.sh production; \
	fi

# ===== Monitoring =====

health: ## Check health of all services
	@echo "$(BLUE)Checking service health...$(NC)"
	@curl -f http://localhost:8080/health || echo "$(RED)✗ API Gateway unhealthy$(NC)"
	@curl -f http://localhost:8081/health || echo "$(RED)✗ Candidate Service unhealthy$(NC)"
	@curl -f http://localhost:8082/health || echo "$(RED)✗ Client Service unhealthy$(NC)"
	@curl -f http://localhost:8083/health || echo "$(RED)✗ Job Service unhealthy$(NC)"
	@echo "$(GREEN)✓ Health check complete$(NC)"

status-staging: ## Check staging deployment status
	@./scripts/monitoring/health-check.sh staging

status-production: ## Check production deployment status
	@./scripts/monitoring/health-check.sh production

metrics: ## Open Grafana metrics dashboard
	@echo "$(BLUE)Opening Grafana...$(NC)"
	@open http://localhost:3002 || xdg-open http://localhost:3002

logs-staging: ## View staging logs
	@kubectl logs -f -l env=staging -n recruitment

logs-production: ## View production logs
	@kubectl logs -f -l env=production -n recruitment

# ===== Maintenance =====

clean: ## Clean up containers, volumes, and build artifacts
	@echo "$(BLUE)Cleaning up...$(NC)"
	@$(DOCKER_COMPOSE) down -v
	@rm -rf backend/node_modules backend/dist
	@rm -rf frontend/node_modules frontend/.next
	@rm -rf mobile/node_modules
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

clean-docker: ## Remove all Docker images and volumes
	@echo "$(RED)⚠ This will remove all Docker images and volumes!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(DOCKER_COMPOSE) down -v --rmi all; \
	fi

prune: ## Prune Docker system (free up space)
	@echo "$(BLUE)Pruning Docker system...$(NC)"
	@docker system prune -f
	@echo "$(GREEN)✓ Docker system pruned$(NC)"

reindex-elasticsearch: ## Reindex Elasticsearch
	@echo "$(BLUE)Reindexing Elasticsearch...$(NC)"
	@./scripts/maintenance/reindex-elasticsearch.sh
	@echo "$(GREEN)✓ Reindexing complete$(NC)"

# ===== Development Helpers =====

shell-postgres: ## Open PostgreSQL shell
	@$(DOCKER_COMPOSE) exec postgres psql -U admin recruitment

shell-mongodb: ## Open MongoDB shell
	@$(DOCKER_COMPOSE) exec mongodb mongosh -u admin -p dev_password_change_in_prod

shell-redis: ## Open Redis CLI
	@$(DOCKER_COMPOSE) exec redis redis-cli -a dev_password_change_in_prod

shell-service: ## Open shell in service container (usage: make shell-service SERVICE=candidate-service)
	@$(DOCKER_COMPOSE) exec $(SERVICE) sh

dev-backend: ## Start backend in development mode
	@echo "$(BLUE)Starting backend in dev mode...$(NC)"
	@cd backend/services/candidate-service && npm run dev

dev-frontend: ## Start frontend in development mode
	@echo "$(BLUE)Starting frontend in dev mode...$(NC)"
	@cd frontend && npm run dev

dev-mobile: ## Start mobile app in development mode
	@echo "$(BLUE)Starting mobile app in dev mode...$(NC)"
	@cd mobile && npm run start

watch: ## Watch for changes and auto-reload
	@echo "$(BLUE)Watching for changes...$(NC)"
	@$(DOCKER_COMPOSE) up --watch

# ===== Documentation =====

docs: ## Generate API documentation
	@echo "$(BLUE)Generating documentation...$(NC)"
	@cd backend && npm run docs:generate
	@echo "$(GREEN)✓ Documentation generated$(NC)"

docs-serve: ## Serve documentation locally
	@echo "$(BLUE)Serving documentation...$(NC)"
	@cd docs && python -m http.server 8000

# ===== Release =====

version: ## Show current version
	@cat package.json | grep version | head -1 | awk -F: '{ print $$2 }' | sed 's/[", ]//g'

release: ## Create new release (usage: make release VERSION=1.0.0)
	@echo "$(BLUE)Creating release $(VERSION)...$(NC)"
	@git tag -a v$(VERSION) -m "Release v$(VERSION)"
	@git push origin v$(VERSION)
	@echo "$(GREEN)✓ Release v$(VERSION) created$(NC)"
