import {
  Controller,
  Get,
  Query,
  Param,
  Req,
  UseGuards,
  BadRequestException,
} from '@nestjs/common';
import { Request } from 'express';
import { GmailService, SearchEmailsDto } from './gmail.service';
import { AuthGuard } from '../auth/auth.guard';
import { QueryBuilderService } from './query-builder.service';
import { EmailTransformer } from './email.transformer';
import { RateLimitService } from './rate-limit.service';
import { SearchCacheService } from './search-cache.service';
import { EmailPreviewService } from './email-preview.service';
import { HtmlSanitizerService } from './html-sanitizer.service';
import { PreviewCacheService } from './preview-cache.service';

/**
 * Gmail Email Search Controller
 * Handles email search and retrieval endpoints
 */
@Controller('gmail')
@UseGuards(AuthGuard)
export class GmailController {
  constructor(
    private readonly gmailService: GmailService,
    private readonly queryBuilder: QueryBuilderService,
    private readonly emailTransformer: EmailTransformer,
    private readonly rateLimitService: RateLimitService,
    private readonly searchCacheService: SearchCacheService,
    private readonly emailPreviewService: EmailPreviewService,
    private readonly htmlSanitizer: HtmlSanitizerService,
    private readonly previewCache: PreviewCacheService,
  ) {}

  /**
   * Search emails with date range and filters
   * GET /api/v1/gmail/search
   *
   * Query Parameters:
   * - dateFrom: ISO 8601 date string (e.g., "2024-01-01")
   * - dateTo: ISO 8601 date string (e.g., "2024-12-31")
   * - hasAttachment: Boolean ("true" or "false")
   * - fromAddress: Email address to filter by sender
   * - subject: Subject keyword to search for
   * - maxResults: Number of results (1-500, default 50)
   * - pageToken: Pagination token from previous response
   */
  @Get('search')
  async searchEmails(
    @Req() req: Request,
    @Query('dateFrom') dateFrom?: string,
    @Query('dateTo') dateTo?: string,
    @Query('hasAttachment') hasAttachment?: string,
    @Query('fromAddress') fromAddress?: string,
    @Query('subject') subject?: string,
    @Query('maxResults') maxResults?: string,
    @Query('pageToken') pageToken?: string,
  ) {
    const sessionData = req.session as any;
    const userId = sessionData.userId;

    // Parse query parameters
    const searchParams: SearchEmailsDto = {};

    if (dateFrom) {
      const parsedFrom = this.queryBuilder.parseDateString(dateFrom);
      if (!parsedFrom) {
        throw new BadRequestException(`Invalid dateFrom format: ${dateFrom}`);
      }
      searchParams.dateFrom = parsedFrom;
    }

    if (dateTo) {
      const parsedTo = this.queryBuilder.parseDateString(dateTo);
      if (!parsedTo) {
        throw new BadRequestException(`Invalid dateTo format: ${dateTo}`);
      }
      searchParams.dateTo = parsedTo;
    }

    if (hasAttachment !== undefined) {
      searchParams.hasAttachment = hasAttachment === 'true';
    }

    if (fromAddress) {
      searchParams.fromAddress = fromAddress;
    }

    if (subject) {
      searchParams.subject = subject;
    }

    if (maxResults) {
      const parsed = parseInt(maxResults, 10);
      if (isNaN(parsed)) {
        throw new BadRequestException(`Invalid maxResults: ${maxResults}`);
      }
      searchParams.maxResults = parsed;
    }

    if (pageToken) {
      searchParams.pageToken = pageToken;
    }

    // Perform search
    const results = await this.gmailService.searchEmails(userId, searchParams);

    return {
      success: true,
      data: results,
      query: searchParams,
    };
  }

  /**
   * Get single email by ID
   * GET /api/v1/gmail/emails/:emailId
   */
  @Get('emails/:emailId')
  async getEmail(@Req() req: Request, @Param('emailId') emailId: string) {
    const sessionData = req.session as any;
    const userId = sessionData.userId;

    const email = await this.gmailService.getEmailById(userId, emailId);

    return {
      success: true,
      data: email,
    };
  }

