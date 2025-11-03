import { Module } from '@nestjs/common';
import { HealthController } from './health.controller';
import { PrismaModule } from '../prisma/prisma.module';

/**
 * Health Check Module
 *
 * Provides health check endpoints for monitoring:
 * - Liveness probe: GET /health
 * - Readiness probe: GET /health/ready
 * - Detailed status: GET /health/detailed
 * - System metrics: GET /health/metrics
 *
 * Used by:
 * - Kubernetes for liveness/readiness probes
 * - Load balancers for health checks
 * - Monitoring systems (Grafana, Datadog, Prometheus)
 *
 * @see SECURITY.md - Logging & Monitoring section
 */
@Module({
  imports: [PrismaModule],
  controllers: [HealthController],
})
export class HealthModule {}
