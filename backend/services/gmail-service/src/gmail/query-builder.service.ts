import { Injectable, Logger } from '@nestjs/common';
import { SearchEmailsDto } from './gmail.service';

/**
 * Gmail Query Builder Service
 * Constructs Gmail search query strings following Gmail search syntax
 * @see https://support.google.com/mail/answer/7190?hl=en
 */
@Injectable()
export class QueryBuilderService {
  private readonly logger = new Logger(QueryBuilderService.name);

  /**
   * Build Gmail search query from parameters
   * @param params - Search parameters
   * @returns Gmail query string
   */
  buildQuery(params: SearchEmailsDto): string {
    const queryParts: string[] = [];

    // Date range filters
    if (params.dateFrom) {
      const afterDate = this.formatDateForGmail(params.dateFrom);
      queryParts.push(`after:${afterDate}`);
    }

    if (params.dateTo) {
      const beforeDate = this.formatDateForGmail(params.dateTo);
      queryParts.push(`before:${beforeDate}`);
    }

    // Attachment filter
    if (params.hasAttachment !== undefined) {
      if (params.hasAttachment) {
        queryParts.push('has:attachment');
      } else {
        queryParts.push('-has:attachment');
      }
    }

    // From address filter
    if (params.fromAddress) {
      const sanitizedFrom = this.sanitizeEmailAddress(params.fromAddress);
      queryParts.push(`from:${sanitizedFrom}`);
    }

    // Subject filter
    if (params.subject) {
      const sanitizedSubject = this.sanitizeQueryTerm(params.subject);
      queryParts.push(`subject:"${sanitizedSubject}"`);
    }

    const query = queryParts.join(' ');

    this.logger.debug(`Built Gmail query: ${query}`);

    return query || ''; // Return empty string if no filters (searches all)
  }

  /**
   * Build query for emails with specific file type attachments
   * @param fileExtension - File extension (e.g., 'pdf', 'docx')
   * @param dateFrom - Optional start date
   * @param dateTo - Optional end date
   * @returns Gmail query string
   */
  buildAttachmentTypeQuery(
    fileExtension: string,
    dateFrom?: Date,
    dateTo?: Date,
  ): string {
    const params: SearchEmailsDto = {
      hasAttachment: true,
      dateFrom,
      dateTo,
    };

    const baseQuery = this.buildQuery(params);
    const sanitizedExtension = this.sanitizeQueryTerm(fileExtension);

    return baseQuery
      ? `${baseQuery} filename:${sanitizedExtension}`
      : `filename:${sanitizedExtension}`;
  }

  /**
   * Build query for emails from multiple senders
   * @param emailAddresses - Array of email addresses
   * @param dateFrom - Optional start date
   * @param dateTo - Optional end date
   * @returns Gmail query string
   */
  buildMultiSenderQuery(
    emailAddresses: string[],
    dateFrom?: Date,
    dateTo?: Date,
  ): string {
    const params: SearchEmailsDto = {
      dateFrom,
      dateTo,
    };

    const baseQuery = this.buildQuery(params);

    const senderParts = emailAddresses.map((email) => {
      const sanitized = this.sanitizeEmailAddress(email);
      return `from:${sanitized}`;
    });

    const sendersQuery = `(${senderParts.join(' OR ')})`;

    return baseQuery ? `${baseQuery} ${sendersQuery}` : sendersQuery;
  }

  /**
   * Build query for emails with specific keywords in body
   * @param keywords - Array of keywords to search for
   * @param matchAll - If true, all keywords must be present (AND), if false any keyword (OR)
   * @param dateFrom - Optional start date
   * @param dateTo - Optional end date
   * @returns Gmail query string
   */
  buildKeywordQuery(
    keywords: string[],
    matchAll: boolean = false,
    dateFrom?: Date,
    dateTo?: Date,
  ): string {
    const params: SearchEmailsDto = {
      dateFrom,
      dateTo,
    };

    const baseQuery = this.buildQuery(params);

    const sanitizedKeywords = keywords.map((kw) =>
      this.sanitizeQueryTerm(kw),
    );

    let keywordQuery: string;

    if (matchAll) {
      // All keywords must be present
      keywordQuery = sanitizedKeywords
        .map((kw) => `"${kw}"`)
        .join(' ');
    } else {
      // Any keyword can be present
      keywordQuery = `(${sanitizedKeywords.map((kw) => `"${kw}"`).join(' OR ')})`;
    }

    return baseQuery ? `${baseQuery} ${keywordQuery}` : keywordQuery;
  }