  /**
   * Get full email preview with body content and sanitized HTML
   * GET /api/v1/gmail/emails/:emailId/preview
   * Implements FR-018: Email Preview
   */
  @Get('emails/:emailId/preview')
  async getEmailPreview(
    @Req() req: Request,
    @Param('emailId') emailId: string,
    @Query('sanitize') sanitize?: string,
  ) {
    const sessionData = req.session as any;
    const userId = sessionData.userId;

    // Check cache first
    let preview = await this.previewCache.getEmailPreview(userId, emailId);

    if (!preview) {
      // Fetch from Gmail API
      preview = await this.emailPreviewService.getEmailPreview(userId, emailId);

      // Cache the preview
      await this.previewCache.setEmailPreview(userId, emailId, preview);
    }

    // Sanitize HTML if requested (default: true)
    const shouldSanitize = sanitize !== 'false';
    if (shouldSanitize && preview.body.html) {
      preview.body.html = this.htmlSanitizer.sanitizeHtml(preview.body.html);
    }

    // Check if email is CV-related
    const isCVEmail = this.emailPreviewService.isCVEmail(preview);

    return {
      success: true,
      data: {
        ...preview,
        isCVEmail,
        cached: !!preview,
      },
    };
  }

  /**
   * Get thread preview (all messages in conversation)
   * GET /api/v1/gmail/threads/:threadId/preview
   */
  @Get('threads/:threadId/preview')
  async getThreadPreview(
    @Req() req: Request,
    @Param('threadId') threadId: string,
    @Query('sanitize') sanitize?: string,
  ) {
    const sessionData = req.session as any;
    const userId = sessionData.userId;

    // Check cache first
    let previews = await this.previewCache.getThreadPreview(userId, threadId);

    if (!previews) {
      // Fetch from Gmail API
      previews = await this.emailPreviewService.getThreadPreview(userId, threadId);

      // Cache the previews
      await this.previewCache.setThreadPreview(userId, threadId, previews);
    }

    // Sanitize HTML if requested (default: true)
    const shouldSanitize = sanitize !== 'false';
    if (shouldSanitize) {
      for (const preview of previews) {
        if (preview.body.html) {
          preview.body.html = this.htmlSanitizer.sanitizeHtml(preview.body.html);
        }
      }
    }

    return {
      success: true,
      data: {
        threadId,
        messageCount: previews.length,
        messages: previews,
      },
    };
  }

  /**
   * Extract plain text from HTML email
   * GET /api/v1/gmail/emails/:emailId/text
   */
  @Get('emails/:emailId/text')
  async getEmailText(
    @Req() req: Request,
    @Param('emailId') emailId: string,
  ) {
    const sessionData = req.session as any;
    const userId = sessionData.userId;

    // Get preview (from cache or API)
    let preview = await this.previewCache.getEmailPreview(userId, emailId);

    if (!preview) {
      preview = await this.emailPreviewService.getEmailPreview(userId, emailId);
      await this.previewCache.setEmailPreview(userId, emailId, preview);
    }

    // Extract plain text
    let plainText = preview.body.text || '';

    // If no text but HTML exists, extract text from HTML
    if (!plainText && preview.body.html) {
      plainText = this.htmlSanitizer.extractPlainText(preview.body.html);
    }

    return {
      success: true,
      data: {
        emailId: preview.id,
        from: preview.from,
        subject: preview.subject,
        date: preview.date,
        text: plainText,
      },
    };
  }

  /**
   * Get email count for date range
   * GET /api/v1/gmail/count
   */
  @Get('count')
  async getEmailCount(
    @Req() req: Request,
    @Query('dateFrom') dateFrom?: string,
    @Query('dateTo') dateTo?: string,
  ) {
    const sessionData = req.session as any;
    const userId = sessionData.userId;

    let parsedFrom: Date | undefined;
    let parsedTo: Date | undefined;

    if (dateFrom) {
      parsedFrom = this.queryBuilder.parseDateString(dateFrom);
      if (!parsedFrom) {
        throw new BadRequestException(`Invalid dateFrom format: ${dateFrom}`);
      }
    }

    if (dateTo) {
      parsedTo = this.queryBuilder.parseDateString(dateTo);
      if (!parsedTo) {
        throw new BadRequestException(`Invalid dateTo format: ${dateTo}`);
      }
    }

    const count = await this.gmailService.getEmailCount(
      userId,
      parsedFrom,
      parsedTo,
    );

    return {
      success: true,
      data: {
        count,
        dateFrom: parsedFrom,
        dateTo: parsedTo,
      },
    };
  }

