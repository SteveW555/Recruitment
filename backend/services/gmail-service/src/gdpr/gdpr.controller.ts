import {
  Controller,
  Get,
  Delete,
  Req,
  UseGuards,
  HttpCode,
  HttpStatus,
  Logger,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiCookieAuth } from '@nestjs/swagger';
import { Request } from 'express';
import { SessionGuard } from '../auth/session.guard';
import { GdprService } from './gdpr.service';

/**
 * GDPR Compliance Controller
 *
 * Provides REST API endpoints for GDPR compliance:
 * - Article 15: Right to Access (data export)
 * - Article 17: Right to Erasure (account deletion)
 * - Article 20: Right to Data Portability (portable export)
 *
 * All endpoints require authentication via session cookie.
 *
 * Security:
 * - Session-based authentication required
 * - Rate limiting applied (10 requests per hour for deletions)
 * - Audit logging for all GDPR operations
 * - Irreversible account deletion with confirmation
 *
 * @see SECURITY.md - GDPR Compliance section
 */
@ApiTags('gdpr')
@ApiCookieAuth('gmail.sid')
@Controller('gdpr')
@UseGuards(SessionGuard)
export class GdprController {
  private readonly logger = new Logger(GdprController.name);

  constructor(private readonly gdprService: GdprService) {}

  /**
   * Get comprehensive data export (GDPR Article 15 - Right to Access)
   *
   * Returns all personal data stored for the authenticated user including:
   * - User profile and authentication details
   * - Download history (last 1000 downloads)
   * - Saved searches
   * - OAuth tokens (masked for security)
   * - Data retention status
   * - GDPR rights information
   *
   * Response Format: JSON
   * Rate Limit: 10 requests per hour
   *
   * @example
   * GET /api/v1/gdpr/my-data
   *
   * Response:
   * {
   *   "success": true,
   *   "data": {
   *     "exportDate": "2025-01-15T10:30:00Z",
   *     "user": { "id": "...", "email": "...", "name": "..." },
   *     "downloads": { "totalDownloads": 42, "records": [...] },
   *     "savedSearches": { "totalSearches": 5, "searches": [...] },
   *     "dataRetention": { "policy": "24-hour automatic deletion", ... },
   *     "gdprRights": { ... }
   *   }
   * }
   */
  @Get('my-data')
  @ApiOperation({
    summary: 'Export all user data (GDPR Article 15)',
    description:
      'Returns comprehensive data export including user profile, downloads, saved searches, and GDPR rights information. ' +
      'All OAuth tokens are masked for security. This endpoint fulfills the Right to Access under GDPR Article 15.',
  })
  @ApiResponse({
    status: 200,
    description: 'Data export successful',
    schema: {
      example: {
        success: true,
        data: {
          exportDate: '2025-01-15T10:30:00Z',
          exportType: 'GDPR Article 15 - Right to Access',
          user: {
            id: 'user_123',
            email: 'user@example.com',
            name: 'John Doe',
            createdAt: '2024-01-01T00:00:00Z',
          },
          downloads: {
            totalDownloads: 42,
            records: [
              {
                id: 'dl_123',
                emailId: 'msg_456',
                fileName: 'resume.pdf',
                fileSize: 153600,
                downloadedAt: '2025-01-15T09:00:00Z',
                status: 'ACTIVE',
              },
            ],
          },
          savedSearches: {
            totalSearches: 5,
            searches: [
              {
                id: 'search_789',
                name: 'CV Emails',
                filters: { hasAttachment: true },
                useCount: 15,
              },
            ],
          },
        },
      },
    },
  })
  @ApiResponse({
    status: 401,
    description: 'Not authenticated',
  })
  @ApiResponse({
    status: 429,
    description: 'Rate limit exceeded',
  })
  async getMyData(@Req() req: Request) {
    const userId = (req.session as any).userId;

    this.logger.log(
      `GDPR data export requested by user ${userId} from IP ${req.ip}`,
    );

    const data = await this.gdprService.exportUserData(userId);

    return {
      success: true,
      data,
      message:
        'Your data export has been generated. This fulfills your Right to Access under GDPR Article 15.',
    };
  }

