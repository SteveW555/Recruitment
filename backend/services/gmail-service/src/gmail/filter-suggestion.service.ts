import { Injectable, Logger } from '@nestjs/common';
import { PrismaClient } from '@prisma/client';
import { AdvancedFilterService, AdvancedSearchDto } from './advanced-filter.service';

export interface FilterSuggestion {
  type: 'domain' | 'keyword' | 'fileType' | 'dateRange' | 'preset';
  name: string;
  description: string;
  filters: Partial<AdvancedSearchDto>;
  frequency?: number; // How often this appears in user's searches
}

/**
 * Filter Suggestion Service
 * Provides intelligent filter suggestions based on search patterns
 * Implements US3: Advanced Filtering - Filter Suggestions
 */
@Injectable()
export class FilterSuggestionService {
  private readonly logger = new Logger(FilterSuggestionService.name);
  private readonly prisma: PrismaClient;

  constructor(private readonly advancedFilter: AdvancedFilterService) {
    this.prisma = new PrismaClient();
  }

  /**
   * Get filter suggestions for user
   * Based on search history and common patterns
   * @param userId - User ID
   * @returns Array of filter suggestions
   */
  async getSuggestionsForUser(userId: string): Promise<FilterSuggestion[]> {
    const suggestions: FilterSuggestion[] = [];

    // Get user's search history
    const recentSearches = await this.getRecentSearches(userId, 50);

    // Analyze patterns
    const domains = await this.extractCommonDomains(recentSearches);
    const keywords = await this.extractCommonKeywords(recentSearches);

    // Add domain suggestions
    for (const domain of domains.slice(0, 5)) {
      suggestions.push({
        type: 'domain',
        name: `Emails from ${domain.domain}`,
        description: `Filter emails from @${domain.domain} domain`,
        filters: {
          fromDomains: [domain.domain],
        },
        frequency: domain.count,
      });
    }

    // Add keyword suggestions
    for (const keyword of keywords.slice(0, 5)) {
      suggestions.push({
        type: 'keyword',
        name: `Contains "${keyword.word}"`,
        description: `Search for emails containing "${keyword.word}"`,
        filters: {
          bodyKeywords: [keyword.word],
        },
        frequency: keyword.count,
      });
    }

    // Add preset suggestions
    suggestions.push(...this.getPresetSuggestions());

    return suggestions;
  }

  /**
   * Get preset filter suggestions
   * Common patterns for recruitment
   */
  private getPresetSuggestions(): FilterSuggestion[] {
    return [
      {
        type: 'preset',
        name: 'CV/Resume Emails',
        description: 'Emails with CV or resume attachments',
        filters: {
          bodyKeywords: ['cv', 'resume', 'curriculum vitae'],
          matchAllKeywords: false,
          hasAttachment: true,
          fileTypes: ['pdf', 'doc', 'docx'],
        },
      },
      {
        type: 'preset',
        name: 'Job Applications',
        description: 'Emails about job applications',
        filters: {
          bodyKeywords: ['application', 'apply', 'position', 'role'],
          matchAllKeywords: false,
          hasAttachment: true,
        },
      },
      {
        type: 'preset',
        name: 'Recent Unread',
        description: 'Unread emails from the last 7 days',
        filters: {
          isRead: false,
          dateFrom: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
        },
      },
      {
        type: 'preset',
        name: 'With PDF Attachments',
        description: 'Emails with PDF attachments',
        filters: {
          hasAttachment: true,
          fileTypes: ['pdf'],
        },
      },
      {
        type: 'preset',
        name: 'This Month',
        description: 'Emails from this month',
        filters: {
          dateFrom: new Date(new Date().getFullYear(), new Date().getMonth(), 1),
        },
      },
      {
        type: 'preset',
        name: 'Last Week',
        description: 'Emails from the last 7 days',
        filters: {
          dateFrom: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
        },
      },
      {
        type: 'preset',
        name: 'Candidate References',
        description: 'Emails about references or recommendations',
        filters: {
          bodyKeywords: ['reference', 'recommendation', 'referee'],
          matchAllKeywords: false,
        },
      },
      {
        type: 'preset',
        name: 'Interview Requests',
        description: 'Emails about interview scheduling',
        filters: {
          bodyKeywords: ['interview', 'meeting', 'availability'],
          matchAllKeywords: false,
        },
      },
    ];
  }

  /**
   * Get domain suggestions based on email frequency
   * @param userId - User ID
   * @returns Top domains the user emails with
   */
  async getDomainSuggestions(userId: string): Promise<FilterSuggestion[]> {
    const recentSearches = await this.getRecentSearches(userId, 100);
    const domains = await this.extractCommonDomains(recentSearches);

    return domains.slice(0, 10).map((domain) => ({
      type: 'domain' as const,
      name: domain.domain,
      description: `${domain.count} emails from this domain`,
      filters: {
        fromDomains: [domain.domain],
      },
      frequency: domain.count,
    }));
  }

