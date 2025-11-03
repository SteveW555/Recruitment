import { Injectable } from '@nestjs/common';
import { PrismaClient } from '@prisma/client';

export enum AuditAction {
  // Authentication
  OAUTH_INITIATED = 'oauth_initiated',
  OAUTH_COMPLETED = 'oauth_completed',
  OAUTH_FAILED = 'oauth_failed',
  OAUTH_REVOKED = 'oauth_revoked',
  TOKEN_REFRESHED = 'token_refreshed',

  // Search
  SEARCH_EMAILS = 'search_emails',
  VIEW_EMAIL = 'view_email',

  // Attachments
  VIEW_ATTACHMENT = 'view_attachment',
  DOWNLOAD_ATTACHMENT = 'download_attachment',
  BULK_DOWNLOAD = 'bulk_download',

  // File Management
  FILE_DELETED = 'file_deleted',
  FILE_CLEANUP_FAILED = 'file_cleanup_failed',

  // Admin
  USER_CREATED = 'user_created',
  USER_DELETED = 'user_deleted',
}

interface AuditLogEntry {
  userId: string | null;
  action: string;
  resourceType?: string | null;
  resourceId?: string | null;
  metadata?: any;
  ipAddress: string;
  userAgent: string;
}

/**
 * Audit logging service for compliance and security
 * Logs all security-relevant actions immutably
 */
@Injectable()
export class AuditService {
  private prisma: PrismaClient;

  constructor() {
    this.prisma = new PrismaClient();
  }

  async onModuleDestroy() {
    await this.prisma.$disconnect();
  }

  /**
   * Log an audit event
   * @param entry - Audit log entry
   */
  async log(entry: AuditLogEntry): Promise<void> {
    try {
      await this.prisma.auditLog.create({
        data: {
          userId: entry.userId,
          action: entry.action,
          resourceType: entry.resourceType || null,
          resourceId: entry.resourceId || null,
          metadata: entry.metadata || {},
          ipAddress: entry.ipAddress,
          userAgent: entry.userAgent,
        },
      });

      // Also log to console for monitoring
      console.log('[AUDIT]', {
        timestamp: new Date().toISOString(),
        userId: entry.userId || 'system',
        action: entry.action,
        resourceType: entry.resourceType,
        resourceId: entry.resourceId,
      });
    } catch (error) {
      // Audit logging failures should not break application flow
      console.error('Audit logging failed:', error);
    }
  }

  /**
   * Get audit logs for a user
   * @param userId - User ID
   * @param limit - Number of logs to retrieve
   */
  async getUserLogs(userId: string, limit: number = 100) {
    return this.prisma.auditLog.findMany({
      where: { userId },
      orderBy: { createdAt: 'desc' },
      take: limit,
    });
  }

  /**
   * Get audit logs by action type
   * @param action - Action type
   * @param limit - Number of logs to retrieve
   */
  async getLogsByAction(action: string, limit: number = 100) {
    return this.prisma.auditLog.findMany({
      where: { action },
      orderBy: { createdAt: 'desc' },
      take: limit,
    });
  }

  /**
   * Get recent audit logs (last 24 hours)
   */
  async getRecentLogs(limit: number = 100) {
    const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);

    return this.prisma.auditLog.findMany({
      where: {
        createdAt: { gte: oneDayAgo },
      },
      orderBy: { createdAt: 'desc' },
      take: limit,
    });
  }
}
