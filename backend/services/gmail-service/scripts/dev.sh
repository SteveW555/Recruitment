#!/bin/bash

# Gmail Service Development Startup Script
# Usage: ./scripts/dev.sh

set -e

echo "🚀 Starting Gmail Service (Development Mode)"
echo "================================================"

# Check if .env exists
if [ ! -f ".env" ]; then
  echo "⚠️  .env file not found! Copying from .env.example..."
  cp .env.example .env
  echo "📝 Please update .env with your actual credentials"
  exit 1
fi

# Check if Docker Compose is running
echo "🐳 Checking Docker services..."
cd ../../../infrastructure/docker
docker-compose -f docker-compose.dev.yml up -d postgres redis
echo "✅ PostgreSQL and Redis are running"

cd ../../backend/services/gmail-service

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
  echo "📦 Installing dependencies..."
  npm install
fi

# Generate Prisma Client
echo "🔧 Generating Prisma Client..."
npm run prisma:generate

# Run migrations
echo "🗄️  Running database migrations..."
npm run prisma:migrate || true

# Start development server
echo "🏃 Starting development server..."
npm run start:dev
