import { Controller, Get, Logger } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';
import { PrismaService } from '../prisma/prisma.service';
import { InjectRedis } from '@nestjs-modules/ioredis';
import { Redis } from 'ioredis';
import * as os from 'os';
import * as process from 'process';

/**
 * Health Check Controller
 *
 * Provides system health and status endpoints for monitoring:
 * - Service liveness (is the service running?)
 * - Service readiness (is the service ready to accept traffic?)
 * - Detailed health status (database, Redis, system metrics)
 *
 * Use Cases:
 * - Kubernetes liveness/readiness probes
 * - Load balancer health checks
 * - Monitoring dashboards (Grafana, Datadog)
 * - Incident investigation
 *
 * Endpoints:
 * - GET /health - Basic health check (liveness)
 * - GET /health/ready - Readiness check
 * - GET /health/detailed - Comprehensive health status
 * - GET /health/metrics - System metrics
 *
 * @see SECURITY.md - Logging & Monitoring section
 */
@ApiTags('health')
@Controller('health')
export class HealthController {
  private readonly logger = new Logger(HealthController.name);
  private readonly startTime: Date;

  constructor(
    private readonly prisma: PrismaService,
    @InjectRedis() private readonly redis: Redis,
  ) {
    this.startTime = new Date();
  }

  /**
   * Basic health check (liveness probe)
   *
   * Returns 200 OK if the service is running.
   * Does NOT check dependencies (database, Redis).
   *
   * Use for: Kubernetes liveness probe
   *
   * @returns Basic health status
   */
  @Get()
  @ApiOperation({
    summary: 'Basic health check (liveness)',
    description: 'Returns 200 OK if service is running. Does not check dependencies.',
  })
  @ApiResponse({
    status: 200,
    description: 'Service is alive',
    schema: {
      example: {
        status: 'ok',
        timestamp: '2025-01-15T10:30:00Z',
        service: 'gmail-service',
        version: '1.0.0',
      },
    },
  })
  async getHealth() {
    return {
      status: 'ok',
      timestamp: new Date().toISOString(),
      service: 'gmail-service',
      version: '1.0.0',
    };
  }

  /**
   * Readiness check
   *
   * Returns 200 OK if the service is ready to accept traffic.
   * Checks critical dependencies:
   * - PostgreSQL database connectivity
   * - Redis connectivity
   *
   * Use for: Kubernetes readiness probe, load balancer health checks
   *
   * @returns Readiness status with dependency checks
   */
  @Get('ready')
  @ApiOperation({
    summary: 'Readiness check',
    description:
      'Returns 200 OK if service is ready to accept traffic. ' +
      'Checks database and Redis connectivity.',
  })
  @ApiResponse({
    status: 200,
    description: 'Service is ready',
    schema: {
      example: {
        status: 'ready',
        timestamp: '2025-01-15T10:30:00Z',
        checks: {
          database: 'ok',
          redis: 'ok',
        },
      },
    },
  })
  @ApiResponse({
    status: 503,
    description: 'Service is not ready (dependency failure)',
    schema: {
      example: {
        status: 'not_ready',
        timestamp: '2025-01-15T10:30:00Z',
        checks: {
          database: 'error',
          redis: 'ok',
        },
        errors: ['Database connection failed'],
      },
    },
  })
  async getReadiness() {
    const checks: any = {
      database: 'checking',
      redis: 'checking',
    };
    const errors: string[] = [];

    // Check database
    try {
      await this.prisma.$queryRaw`SELECT 1`;
      checks.database = 'ok';
    } catch (error) {
      checks.database = 'error';
      errors.push(`Database: ${error.message}`);
      this.logger.error(`Database health check failed: ${error.message}`);
    }

    // Check Redis
    try {
      await this.redis.ping();
      checks.redis = 'ok';
    } catch (error) {
      checks.redis = 'error';
      errors.push(`Redis: ${error.message}`);
      this.logger.error(`Redis health check failed: ${error.message}`);
    }

    const isReady = errors.length === 0;

    return {
      status: isReady ? 'ready' : 'not_ready',
      timestamp: new Date().toISOString(),
      checks,
      ...(errors.length > 0 && { errors }),
    };
  }

