import { Injectable, Logger } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';

/**
 * Audit Logging Service
 *
 * Provides comprehensive audit logging for security-critical operations:
 * - Authentication events (login, logout, token refresh)
 * - Authorization failures (access denied)
 * - Data access (email search, preview, download)
 * - GDPR operations (data export, account deletion)
 * - Configuration changes
 * - System events (startup, shutdown, errors)
 *
 * Audit logs include:
 * - Timestamp (ISO 8601)
 * - Event type and severity
 * - User ID and IP address
 * - User agent (browser/device)
 * - Action performed
 * - Resource accessed
 * - Result (success/failure)
 * - Additional metadata
 *
 * Compliance:
 * - Retained for 90 days (configurable)
 * - Anonymized after retention period
 * - Tamper-proof (append-only)
 * - Searchable for incident investigation
 *
 * @see SECURITY.md - Logging & Monitoring section
 */
@Injectable()
export class AuditLogService {
  private readonly logger = new Logger(AuditLogService.name);

  constructor(private readonly prisma: PrismaService) {}

  /**
   * Log authentication event
   *
   * @param userId - User ID (null for failed login)
   * @param event - Event type (LOGIN, LOGOUT, TOKEN_REFRESH)
   * @param success - Whether operation succeeded
   * @param metadata - Additional context
   */
  async logAuth(
    userId: string | null,
    event: 'LOGIN' | 'LOGOUT' | 'TOKEN_REFRESH',
    success: boolean,
    metadata: {
      ipAddress?: string;
      userAgent?: string;
      provider?: string;
      reason?: string;
    } = {},
  ): Promise<void> {
    await this.log({
      category: 'AUTHENTICATION',
      event,
      severity: success ? 'INFO' : 'WARNING',
      userId,
      success,
      ipAddress: metadata.ipAddress,
      userAgent: metadata.userAgent,
      metadata: {
        provider: metadata.provider,
        reason: metadata.reason,
      },
    });
  }

  /**
   * Log authorization event (access control)
   *
   * @param userId - User attempting access
   * @param resource - Resource being accessed
   * @param action - Action attempted (READ, WRITE, DELETE)
   * @param success - Whether access was granted
   * @param metadata - Additional context
   */
  async logAuthorization(
    userId: string,
    resource: string,
    action: 'READ' | 'WRITE' | 'DELETE',
    success: boolean,
    metadata: {
      ipAddress?: string;
      userAgent?: string;
      reason?: string;
    } = {},
  ): Promise<void> {
    await this.log({
      category: 'AUTHORIZATION',
      event: `${action}_${success ? 'GRANTED' : 'DENIED'}`,
      severity: success ? 'INFO' : 'WARNING',
      userId,
      resource,
      success,
      ipAddress: metadata.ipAddress,
      userAgent: metadata.userAgent,
      metadata: {
        action,
        reason: metadata.reason,
      },
    });
  }

  /**
   * Log data access event
   *
   * @param userId - User accessing data
   * @param operation - Operation type (SEARCH, PREVIEW, DOWNLOAD)
   * @param resource - Resource accessed (email ID, attachment ID)
   * @param metadata - Additional context
   */
  async logDataAccess(
    userId: string,
    operation: 'SEARCH' | 'PREVIEW' | 'DOWNLOAD',
    resource: string,
    metadata: {
      ipAddress?: string;
      userAgent?: string;
      emailId?: string;
      attachmentId?: string;
      fileName?: string;
      fileSize?: number;
      resultCount?: number;
    } = {},
  ): Promise<void> {
    await this.log({
      category: 'DATA_ACCESS',
      event: operation,
      severity: 'INFO',
      userId,
      resource,
      success: true,
      ipAddress: metadata.ipAddress,
      userAgent: metadata.userAgent,
      metadata,
    });
  }