  /**
   * Get quick date range suggestions
   */
  getDateRangeSuggestions(): FilterSuggestion[] {
    const now = new Date();

    return [
      {
        type: 'dateRange',
        name: 'Today',
        description: 'Emails from today',
        filters: {
          dateFrom: new Date(now.getFullYear(), now.getMonth(), now.getDate()),
        },
      },
      {
        type: 'dateRange',
        name: 'Yesterday',
        description: 'Emails from yesterday',
        filters: {
          dateFrom: new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1),
          dateTo: new Date(now.getFullYear(), now.getMonth(), now.getDate()),
        },
      },
      {
        type: 'dateRange',
        name: 'Last 7 days',
        description: 'Emails from the past week',
        filters: {
          dateFrom: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
        },
      },
      {
        type: 'dateRange',
        name: 'Last 30 days',
        description: 'Emails from the past month',
        filters: {
          dateFrom: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
        },
      },
      {
        type: 'dateRange',
        name: 'This Month',
        description: 'Emails from current month',
        filters: {
          dateFrom: new Date(now.getFullYear(), now.getMonth(), 1),
        },
      },
      {
        type: 'dateRange',
        name: 'Last Month',
        description: 'Emails from previous month',
        filters: {
          dateFrom: new Date(now.getFullYear(), now.getMonth() - 1, 1),
          dateTo: new Date(now.getFullYear(), now.getMonth(), 1),
        },
      },
    ];
  }

  /**
   * Get file type suggestions
   */
  getFileTypeSuggestions(): FilterSuggestion[] {
    return [
      {
        type: 'fileType',
        name: 'PDF Documents',
        description: 'Emails with PDF attachments',
        filters: {
          hasAttachment: true,
          fileTypes: ['pdf'],
        },
      },
      {
        type: 'fileType',
        name: 'Word Documents',
        description: 'Emails with DOC/DOCX attachments',
        filters: {
          hasAttachment: true,
          fileTypes: ['doc', 'docx'],
        },
      },
      {
        type: 'fileType',
        name: 'Any Document',
        description: 'Emails with any document attachment',
        filters: {
          hasAttachment: true,
          fileTypes: ['pdf', 'doc', 'docx', 'rtf', 'txt'],
        },
      },
    ];
  }

  /**
   * Extract common domains from search history
   */
  private async extractCommonDomains(
    searches: any[],
  ): Promise<Array<{ domain: string; count: number }>> {
    const domainCounts = new Map<string, number>();

    for (const search of searches) {
      if (search.senderFilter) {
        const domain = this.advancedFilter.extractDomain(search.senderFilter);
        if (domain) {
          domainCounts.set(domain, (domainCounts.get(domain) || 0) + 1);
        }
      }
    }

    return Array.from(domainCounts.entries())
      .map(([domain, count]) => ({ domain, count }))
      .sort((a, b) => b.count - a.count);
  }

  /**
   * Extract common keywords from search history
   */
  private async extractCommonKeywords(
    searches: any[],
  ): Promise<Array<{ word: string; count: number }>> {
    const keywordCounts = new Map<string, number>();

    for (const search of searches) {
      // Extract from subject filter
      if (search.subjectFilter) {
        const words = this.extractWords(search.subjectFilter);
        words.forEach((word) => {
          keywordCounts.set(word, (keywordCounts.get(word) || 0) + 1);
        });
      }

      // Extract from body filter
      if (search.bodyFilter) {
        const words = this.extractWords(search.bodyFilter);
        words.forEach((word) => {
          keywordCounts.set(word, (keywordCounts.get(word) || 0) + 1);
        });
      }
    }

    return Array.from(keywordCounts.entries())
      .map(([word, count]) => ({ word, count }))
      .filter(({ word }) => word.length >= 3) // Filter short words
      .sort((a, b) => b.count - a.count);
  }

  /**
   * Extract meaningful words from text
   */
  private extractWords(text: string): string[] {
    const stopWords = new Set([
      'the',
      'is',
      'at',
      'which',
      'on',
      'and',
      'or',
      'for',
      'with',
      'from',
      'to',
      'of',
    ]);

    return text
      .toLowerCase()
      .split(/\W+/)
      .filter((word) => word.length >= 3 && !stopWords.has(word));
  }

  /**
   * Get recent search queries
   */
  private async getRecentSearches(userId: string, limit: number = 50) {
    try {
      return await this.prisma.searchQuery.findMany({
        where: { userId },
        orderBy: { createdAt: 'desc' },
        take: limit,
      });
    } catch (error) {
      this.logger.error(`Failed to get recent searches: ${error.message}`);
      return [];
    }
  }

  /**
   * Close Prisma connection
   */
  async onModuleDestroy() {
    await this.prisma.$disconnect();
  }
}