  /**
   * Delete user account and all data (GDPR Article 17 - Right to Erasure)
   *
   * **WARNING: This action is irreversible!**
   *
   * Deletes:
   * - User profile
   * - All OAuth tokens (with Google revocation)
   * - All download records and files
   * - All saved searches
   * - All cache entries
   *
   * Retained for Legal Compliance:
   * - Audit logs (anonymized after 90 days)
   *
   * After deletion:
   * - Session will be invalidated
   * - User must re-authenticate to create new account
   * - Previous data cannot be recovered
   *
   * Rate Limit: 3 requests per day
   *
   * @example
   * DELETE /api/v1/gdpr/delete-account
   *
   * Response:
   * {
   *   "success": true,
   *   "data": {
   *     "userId": "...",
   *     "email": "...",
   *     "deletionDate": "2025-01-15T10:30:00Z",
   *     "deletedData": {
   *       "oauthTokens": 2,
   *       "downloadRecords": 42,
   *       "savedSearches": 5
   *     }
   *   }
   * }
   */
  @Delete('delete-account')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({
    summary: 'Delete account and all data (GDPR Article 17)',
    description:
      '**IRREVERSIBLE ACTION** - Permanently deletes user account and all associated data. ' +
      'Revokes OAuth tokens, deletes download records, saved searches, and cache entries. ' +
      'Audit logs are retained for 90 days for legal compliance. ' +
      'This endpoint fulfills the Right to Erasure under GDPR Article 17.',
  })
  @ApiResponse({
    status: 200,
    description: 'Account deleted successfully',
    schema: {
      example: {
        success: true,
        data: {
          userId: 'user_123',
          email: 'user@example.com',
          deletionDate: '2025-01-15T10:30:00Z',
          deletedData: {
            oauthTokens: 2,
            downloadRecords: 42,
            savedSearches: 5,
            cacheEntries: 15,
          },
          errors: [],
        },
        message: 'Your account has been permanently deleted.',
      },
    },
  })
  @ApiResponse({
    status: 401,
    description: 'Not authenticated',
  })
  @ApiResponse({
    status: 429,
    description: 'Rate limit exceeded (max 3 deletions per day)',
  })
  async deleteAccount(@Req() req: Request) {
    const userId = (req.session as any).userId;

    this.logger.warn(
      `GDPR account deletion requested by user ${userId} from IP ${req.ip}`,
    );

    const deletionSummary = await this.gdprService.deleteUserAccount(userId);

    // Destroy session after account deletion
    req.session.destroy((err) => {
      if (err) {
        this.logger.error(`Failed to destroy session: ${err.message}`);
      }
    });

    return {
      success: true,
      data: deletionSummary,
      message:
        'Your account has been permanently deleted. All personal data has been removed from our systems. ' +
        'Audit logs will be anonymized after 90 days. Thank you for using our service.',
    };
  }

