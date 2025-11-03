import { Injectable, Logger, BadRequestException } from '@nestjs/common';
import { gmail_v1 } from 'googleapis';
import { GmailClientService } from './gmail-client.service';
import { GmailAuthHelper } from './gmail-auth.helper';
import { QueryBuilderService } from './query-builder.service';
import { EmailTransformer } from './email.transformer';
import { SearchCacheService } from './search-cache.service';
import { RateLimitService } from './rate-limit.service';
import { UserRepository } from '../auth/user.repository';
import { AuditService } from '../audit/audit.service';

export interface SearchEmailsDto {
  dateFrom?: Date;
  dateTo?: Date;
  hasAttachment?: boolean;
  fromAddress?: string;
  subject?: string;
  maxResults?: number;
  pageToken?: string;
}

export interface SearchEmailsResult {
  emails: any[];
  nextPageToken?: string;
  totalResults?: number;
  hasMore: boolean;
  cached: boolean;
}

/**
 * Gmail Email Search Service
 * Handles email search with date range queries, pagination, and caching
 */
@Injectable()
export class GmailService {
  private readonly logger = new Logger(GmailService.name);
  private readonly DEFAULT_MAX_RESULTS = 50;
  private readonly MAX_RESULTS_LIMIT = 500;

  constructor(
    private readonly gmailClient: GmailClientService,
    private readonly gmailAuthHelper: GmailAuthHelper,
    private readonly queryBuilder: QueryBuilderService,
    private readonly emailTransformer: EmailTransformer,
    private readonly searchCache: SearchCacheService,
    private readonly rateLimitService: RateLimitService,
    private readonly userRepository: UserRepository,
    private readonly auditService: AuditService,
  ) {}

  /**
   * Search emails with date range and filters
   * @param userId - User ID
   * @param searchParams - Search parameters
   * @returns Search results with pagination
   */
  async searchEmails(
    userId: string,
    searchParams: SearchEmailsDto,
  ): Promise<SearchEmailsResult> {
    // Validate authentication
    await this.gmailAuthHelper.validateGmailAuth(userId);

    // Validate search parameters
    this.validateSearchParams(searchParams);

    // Build Gmail query string
    const queryString = this.queryBuilder.buildQuery(searchParams);

    // Check cache first (if not using pagination)
    if (!searchParams.pageToken) {
      const cachedResults = await this.searchCache.getCachedSearch(
        userId,
        queryString,
      );

      if (cachedResults) {
        this.logger.log(`Cache hit for user ${userId}, query: ${queryString}`);
        return {
          ...cachedResults,
          cached: true,
        };
      }
    }

    // Check rate limit
    await this.rateLimitService.checkRateLimit(userId);

    const maxResults = Math.min(
      searchParams.maxResults || this.DEFAULT_MAX_RESULTS,
      this.MAX_RESULTS_LIMIT,
    );

    try {
      // Search Gmail API
      const searchStart = Date.now();
      const listResponse = await this.gmailClient.listMessages(
        userId,
        queryString,
        maxResults,
        searchParams.pageToken,
      );

      const searchDuration = Date.now() - searchStart;
      this.logger.log(
        `Gmail API search completed in ${searchDuration}ms for user ${userId}`,
      );

      // If no results, return early
      if (!listResponse.messages || listResponse.messages.length === 0) {
        const emptyResult = {
          emails: [],
          totalResults: 0,
          hasMore: false,
          cached: false,
        };

        // Cache empty result
        await this.searchCache.cacheSearch(userId, queryString, emptyResult);

        // Log search query
        await this.logSearchQuery(userId, searchParams, 0, searchDuration);

        return emptyResult;
      }

      // Get message IDs
      const messageIds = listResponse.messages.map((msg) => msg.id);

      // Fetch full message details
      const fetchStart = Date.now();
      const fullMessages = await this.gmailClient.getMessagesBatch(
        userId,
        messageIds,
        'full',
      );

      const fetchDuration = Date.now() - fetchStart;
      this.logger.log(
        `Fetched ${fullMessages.length} messages in ${fetchDuration}ms`,
      );

      // Transform messages to internal model
      const transformedEmails = fullMessages.map((msg) =>
        this.emailTransformer.transformEmail(msg),
      );

      const result: SearchEmailsResult = {
        emails: transformedEmails,
        nextPageToken: listResponse.nextPageToken,
        totalResults: listResponse.resultSizeEstimate,
        hasMore: !!listResponse.nextPageToken,
        cached: false,
      };

      // Cache results (only first page)
      if (!searchParams.pageToken) {
        await this.searchCache.cacheSearch(userId, queryString, result);
      }

      // Log search query
      await this.logSearchQuery(
        userId,
        searchParams,
        transformedEmails.length,
        searchDuration + fetchDuration,
      );

      return result;
    } catch (error) {
      this.logger.error(
        `Email search failed for user ${userId}: ${error.message}`,
        error.stack,
      );

      // Handle rate limiting with exponential backoff
      if (error.message?.includes('rate limit')) {
        return await this.rateLimitService.handleRateLimitWithRetry(
          userId,
          () => this.searchEmails(userId, searchParams),
        );
      }

      // Handle other errors
      this.gmailAuthHelper.handleGmailApiError(error, userId);
    }
  }

