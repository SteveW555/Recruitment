import {
  Controller,
  Get,
  Post,
  Put,
  Delete,
  Body,
  Param,
  Query,
  Req,
  UseGuards,
  BadRequestException,
} from '@nestjs/common';
import { Request } from 'express';
import { AuthGuard } from '../auth/auth.guard';
import { GmailService } from './gmail.service';
import { AdvancedFilterService, AdvancedSearchDto } from './advanced-filter.service';
import { SavedSearchService, CreateSavedSearchDto, UpdateSavedSearchDto } from './saved-search.service';
import { FilterSuggestionService } from './filter-suggestion.service';
import { QueryBuilderService } from './query-builder.service';

/**
 * Advanced Search Controller
 * Handles advanced filtering, saved searches, and filter suggestions
 * Implements US3: Advanced Filtering
 */
@Controller('gmail/advanced')
@UseGuards(AuthGuard)
export class AdvancedSearchController {
  constructor(
    private readonly gmailService: GmailService,
    private readonly advancedFilter: AdvancedFilterService,
    private readonly savedSearchService: SavedSearchService,
    private readonly filterSuggestions: FilterSuggestionService,
    private readonly queryBuilder: QueryBuilderService,
  ) {}

  /**
   * Advanced search with complex filters
   * POST /api/v1/gmail/advanced/search
   */
  @Post('search')
  async advancedSearch(
    @Req() req: Request,
    @Body() filters: AdvancedSearchDto,
    @Query('maxResults') maxResults?: string,
    @Query('pageToken') pageToken?: string,
  ) {
    const sessionData = req.session as any;
    const userId = sessionData.userId;

    // Validate filters
    const validation = this.advancedFilter.validateFilters(filters);
    if (!validation.valid) {
      throw new BadRequestException(validation.errors.join(', '));
    }

    // Build query
    const queryString = this.advancedFilter.buildAdvancedQuery(filters);

    // Execute search using basic search service
    const results = await this.gmailService.searchEmails(userId, {
      dateFrom: filters.dateFrom,
      dateTo: filters.dateTo,
      maxResults: maxResults ? parseInt(maxResults, 10) : undefined,
      pageToken,
    });

    return {
      success: true,
      data: results,
      query: {
        filters,
        gmailQuery: queryString,
      },
    };
  }

  /**
   * Search by sender domain
   * GET /api/v1/gmail/advanced/search/domain
   */
  @Get('search/domain')
  async searchByDomain(
    @Req() req: Request,
    @Query('domain') domain: string,
    @Query('dateFrom') dateFrom?: string,
    @Query('dateTo') dateTo?: string,
  ) {
    const sessionData = req.session as any;
    const userId = sessionData.userId;

    if (!domain) {
      throw new BadRequestException('domain parameter is required');
    }

    const queryString = this.advancedFilter.buildDomainSearchQuery(
      domain,
      dateFrom ? this.queryBuilder.parseDateString(dateFrom) : undefined,
      dateTo ? this.queryBuilder.parseDateString(dateTo) : undefined,
    );

    const results = await this.gmailService.searchEmails(userId, {
      dateFrom: dateFrom ? this.queryBuilder.parseDateString(dateFrom) : undefined,
      dateTo: dateTo ? this.queryBuilder.parseDateString(dateTo) : undefined,
    });

    return {
      success: true,
      data: results,
      query: {
        domain,
        gmailQuery: queryString,
      },
    };
  }