  /**
   * Build query for CV attachments (common CV file types)
   * @param dateFrom - Optional start date
   * @param dateTo - Optional end date
   * @returns Gmail query string
   */
  buildCVAttachmentQuery(dateFrom?: Date, dateTo?: Date): string {
    const params: SearchEmailsDto = {
      hasAttachment: true,
      dateFrom,
      dateTo,
    };

    const baseQuery = this.buildQuery(params);

    // Common CV file extensions
    const cvExtensions = ['pdf', 'doc', 'docx', 'rtf', 'txt'];
    const filenameParts = cvExtensions.map(
      (ext) => `filename:${ext}`,
    );

    const filenameQuery = `(${filenameParts.join(' OR ')})`;

    // Common CV keywords in subject or filename
    const cvKeywords = ['cv', 'resume', 'curriculum', 'vitae', 'application'];
    const keywordParts = cvKeywords.map(
      (kw) => `(subject:"${kw}" OR filename:"${kw}")`,
    );

    const keywordQuery = `(${keywordParts.join(' OR ')})`;

    const cvQuery = `${filenameQuery} ${keywordQuery}`;

    return baseQuery ? `${baseQuery} ${cvQuery}` : cvQuery;
  }

  /**
   * Format date for Gmail query (YYYY/MM/DD)
   * @param date - Date object
   * @returns Formatted date string
   */
  private formatDateForGmail(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');

    return `${year}/${month}/${day}`;
  }

  /**
   * Sanitize email address for query
   * Removes potentially dangerous characters
   * @param email - Email address
   * @returns Sanitized email
   */
  private sanitizeEmailAddress(email: string): string {
    // Remove whitespace and quotes
    let sanitized = email.trim().replace(/["']/g, '');

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(sanitized)) {
      this.logger.warn(`Invalid email format: ${email}`);
      // Return sanitized anyway, Gmail will handle invalid format
    }

    return sanitized;
  }

  /**
   * Sanitize query term for safe Gmail search
   * Escapes special characters
   * @param term - Search term
   * @returns Sanitized term
   */
  private sanitizeQueryTerm(term: string): string {
    // Remove or escape Gmail special characters
    // Gmail special chars: ( ) { } [ ] " \
    let sanitized = term.trim();

    // Escape backslashes first
    sanitized = sanitized.replace(/\\/g, '\\\\');

    // Escape quotes
    sanitized = sanitized.replace(/"/g, '\\"');

    // Remove other special characters that could break query
    sanitized = sanitized.replace(/[{}[\]]/g, '');

    return sanitized;
  }

  /**
   * Parse date string to Date object
   * Supports ISO 8601 and common formats
   * @param dateString - Date string
   * @returns Date object or null if invalid
   */
  parseDateString(dateString: string): Date | null {
    try {
      const date = new Date(dateString);

      if (isNaN(date.getTime())) {
        this.logger.warn(`Invalid date string: ${dateString}`);
        return null;
      }

      return date;
    } catch (error) {
      this.logger.error(`Failed to parse date: ${dateString}`);
      return null;
    }
  }

  /**
   * Validate date range
   * @param dateFrom - Start date
   * @param dateTo - End date
   * @returns True if valid, false otherwise
   */
  isValidDateRange(dateFrom: Date, dateTo: Date): boolean {
    if (!dateFrom || !dateTo) {
      return true; // If either is missing, no range to validate
    }

    return dateFrom <= dateTo;
  }
}