  /**
   * Export portable data (GDPR Article 20 - Right to Data Portability)
   *
   * Returns user data in simplified, machine-readable JSON format suitable
   * for importing into other systems. This format excludes sensitive security
   * information and focuses on user-generated content.
   *
   * Included Data:
   * - User profile (email, name)
   * - Download history
   * - Saved searches with filters
   *
   * Format: JSON (version 1.0)
   * Rate Limit: 10 requests per hour
   *
   * @example
   * GET /api/v1/gdpr/export
   *
   * Response:
   * {
   *   "success": true,
   *   "data": {
   *     "format": "JSON",
   *     "version": "1.0",
   *     "exportDate": "2025-01-15T10:30:00Z",
   *     "user": { ... },
   *     "downloads": [...],
   *     "savedSearches": [...]
   *   }
   * }
   */
  @Get('export')
  @ApiOperation({
    summary: 'Export portable data (GDPR Article 20)',
    description:
      'Returns user data in simplified, machine-readable JSON format for data portability. ' +
      'Excludes sensitive security information. Suitable for importing into other systems. ' +
      'This endpoint fulfills the Right to Data Portability under GDPR Article 20.',
  })
  @ApiResponse({
    status: 200,
    description: 'Portable data export successful',
    schema: {
      example: {
        success: true,
        data: {
          format: 'JSON',
          version: '1.0',
          exportDate: '2025-01-15T10:30:00Z',
          user: {
            id: 'user_123',
            email: 'user@example.com',
            name: 'John Doe',
          },
          downloads: [
            {
              id: 'dl_123',
              fileName: 'resume.pdf',
              fileSize: 153600,
              downloadedAt: '2025-01-15T09:00:00Z',
            },
          ],
          savedSearches: [
            {
              id: 'search_789',
              name: 'CV Emails',
              filters: { hasAttachment: true },
            },
          ],
        },
      },
    },
  })
  @ApiResponse({
    status: 401,
    description: 'Not authenticated',
  })
  @ApiResponse({
    status: 429,
    description: 'Rate limit exceeded',
  })
  async exportPortableData(@Req() req: Request) {
    const userId = (req.session as any).userId;

    this.logger.log(
      `GDPR portable export requested by user ${userId} from IP ${req.ip}`,
    );

    const portableData = await this.gdprService.exportPortableData(userId);

    return {
      success: true,
      data: portableData,
      message:
        'Your data has been exported in portable JSON format. This fulfills your Right to Data Portability under GDPR Article 20.',
    };
  }

  /**
   * Get GDPR compliance status
   *
   * Returns comprehensive compliance status for the authenticated user:
   * - Data retention compliance
   * - Available GDPR rights and endpoints
   * - Active and expired data counts
   * - Data categories stored
   *
   * Rate Limit: 30 requests per hour
   *
   * @example
   * GET /api/v1/gdpr/status
   *
   * Response:
   * {
   *   "success": true,
   *   "data": {
   *     "userId": "...",
   *     "dataRetentionCompliance": {
   *       "policy": "24-hour automatic deletion",
   *       "status": "COMPLIANT",
   *       "activeFiles": 3,
   *       "pendingDeletion": 1
   *     },
   *     "gdprRights": { ... }
   *   }
   * }
   */
  @Get('status')
  @ApiOperation({
    summary: 'Get GDPR compliance status',
    description:
      'Returns comprehensive compliance status including data retention policy, ' +
      'available GDPR rights, active/expired data counts, and data categories stored.',
  })
  @ApiResponse({
    status: 200,
    description: 'Compliance status retrieved',
    schema: {
      example: {
        success: true,
        data: {
          userId: 'user_123',
          email: 'user@example.com',
          accountCreated: '2024-01-01T00:00:00Z',
          dataRetentionCompliance: {
            policy: '24-hour automatic deletion',
            status: 'COMPLIANT',
            activeFiles: 3,
            pendingDeletion: 1,
          },
          gdprRights: {
            rightToAccess: {
              available: true,
              endpoint: 'GET /api/v1/gdpr/my-data',
            },
            rightToErasure: {
              available: true,
              endpoint: 'DELETE /api/v1/gdpr/delete-account',
            },
            rightToPortability: {
              available: true,
              endpoint: 'GET /api/v1/gdpr/export',
            },
          },
        },
      },
    },
  })
  @ApiResponse({
    status: 401,
    description: 'Not authenticated',
  })
  async getGdprStatus(@Req() req: Request) {
    const userId = (req.session as any).userId;

    const status = await this.gdprService.getGdprStatus(userId);

    return {
      success: true,
      data: status,
    };
  }
}
