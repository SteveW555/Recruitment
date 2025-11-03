import { Injectable, Logger } from '@nestjs/common';
import { QueryBuilderService } from './query-builder.service';

export interface AdvancedSearchDto {
  // Date range
  dateFrom?: Date;
  dateTo?: Date;

  // Sender filters
  fromAddress?: string;
  fromDomains?: string[]; // e.g., ['example.com', 'test.org']
  excludeDomains?: string[]; // Exclude specific domains

  // Content filters
  subject?: string;
  bodyKeywords?: string[]; // Search in email body
  subjectKeywords?: string[]; // Search in subject line
  matchAllKeywords?: boolean; // AND vs OR logic

  // Attachment filters
  hasAttachment?: boolean;
  fileTypes?: string[]; // e.g., ['pdf', 'docx']
  minAttachments?: number; // Minimum number of attachments

  // Advanced filters
  labels?: string[]; // Gmail labels
  isRead?: boolean; // Read/unread status
  isStarred?: boolean; // Starred emails
  hasThread?: boolean; // Emails with replies

  // Size filters
  minSize?: number; // In bytes
  maxSize?: number; // In bytes

  // Exclusions
  excludeWords?: string[]; // Words to exclude
}

/**
 * Advanced Filter Service
 * Extends basic Gmail search with advanced filtering capabilities
 * Implements US3: Advanced Filtering
 */
@Injectable()
export class AdvancedFilterService {
  private readonly logger = new Logger(AdvancedFilterService.name);

  constructor(private readonly queryBuilder: QueryBuilderService) {}

  /**
   * Build advanced Gmail search query
   * @param filters - Advanced filter parameters
   * @returns Gmail query string
   */
  buildAdvancedQuery(filters: AdvancedSearchDto): string {
    const queryParts: string[] = [];

    // Date range
    if (filters.dateFrom) {
      const afterDate = this.formatDateForGmail(filters.dateFrom);
      queryParts.push(`after:${afterDate}`);
    }

    if (filters.dateTo) {
      const beforeDate = this.formatDateForGmail(filters.dateTo);
      queryParts.push(`before:${beforeDate}`);
    }

    // Sender domain filtering
    if (filters.fromDomains && filters.fromDomains.length > 0) {
      const domainQuery = this.buildDomainQuery(filters.fromDomains, false);
      queryParts.push(domainQuery);
    }

    // Exclude domains
    if (filters.excludeDomains && filters.excludeDomains.length > 0) {
      const excludeQuery = this.buildDomainQuery(filters.excludeDomains, true);
      queryParts.push(excludeQuery);
    }

    // Specific sender
    if (filters.fromAddress) {
      queryParts.push(`from:${this.sanitizeEmail(filters.fromAddress)}`);
    }

    // Subject keywords
    if (filters.subjectKeywords && filters.subjectKeywords.length > 0) {
      const subjectQuery = this.buildKeywordQuery(
        filters.subjectKeywords,
        'subject',
        filters.matchAllKeywords || false,
      );
      queryParts.push(subjectQuery);
    }

    // Subject text
    if (filters.subject) {
      queryParts.push(`subject:"${this.sanitizeText(filters.subject)}"`);
    }

    // Body keywords
    if (filters.bodyKeywords && filters.bodyKeywords.length > 0) {
      const bodyQuery = this.buildKeywordQuery(
        filters.bodyKeywords,
        'body',
        filters.matchAllKeywords || false,
      );
      queryParts.push(bodyQuery);
    }

    // Attachment filters
    if (filters.hasAttachment !== undefined) {
      queryParts.push(filters.hasAttachment ? 'has:attachment' : '-has:attachment');
    }

    // File types
    if (filters.fileTypes && filters.fileTypes.length > 0) {
      const fileTypeQuery = this.buildFileTypeQuery(filters.fileTypes);
      queryParts.push(fileTypeQuery);
    }

    // Gmail labels
    if (filters.labels && filters.labels.length > 0) {
      const labelQuery = filters.labels
        .map((label) => `label:${this.sanitizeText(label)}`)
        .join(' ');
      queryParts.push(labelQuery);
    }

    // Read/unread status
    if (filters.isRead !== undefined) {
      queryParts.push(filters.isRead ? 'is:read' : 'is:unread');
    }

    // Starred status
    if (filters.isStarred !== undefined) {
      queryParts.push(filters.isStarred ? 'is:starred' : '-is:starred');
    }

    // Size filters
    if (filters.minSize) {
      queryParts.push(`size:${filters.minSize}`);
    }

    if (filters.maxSize) {
      queryParts.push(`larger:${filters.minSize || 0} smaller:${filters.maxSize}`);
    }

    // Exclude words
    if (filters.excludeWords && filters.excludeWords.length > 0) {
      const excludeQuery = filters.excludeWords
        .map((word) => `-"${this.sanitizeText(word)}"`)
        .join(' ');
      queryParts.push(excludeQuery);
    }

    const query = queryParts.join(' ').trim();

    this.logger.debug(`Built advanced query: ${query}`);

    return query;
  }

  /**
   * Build sender domain query
   * @param domains - Array of domains
   * @param exclude - Whether to exclude these domains
   * @returns Gmail query string
   */
  private buildDomainQuery(domains: string[], exclude: boolean): string {
    const prefix = exclude ? '-' : '';
    const domainParts = domains.map((domain) => {
      const sanitized = this.sanitizeDomain(domain);
      return `${prefix}from:*@${sanitized}`;
    });

    if (domainParts.length === 1) {
      return domainParts[0];
    }

    // Multiple domains - use OR logic
    return `(${domainParts.join(' OR ')})`;
  }