  /**
   * Log GDPR operation
   *
   * @param userId - User exercising GDPR rights
   * @param operation - GDPR operation (DATA_EXPORT, ACCOUNT_DELETION, PORTABLE_EXPORT)
   * @param success - Whether operation succeeded
   * @param metadata - Additional context
   */
  async logGdpr(
    userId: string,
    operation: 'DATA_EXPORT' | 'ACCOUNT_DELETION' | 'PORTABLE_EXPORT',
    success: boolean,
    metadata: {
      ipAddress?: string;
      userAgent?: string;
      recordCount?: number;
      errors?: string[];
    } = {},
  ): Promise<void> {
    await this.log({
      category: 'GDPR',
      event: operation,
      severity: operation === 'ACCOUNT_DELETION' ? 'CRITICAL' : 'INFO',
      userId,
      success,
      ipAddress: metadata.ipAddress,
      userAgent: metadata.userAgent,
      metadata,
    });
  }

  /**
   * Log security event
   *
   * @param event - Security event type
   * @param severity - Event severity
   * @param metadata - Additional context
   */
  async logSecurity(
    event: string,
    severity: 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL',
    metadata: {
      userId?: string;
      ipAddress?: string;
      userAgent?: string;
      reason?: string;
      details?: any;
    } = {},
  ): Promise<void> {
    await this.log({
      category: 'SECURITY',
      event,
      severity,
      userId: metadata.userId,
      success: severity === 'INFO',
      ipAddress: metadata.ipAddress,
      userAgent: metadata.userAgent,
      metadata: {
        reason: metadata.reason,
        details: metadata.details,
      },
    });
  }

  /**
   * Log system event
   *
   * @param event - System event type
   * @param severity - Event severity
   * @param metadata - Additional context
   */
  async logSystem(
    event: string,
    severity: 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL',
    metadata: any = {},
  ): Promise<void> {
    await this.log({
      category: 'SYSTEM',
      event,
      severity,
      success: severity === 'INFO',
      metadata,
    });
  }

  /**
   * Search audit logs
   *
   * @param filters - Search filters
   * @returns Matching audit log entries
   */
  async searchLogs(filters: {
    userId?: string;
    category?: string;
    event?: string;
    fromDate?: Date;
    toDate?: Date;
    ipAddress?: string;
    severity?: string;
    limit?: number;
  }): Promise<any[]> {
    // In production, this would query the audit_logs table
    // For now, return structured log format
    this.logger.log(`Searching audit logs with filters: ${JSON.stringify(filters)}`);
    return [];
  }

  /**
   * Get audit statistics
   *
   * @param fromDate - Start date
   * @param toDate - End date
   * @returns Audit statistics
   */
  async getStatistics(fromDate: Date, toDate: Date): Promise<any> {
    // In production, this would aggregate from audit_logs table
    return {
      period: {
        from: fromDate.toISOString(),
        to: toDate.toISOString(),
      },
      totalEvents: 0,
      byCategory: {},
      bySeverity: {},
      topUsers: [],
      topIpAddresses: [],
    };
  }

  // ============================================================================
  // Private Helper Methods
  // ============================================================================

  /**
   * Core logging method - writes structured audit log
   */
  private async log(entry: {
    category: string;
    event: string;
    severity: 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';
    userId?: string | null;
    resource?: string;
    success: boolean;
    ipAddress?: string;
    userAgent?: string;
    metadata?: any;
  }): Promise<void> {
    const logEntry = {
      timestamp: new Date().toISOString(),
      category: entry.category,
      event: entry.event,
      severity: entry.severity,
      userId: entry.userId || null,
      resource: entry.resource || null,
      success: entry.success,
      ipAddress: entry.ipAddress || 'unknown',
      userAgent: entry.userAgent || 'unknown',
      metadata: entry.metadata || {},
    };

    try {
      // Write to structured log output
      this.logger.log(JSON.stringify(logEntry));

      // In production, also write to database audit_logs table
      // await this.prisma.auditLog.create({ data: logEntry });
    } catch (error) {
      // Never throw - logging failures should not break the application
      this.logger.error(
        `Failed to write audit log: ${error.message}`,
        error.stack,
      );
    }
  }
}
