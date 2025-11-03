# Gmail Service - Production Dockerfile
# Multi-stage build for optimized production image

# =============================================================================
# Stage 1: Dependencies
# =============================================================================
FROM node:20-alpine AS dependencies

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY prisma ./prisma/

# Install dependencies (including devDependencies for Prisma)
RUN npm ci --include=dev

# Generate Prisma Client
RUN npx prisma generate

# =============================================================================
# Stage 2: Builder
# =============================================================================
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependencies from previous stage
COPY --from=dependencies /app/node_modules ./node_modules
COPY --from=dependencies /app/prisma ./prisma

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Remove devDependencies
RUN npm prune --production

# =============================================================================
# Stage 3: Production
# =============================================================================
FROM node:20-alpine AS production

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S gmail -u 1001

WORKDIR /app

# Copy built application and dependencies
COPY --from=builder --chown=gmail:nodejs /app/dist ./dist
COPY --from=builder --chown=gmail:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=gmail:nodejs /app/prisma ./prisma
COPY --from=builder --chown=gmail:nodejs /app/package*.json ./

# Create directories for file storage
RUN mkdir -p /app/storage/downloads && \
    chown -R gmail:nodejs /app/storage

# Switch to non-root user
USER gmail

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \
  CMD node -e "require('http').get('http://localhost:8080/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Set environment variables
ENV NODE_ENV=production \
    PORT=8080

# Use dumb-init to handle signals properly
ENTRYPOINT ["dumb-init", "--"]

# Start the application
CMD ["node", "dist/main.js"]