  /**
   * Build keyword query for subject or body
   * @param keywords - Array of keywords
   * @param field - 'subject' or 'body'
   * @param matchAll - AND vs OR logic
   * @returns Gmail query string
   */
  private buildKeywordQuery(
    keywords: string[],
    field: 'subject' | 'body',
    matchAll: boolean,
  ): string {
    const sanitized = keywords.map((kw) => this.sanitizeText(kw));

    if (matchAll) {
      // AND logic - all keywords must be present
      return sanitized
        .map((kw) => `${field}:"${kw}"`)
        .join(' ');
    } else {
      // OR logic - any keyword can be present
      const keywordParts = sanitized.map((kw) => `${field}:"${kw}"`);
      return `(${keywordParts.join(' OR ')})`;
    }
  }

  /**
   * Build file type query
   * @param fileTypes - Array of file extensions
   * @returns Gmail query string
   */
  private buildFileTypeQuery(fileTypes: string[]): string {
    const sanitized = fileTypes.map((ext) => this.sanitizeText(ext));

    if (sanitized.length === 1) {
      return `filename:${sanitized[0]}`;
    }

    const fileTypeParts = sanitized.map((ext) => `filename:${ext}`);
    return `(${fileTypeParts.join(' OR ')})`;
  }

  /**
   * Search emails with sender domain filter
   * @param domain - Domain to search (e.g., 'example.com')
   * @param dateFrom - Optional start date
   * @param dateTo - Optional end date
   * @returns Gmail query string
   */
  buildDomainSearchQuery(
    domain: string,
    dateFrom?: Date,
    dateTo?: Date,
  ): string {
    return this.buildAdvancedQuery({
      fromDomains: [domain],
      dateFrom,
      dateTo,
    });
  }

  /**
   * Search emails with multiple keywords in body
   * @param keywords - Keywords to search
   * @param matchAll - Whether all keywords must be present
   * @param dateFrom - Optional start date
   * @param dateTo - Optional end date
   * @returns Gmail query string
   */
  buildKeywordSearchQuery(
    keywords: string[],
    matchAll: boolean = false,
    dateFrom?: Date,
    dateTo?: Date,
  ): string {
    return this.buildAdvancedQuery({
      bodyKeywords: keywords,
      matchAllKeywords: matchAll,
      dateFrom,
      dateTo,
    });
  }

  /**
   * Build query for recruitment-specific searches
   * Common patterns for CV/application emails
   */
  buildRecruitmentQuery(dateFrom?: Date, dateTo?: Date): string {
    const recruitmentKeywords = [
      'cv',
      'resume',
      'application',
      'apply',
      'position',
      'role',
      'candidate',
    ];

    return this.buildAdvancedQuery({
      bodyKeywords: recruitmentKeywords,
      matchAllKeywords: false, // Any keyword matches
      hasAttachment: true,
      fileTypes: ['pdf', 'doc', 'docx'],
      dateFrom,
      dateTo,
    });
  }

  /**
   * Sanitize email address
   */
  private sanitizeEmail(email: string): string {
    return email.trim().replace(/["']/g, '');
  }

  /**
   * Sanitize domain name
   */
  private sanitizeDomain(domain: string): string {
    // Remove protocol, www, and trailing slashes
    let sanitized = domain.toLowerCase().trim();
    sanitized = sanitized.replace(/^(https?:\/\/)?(www\.)?/, '');
    sanitized = sanitized.replace(/\/.*$/, '');
    return sanitized;
  }

  /**
   * Sanitize text for query
   */
  private sanitizeText(text: string): string {
    let sanitized = text.trim();
    // Escape backslashes and quotes
    sanitized = sanitized.replace(/\\/g, '\\\\');
    sanitized = sanitized.replace(/"/g, '\\"');
    // Remove special Gmail characters
    sanitized = sanitized.replace(/[{}[\]]/g, '');
    return sanitized;
  }

  /**
   * Format date for Gmail (YYYY/MM/DD)
   */
  private formatDateForGmail(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}/${month}/${day}`;
  }

  /**
   * Extract domain from email address
   */
  extractDomain(email: string): string | null {
    const match = email.match(/@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$/);
    return match ? match[1].toLowerCase() : null;
  }

  /**
   * Validate advanced filter parameters
   */
  validateFilters(filters: AdvancedSearchDto): {
    valid: boolean;
    errors: string[];
  } {
    const errors: string[] = [];

    // Validate date range
    if (filters.dateFrom && filters.dateTo) {
      if (filters.dateFrom > filters.dateTo) {
        errors.push('dateFrom must be earlier than dateTo');
      }
    }

    // Validate domains
    if (filters.fromDomains) {
      for (const domain of filters.fromDomains) {
        if (!this.isValidDomain(domain)) {
          errors.push(`Invalid domain: ${domain}`);
        }
      }
    }

    // Validate size filters
    if (filters.minSize && filters.maxSize) {
      if (filters.minSize > filters.maxSize) {
        errors.push('minSize must be less than maxSize');
      }
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }

  /**
   * Check if domain is valid
   */
  private isValidDomain(domain: string): boolean {
    const domainRegex = /^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?(\.[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?)*\.[a-zA-Z]{2,}$/;
    return domainRegex.test(domain);
  }
}