  /**
   * Search by keywords
   * POST /api/v1/gmail/advanced/search/keywords
   */
  @Post('search/keywords')
  async searchByKeywords(
    @Req() req: Request,
    @Body('keywords') keywords: string[],
    @Body('matchAll') matchAll?: boolean,
    @Body('dateFrom') dateFrom?: string,
    @Body('dateTo') dateTo?: string,
  ) {
    const sessionData = req.session as any;
    const userId = sessionData.userId;

    if (!keywords || keywords.length === 0) {
      throw new BadRequestException('keywords array is required');
    }

    const queryString = this.advancedFilter.buildKeywordSearchQuery(
      keywords,
      matchAll || false,
      dateFrom ? this.queryBuilder.parseDateString(dateFrom) : undefined,
      dateTo ? this.queryBuilder.parseDateString(dateTo) : undefined,
    );

    const results = await this.gmailService.searchEmails(userId, {
      dateFrom: dateFrom ? this.queryBuilder.parseDateString(dateFrom) : undefined,
      dateTo: dateTo ? this.queryBuilder.parseDateString(dateTo) : undefined,
    });

    return {
      success: true,
      data: results,
      query: {
        keywords,
        matchAll,
        gmailQuery: queryString,
      },
    };
  }

  /**
   * Search recruitment-related emails
   * GET /api/v1/gmail/advanced/search/recruitment
   */
  @Get('search/recruitment')
  async searchRecruitment(
    @Req() req: Request,
    @Query('dateFrom') dateFrom?: string,
    @Query('dateTo') dateTo?: string,
  ) {
    const sessionData = req.session as any;
    const userId = sessionData.userId;

    const queryString = this.advancedFilter.buildRecruitmentQuery(
      dateFrom ? this.queryBuilder.parseDateString(dateFrom) : undefined,
      dateTo ? this.queryBuilder.parseDateString(dateTo) : undefined,
    );

    const results = await this.gmailService.searchEmails(userId, {
      dateFrom: dateFrom ? this.queryBuilder.parseDateString(dateFrom) : undefined,
      dateTo: dateTo ? this.queryBuilder.parseDateString(dateTo) : undefined,
      hasAttachment: true,
    });

    return {
      success: true,
      data: results,
      query: {
        type: 'recruitment',
        gmailQuery: queryString,
      },
    };
  }

  // =============================================================================
  // Saved Searches
  // =============================================================================

  /**
   * Get all saved searches
   * GET /api/v1/gmail/advanced/saved
   */
  @Get('saved')
  async getSavedSearches(@Req() req: Request) {
    const sessionData = req.session as any;
    const userId = sessionData.userId;

    const searches = await this.savedSearchService.getUserSavedSearches(userId);

    return {
      success: true,
      data: {
        totalSaved: searches.length,
        searches,
      },
    };
  }

  /**
   * Create saved search
   * POST /api/v1/gmail/advanced/saved
   */
  @Post('saved')
  async createSavedSearch(
    @Req() req: Request,
    @Body() data: CreateSavedSearchDto,
  ) {
    const sessionData = req.session as any;
    const userId = sessionData.userId;

    const savedSearch = await this.savedSearchService.createSavedSearch(userId, data);

    return {
      success: true,
      data: savedSearch,
    };
  }

  /**
   * Get single saved search
   * GET /api/v1/gmail/advanced/saved/:id
   */
  @Get('saved/:id')
  async getSavedSearch(
    @Req() req: Request,
    @Param('id') searchId: string,
  ) {
    const sessionData = req.session as any;
    const userId = sessionData.userId;

    const savedSearch = await this.savedSearchService.getSavedSearch(userId, searchId);

    if (!savedSearch) {
      throw new BadRequestException('Saved search not found');
    }

    return {
      success: true,
      data: savedSearch,
    };
  }

  /**
   * Update saved search
   * PUT /api/v1/gmail/advanced/saved/:id
   */
  @Put('saved/:id')
  async updateSavedSearch(
    @Req() req: Request,
    @Param('id') searchId: string,
    @Body() data: UpdateSavedSearchDto,
  ) {
    const sessionData = req.session as any;
    const userId = sessionData.userId;

    const updated = await this.savedSearchService.updateSavedSearch(userId, searchId, data);

    return {
      success: true,
      data: updated,
    };
  }