  /**
   * Get single email by ID
   * @param userId - User ID
   * @param emailId - Gmail message ID
   * @returns Email details
   */
  async getEmailById(userId: string, emailId: string): Promise<any> {
    await this.gmailAuthHelper.validateGmailAuth(userId);

    try {
      const message = await this.gmailClient.getMessage(userId, emailId, 'full');
      return this.emailTransformer.transformEmail(message);
    } catch (error) {
      this.logger.error(
        `Failed to get email ${emailId} for user ${userId}: ${error.message}`,
      );
      this.gmailAuthHelper.handleGmailApiError(error, userId);
    }
  }

  /**
   * Get email count for date range
   * @param userId - User ID
   * @param dateFrom - Start date
   * @param dateTo - End date
   * @returns Estimated count
   */
  async getEmailCount(
    userId: string,
    dateFrom?: Date,
    dateTo?: Date,
  ): Promise<number> {
    await this.gmailAuthHelper.validateGmailAuth(userId);

    const queryString = this.queryBuilder.buildQuery({
      dateFrom,
      dateTo,
    });

    try {
      const response = await this.gmailClient.listMessages(
        userId,
        queryString,
        1, // Only need count, not actual messages
      );

      return response.resultSizeEstimate || 0;
    } catch (error) {
      this.logger.error(
        `Failed to get email count for user ${userId}: ${error.message}`,
      );
      this.gmailAuthHelper.handleGmailApiError(error, userId);
    }
  }

  /**
   * Validate search parameters
   */
  private validateSearchParams(params: SearchEmailsDto): void {
    if (params.dateFrom && params.dateTo) {
      if (params.dateFrom > params.dateTo) {
        throw new BadRequestException(
          'dateFrom must be earlier than or equal to dateTo',
        );
      }

      // Check if date range is reasonable (not more than 5 years)
      const fiveYearsMs = 5 * 365 * 24 * 60 * 60 * 1000;
      if (params.dateTo.getTime() - params.dateFrom.getTime() > fiveYearsMs) {
        throw new BadRequestException(
          'Date range cannot exceed 5 years. Please narrow your search.',
        );
      }
    }

    if (params.maxResults && params.maxResults > this.MAX_RESULTS_LIMIT) {
      throw new BadRequestException(
        `maxResults cannot exceed ${this.MAX_RESULTS_LIMIT}`,
      );
    }

    if (params.maxResults && params.maxResults < 1) {
      throw new BadRequestException('maxResults must be at least 1');
    }
  }

  /**
   * Log search query for audit and analytics
   */
  private async logSearchQuery(
    userId: string,
    searchParams: SearchEmailsDto,
    resultsCount: number,
    durationMs: number,
  ): Promise<void> {
    try {
      await this.auditService.logAction({
        userId,
        action: 'EMAIL_SEARCH',
        details: {
          searchParams,
          resultsCount,
          durationMs,
        },
        ipAddress: null, // Will be set by controller
        userAgent: null, // Will be set by controller
      });
    } catch (error) {
      this.logger.error(
        `Failed to log search query for user ${userId}: ${error.message}`,
      );
      // Don't throw - audit logging failures shouldn't break the search
    }
  }
}