  /**
   * Search CV emails (emails with CV attachments)
   * GET /api/v1/gmail/search/cv
   */
  @Get('search/cv')
  async searchCVEmails(
    @Req() req: Request,
    @Query('dateFrom') dateFrom?: string,
    @Query('dateTo') dateTo?: string,
    @Query('maxResults') maxResults?: string,
    @Query('pageToken') pageToken?: string,
  ) {
    const sessionData = req.session as any;
    const userId = sessionData.userId;

    // Parse dates
    let parsedFrom: Date | undefined;
    let parsedTo: Date | undefined;

    if (dateFrom) {
      parsedFrom = this.queryBuilder.parseDateString(dateFrom);
      if (!parsedFrom) {
        throw new BadRequestException(`Invalid dateFrom format: ${dateFrom}`);
      }
    }

    if (dateTo) {
      parsedTo = this.queryBuilder.parseDateString(dateTo);
      if (!parsedTo) {
        throw new BadRequestException(`Invalid dateTo format: ${dateTo}`);
      }
    }

    // Build CV-specific query
    const cvQuery = this.queryBuilder.buildCVAttachmentQuery(
      parsedFrom,
      parsedTo,
    );

    // Search with custom query
    const searchParams: SearchEmailsDto = {
      dateFrom: parsedFrom,
      dateTo: parsedTo,
      hasAttachment: true,
      maxResults: maxResults ? parseInt(maxResults, 10) : undefined,
      pageToken,
    };

    const results = await this.gmailService.searchEmails(userId, searchParams);

    // Filter results to only include likely CV emails
    const cvEmails = results.emails.filter((email) =>
      this.emailTransformer.isCVEmail(email),
    );

    return {
      success: true,
      data: {
        ...results,
        emails: cvEmails,
        totalCVEmails: cvEmails.length,
      },
      query: {
        dateFrom: parsedFrom,
        dateTo: parsedTo,
        cvQuery,
      },
    };
  }

  /**
   * Get rate limit status
   * GET /api/v1/gmail/rate-limit
   */
  @Get('rate-limit')
  async getRateLimitStatus(@Req() req: Request) {
    const sessionData = req.session as any;
    const userId = sessionData.userId;

    const stats = await this.rateLimitService.getRateLimitStats(userId);

    return {
      success: true,
      data: stats,
    };
  }

  /**
   * Get cache statistics
   * GET /api/v1/gmail/cache-stats
   */
  @Get('cache-stats')
  async getCacheStats(@Req() req: Request) {
    const sessionData = req.session as any;
    const userId = sessionData.userId;

    const stats = await this.searchCacheService.getCacheStats(userId);

    return {
      success: true,
      data: stats,
    };
  }

  /**
   * Invalidate user's search cache
   * POST /api/v1/gmail/cache/invalidate
   */
  @Get('cache/invalidate')
  async invalidateCache(@Req() req: Request) {
    const sessionData = req.session as any;
    const userId = sessionData.userId;

    await this.searchCacheService.invalidateUserCache(userId);

    return {
      success: true,
      message: 'Cache invalidated successfully',
    };
  }

  /**
   * Get preview cache statistics
   * GET /api/v1/gmail/preview-cache/stats
   */
  @Get('preview-cache/stats')
  async getPreviewCacheStats(@Req() req: Request) {
    const sessionData = req.session as any;
    const userId = sessionData.userId;

    const stats = await this.previewCache.getCacheStats(userId);

    return {
      success: true,
      data: stats,
    };
  }

  /**
   * Invalidate email preview cache
   * POST /api/v1/gmail/preview-cache/invalidate/:emailId
   */
  @Get('preview-cache/invalidate/:emailId')
  async invalidateEmailPreview(
    @Req() req: Request,
    @Param('emailId') emailId: string,
  ) {
    const sessionData = req.session as any;
    const userId = sessionData.userId;

    await this.previewCache.invalidateEmailPreview(userId, emailId);

    return {
      success: true,
      message: `Preview cache invalidated for email ${emailId}`,
    };
  }

  /**
   * Invalidate all preview caches for user
   * POST /api/v1/gmail/preview-cache/invalidate-all
   */
  @Get('preview-cache/invalidate-all')
  async invalidateAllPreviews(@Req() req: Request) {
    const sessionData = req.session as any;
    const userId = sessionData.userId;

    await this.previewCache.invalidateUserPreviews(userId);

    return {
      success: true,
      message: 'All preview caches invalidated',
    };
  }

  /**
   * Health check endpoint
   * GET /api/v1/gmail/health
   */
  @Get('health')
  async healthCheck() {
    return {
      success: true,
      service: 'gmail-service',
      timestamp: new Date().toISOString(),
      status: 'healthy',
    };
  }
}