  /**
   * Delete saved search
   * DELETE /api/v1/gmail/advanced/saved/:id
   */
  @Delete('saved/:id')
  async deleteSavedSearch(
    @Req() req: Request,
    @Param('id') searchId: string,
  ) {
    const sessionData = req.session as any;
    const userId = sessionData.userId;

    await this.savedSearchService.deleteSavedSearch(userId, searchId);

    return {
      success: true,
      message: 'Saved search deleted successfully',
    };
  }

  /**
   * Execute saved search
   * GET /api/v1/gmail/advanced/saved/:id/execute
   */
  @Get('saved/:id/execute')
  async executeSavedSearch(
    @Req() req: Request,
    @Param('id') searchId: string,
    @Query('maxResults') maxResults?: string,
    @Query('pageToken') pageToken?: string,
  ) {
    const sessionData = req.session as any;
    const userId = sessionData.userId;

    const savedSearch = await this.savedSearchService.getSavedSearch(userId, searchId);

    if (!savedSearch) {
      throw new BadRequestException('Saved search not found');
    }

    // Record usage
    await this.savedSearchService.recordUsage(userId, searchId);

    // Execute search
    const filters = savedSearch.filters as AdvancedSearchDto;
    const queryString = this.advancedFilter.buildAdvancedQuery(filters);

    const results = await this.gmailService.searchEmails(userId, {
      dateFrom: filters.dateFrom,
      dateTo: filters.dateTo,
      maxResults: maxResults ? parseInt(maxResults, 10) : undefined,
      pageToken,
    });

    return {
      success: true,
      data: results,
      savedSearch: {
        id: savedSearch.id,
        name: savedSearch.name,
        description: savedSearch.description,
      },
      query: {
        filters,
        gmailQuery: queryString,
      },
    };
  }

  /**
   * Get saved search statistics
   * GET /api/v1/gmail/advanced/saved/stats
   */
  @Get('saved-stats')
  async getSavedSearchStats(@Req() req: Request) {
    const sessionData = req.session as any;
    const userId = sessionData.userId;

    const stats = await this.savedSearchService.getStats(userId);

    return {
      success: true,
      data: stats,
    };
  }

  // =============================================================================
  // Filter Suggestions
  // =============================================================================

  /**
   * Get filter suggestions
   * GET /api/v1/gmail/advanced/suggestions
   */
  @Get('suggestions')
  async getFilterSuggestions(@Req() req: Request) {
    const sessionData = req.session as any;
    const userId = sessionData.userId;

    const suggestions = await this.filterSuggestions.getSuggestionsForUser(userId);

    return {
      success: true,
      data: {
        total: suggestions.length,
        suggestions,
      },
    };
  }

  /**
   * Get domain suggestions
   * GET /api/v1/gmail/advanced/suggestions/domains
   */
  @Get('suggestions/domains')
  async getDomainSuggestions(@Req() req: Request) {
    const sessionData = req.session as any;
    const userId = sessionData.userId;

    const suggestions = await this.filterSuggestions.getDomainSuggestions(userId);

    return {
      success: true,
      data: {
        total: suggestions.length,
        suggestions,
      },
    };
  }

  /**
   * Get date range suggestions
   * GET /api/v1/gmail/advanced/suggestions/date-ranges
   */
  @Get('suggestions/date-ranges')
  async getDateRangeSuggestions() {
    const suggestions = this.filterSuggestions.getDateRangeSuggestions();

    return {
      success: true,
      data: {
        total: suggestions.length,
        suggestions,
      },
    };
  }

  /**
   * Get file type suggestions
   * GET /api/v1/gmail/advanced/suggestions/file-types
   */
  @Get('suggestions/file-types')
  async getFileTypeSuggestions() {
    const suggestions = this.filterSuggestions.getFileTypeSuggestions();

    return {
      success: true,
      data: {
        total: suggestions.length,
        suggestions,
      },
    };
  }

  /**
   * Health check
   * GET /api/v1/gmail/advanced/health
   */
  @Get('health')
  async healthCheck() {
    return {
      success: true,
      service: 'advanced-search',
      timestamp: new Date().toISOString(),
      status: 'healthy',
    };
  }
}