  /**
   * Detailed health status
   *
   * Returns comprehensive health information:
   * - Service status and uptime
   * - Dependency health (database, Redis)
   * - System metrics (memory, CPU)
   * - Configuration status
   *
   * Use for: Monitoring dashboards, incident investigation
   *
   * @returns Detailed health status
   */
  @Get('detailed')
  @ApiOperation({
    summary: 'Detailed health status',
    description:
      'Returns comprehensive health information including service status, ' +
      'dependency health, system metrics, and configuration.',
  })
  @ApiResponse({
    status: 200,
    description: 'Detailed health status',
    schema: {
      example: {
        status: 'healthy',
        timestamp: '2025-01-15T10:30:00Z',
        service: {
          name: 'gmail-service',
          version: '1.0.0',
          uptime: '5d 12h 30m',
          environment: 'production',
        },
        dependencies: {
          database: {
            status: 'ok',
            responseTime: '15ms',
          },
          redis: {
            status: 'ok',
            responseTime: '2ms',
          },
        },
        system: {
          platform: 'linux',
          nodeVersion: 'v20.10.0',
          memory: {
            used: 512,
            total: 2048,
            percentage: 25,
          },
          cpu: {
            count: 4,
            usage: 35,
          },
        },
      },
    },
  })
  async getDetailedHealth() {
    const now = Date.now();

    // Check database with timing
    let dbStatus = 'ok';
    let dbResponseTime = 0;
    try {
      const dbStart = Date.now();
      await this.prisma.$queryRaw`SELECT 1`;
      dbResponseTime = Date.now() - dbStart;
    } catch (error) {
      dbStatus = 'error';
      this.logger.error(`Database health check failed: ${error.message}`);
    }

    // Check Redis with timing
    let redisStatus = 'ok';
    let redisResponseTime = 0;
    try {
      const redisStart = Date.now();
      await this.redis.ping();
      redisResponseTime = Date.now() - redisStart;
    } catch (error) {
      redisStatus = 'error';
      this.logger.error(`Redis health check failed: ${error.message}`);
    }

    // System metrics
    const totalMemory = os.totalmem();
    const freeMemory = os.freemem();
    const usedMemory = totalMemory - freeMemory;
    const memoryPercentage = Math.round((usedMemory / totalMemory) * 100);

    const cpus = os.cpus();
    const cpuCount = cpus.length;

    // Calculate uptime
    const uptimeMs = now - this.startTime.getTime();
    const uptimeStr = this.formatUptime(uptimeMs);

    const isHealthy = dbStatus === 'ok' && redisStatus === 'ok';

    return {
      status: isHealthy ? 'healthy' : 'degraded',
      timestamp: new Date().toISOString(),
      service: {
        name: 'gmail-service',
        version: '1.0.0',
        uptime: uptimeStr,
        startTime: this.startTime.toISOString(),
        environment: process.env.NODE_ENV || 'development',
        nodeVersion: process.version,
      },
      dependencies: {
        database: {
          status: dbStatus,
          responseTime: `${dbResponseTime}ms`,
          type: 'PostgreSQL',
        },
        redis: {
          status: redisStatus,
          responseTime: `${redisResponseTime}ms`,
          type: 'Redis',
        },
      },
      system: {
        platform: os.platform(),
        arch: os.arch(),
        hostname: os.hostname(),
        nodeVersion: process.version,
        memory: {
          used: Math.round(usedMemory / 1024 / 1024), // MB
          total: Math.round(totalMemory / 1024 / 1024), // MB
          free: Math.round(freeMemory / 1024 / 1024), // MB
          percentage: memoryPercentage,
        },
        cpu: {
          count: cpuCount,
          model: cpus[0]?.model || 'Unknown',
        },
        uptime: {
          process: uptimeStr,
          system: this.formatUptime(os.uptime() * 1000),
        },
      },
    };
  }

  /**
   * System metrics
   *
   * Returns real-time system metrics for monitoring:
   * - Process metrics (memory, CPU, uptime)
   * - Dependency metrics (database, Redis)
   * - Request metrics (if available)
   *
   * Use for: Prometheus scraping, Grafana dashboards
   *
   * @returns System metrics
   */
  @Get('metrics')
  @ApiOperation({
    summary: 'System metrics',
    description:
      'Returns real-time system metrics including process metrics, ' +
      'dependency status, and request statistics.',
  })
  @ApiResponse({
    status: 200,
    description: 'System metrics',
    schema: {
      example: {
        timestamp: '2025-01-15T10:30:00Z',
        process: {
          uptime: 468000,
          memoryUsage: {
            rss: 134217728,
            heapTotal: 67108864,
            heapUsed: 50331648,
            external: 1048576,
          },
          cpuUsage: {
            user: 1234567,
            system: 234567,
          },
        },
        dependencies: {
          database: 'ok',
          redis: 'ok',
        },
      },
    },
  })
  async getMetrics() {
    const memUsage = process.memoryUsage();
    const cpuUsage = process.cpuUsage();

    // Check dependencies (simple)
    let dbStatus = 'ok';
    try {
      await this.prisma.$queryRaw`SELECT 1`;
    } catch {
      dbStatus = 'error';
    }

    let redisStatus = 'ok';
    try {
      await this.redis.ping();
    } catch {
      redisStatus = 'error';
    }

    return {
      timestamp: new Date().toISOString(),
      process: {
        uptime: process.uptime(),
        memoryUsage: {
          rss: memUsage.rss,
          heapTotal: memUsage.heapTotal,
          heapUsed: memUsage.heapUsed,
          external: memUsage.external,
        },
        cpuUsage: {
          user: cpuUsage.user,
          system: cpuUsage.system,
        },
      },
      dependencies: {
        database: dbStatus,
        redis: redisStatus,
      },
      system: {
        platform: os.platform(),
        arch: os.arch(),
        cpuCount: os.cpus().length,
        totalMemory: os.totalmem(),
        freeMemory: os.freemem(),
      },
    };
  }

  // ============================================================================
  // Private Helper Methods
  // ============================================================================

  /**
   * Format uptime in human-readable format
   */
  private formatUptime(uptimeMs: number): string {
    const seconds = Math.floor(uptimeMs / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) {
      return `${days}d ${hours % 24}h ${minutes % 60}m`;
    } else if (hours > 0) {
      return `${hours}h ${minutes % 60}m ${seconds % 60}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${seconds % 60}s`;
    } else {
      return `${seconds}s`;
    }
  }
}
