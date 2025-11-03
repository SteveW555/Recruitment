import { Injectable, Logger } from '@nestjs/common';
import { gmail_v1 } from 'googleapis';

export interface TransformedEmail {
  id: string;
  threadId: string;
  from: string;
  to: string[];
  cc?: string[];
  bcc?: string[];
  subject: string;
  date: Date;
  snippet: string;
  body: {
    plain?: string;
    html?: string;
  };
  attachments: TransformedAttachment[];
  labels: string[];
  hasAttachments: boolean;
  sizeEstimate: number;
  internalDate: Date;
  headers: Record<string, string>;
}

export interface TransformedAttachment {
  attachmentId: string;
  filename: string;
  mimeType: string;
  size: number;
  isInline: boolean;
}

/**
 * Email Transformer Service
 * Transforms Gmail API messages to internal model
 */
@Injectable()
export class EmailTransformer {
  private readonly logger = new Logger(EmailTransformer.name);

  /**
   * Transform Gmail API message to internal model
   * @param message - Gmail API message
   * @returns Transformed email object
   */
  transformEmail(message: gmail_v1.Schema$Message): TransformedEmail {
    const headers = this.extractHeaders(message);
    const attachments = this.extractAttachments(message);
    const body = this.extractBody(message);

    return {
      id: message.id,
      threadId: message.threadId,
      from: headers.from || '',
      to: this.parseAddressList(headers.to),
      cc: this.parseAddressList(headers.cc),
      bcc: this.parseAddressList(headers.bcc),
      subject: headers.subject || '(No Subject)',
      date: this.parseDate(headers.date || message.internalDate),
      snippet: message.snippet || '',
      body,
      attachments,
      labels: message.labelIds || [],
      hasAttachments: attachments.length > 0,
      sizeEstimate: message.sizeEstimate || 0,
      internalDate: new Date(parseInt(message.internalDate, 10)),
      headers: headers,
    };
  }

  /**
   * Extract headers from Gmail message
   */
  private extractHeaders(
    message: gmail_v1.Schema$Message,
  ): Record<string, string> {
    const headers: Record<string, string> = {};

    if (!message.payload?.headers) {
      return headers;
    }

    message.payload.headers.forEach((header) => {
      const name = header.name.toLowerCase();
      const value = header.value;

      // Store commonly used headers
      if (
        [
          'from',
          'to',
          'cc',
          'bcc',
          'subject',
          'date',
          'message-id',
          'in-reply-to',
          'references',
          'content-type',
        ].includes(name)
      ) {
        headers[name] = value;
      }
    });

    return headers;
  }

  /**
   * Extract attachments from Gmail message
   */
  private extractAttachments(
    message: gmail_v1.Schema$Message,
  ): TransformedAttachment[] {
    const attachments: TransformedAttachment[] = [];

    if (!message.payload) {
      return attachments;
    }

    const processPart = (part: gmail_v1.Schema$MessagePart) => {
      if (part.filename && part.body?.attachmentId) {
        attachments.push({
          attachmentId: part.body.attachmentId,
          filename: part.filename,
          mimeType: part.mimeType || 'application/octet-stream',
          size: part.body.size || 0,
          isInline: this.isInlineAttachment(part),
        });
      }

      // Recursively process nested parts
      if (part.parts) {
        part.parts.forEach(processPart);
      }
    };

    // Process message payload
    if (message.payload.parts) {
      message.payload.parts.forEach(processPart);
    } else {
      // Single part message
      processPart(message.payload);
    }

    return attachments;
  }

  /**
   * Check if attachment is inline (embedded image)
   */
  private isInlineAttachment(part: gmail_v1.Schema$MessagePart): boolean {
    if (!part.headers) {
      return false;
    }

    const contentDisposition = part.headers.find(
      (h) => h.name.toLowerCase() === 'content-disposition',
    );

    return contentDisposition?.value?.toLowerCase().includes('inline') || false;
  }

  /**
   * Extract body from Gmail message
   */
  private extractBody(message: gmail_v1.Schema$Message): {
    plain?: string;
    html?: string;
  } {
    const body: { plain?: string; html?: string } = {};

    if (!message.payload) {
      return body;
    }

    const processPart = (part: gmail_v1.Schema$MessagePart) => {
      const mimeType = part.mimeType?.toLowerCase();

      // Extract text/plain
      if (mimeType === 'text/plain' && part.body?.data) {
        if (!body.plain) {
          // Only take first text/plain part
          body.plain = this.decodeBase64(part.body.data);
        }
      }

      // Extract text/html
      if (mimeType === 'text/html' && part.body?.data) {
        if (!body.html) {
          // Only take first text/html part
          body.html = this.decodeBase64(part.body.data);
        }
      }

      // Recursively process nested parts
      if (part.parts) {
        part.parts.forEach(processPart);
      }
    };

    // Process message payload
    if (message.payload.parts) {
      message.payload.parts.forEach(processPart);
    } else {
      // Single part message
      processPart(message.payload);
    }

    return body;
  }

  /**
   * Decode base64url encoded string
   * Gmail uses base64url (RFC 4648) encoding
   */
  private decodeBase64(data: string): string {
    try {
      // Convert base64url to base64
      const base64 = data.replace(/-/g, '+').replace(/_/g, '/');

      // Decode from base64
      return Buffer.from(base64, 'base64').toString('utf-8');
    } catch (error) {
      this.logger.error(`Failed to decode base64 data: ${error.message}`);
      return '';
    }
  }

  /**
   * Parse comma-separated email address list
   */
  private parseAddressList(addressString?: string): string[] {
    if (!addressString) {
      return [];
    }

    // Split by comma and clean up
    return addressString
      .split(',')
      .map((addr) => addr.trim())
      .filter((addr) => addr.length > 0);
  }

  /**
   * Parse date string to Date object
   */
  private parseDate(dateString?: string): Date {
    if (!dateString) {
      return new Date();
    }

    try {
      // If it's a timestamp (all digits), parse as integer
      if (/^\d+$/.test(dateString)) {
        return new Date(parseInt(dateString, 10));
      }

      // Otherwise parse as date string
      const date = new Date(dateString);

      if (isNaN(date.getTime())) {
        this.logger.warn(`Invalid date string: ${dateString}`);
        return new Date();
      }

      return date;
    } catch (error) {
      this.logger.error(`Failed to parse date: ${dateString}`);
      return new Date();
    }
  }

  /**
   * Get plain text preview (first 200 characters)
   * For FR-018: Email preview requirement
   */
  getEmailPreview(email: TransformedEmail): string {
    let text = email.body.plain || '';

    // If no plain text, strip HTML tags from HTML body
    if (!text && email.body.html) {
      text = this.stripHtmlTags(email.body.html);
    }

    // If still no text, use snippet
    if (!text) {
      text = email.snippet;
    }

    // Take first 200 characters
    const preview = text.slice(0, 200).trim();

    // Add truncation indicator if text is longer
    if (text.length > 200) {
      return preview + ' [...]';
    }

    return preview;
  }

  /**
   * Strip HTML tags from text
   */
  private stripHtmlTags(html: string): string {
    // Remove script and style tags with their content
    let text = html.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
    text = text.replace(/<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>/gi, '');

    // Remove all HTML tags
    text = text.replace(/<[^>]+>/g, '');

    // Decode HTML entities
    text = this.decodeHtmlEntities(text);

    // Normalize whitespace
    text = text.replace(/\s+/g, ' ').trim();

    return text;
  }

  /**
   * Decode common HTML entities
   */
  private decodeHtmlEntities(text: string): string {
    const entities: Record<string, string> = {
      '&nbsp;': ' ',
      '&amp;': '&',
      '&lt;': '<',
      '&gt;': '>',
      '&quot;': '"',
      '&#39;': "'",
      '&apos;': "'",
    };

    return text.replace(/&[#\w]+;/g, (entity) => {
      return entities[entity] || entity;
    });
  }

  /**
   * Check if email is likely a CV/resume
   * Based on attachments and keywords
   */
  isCVEmail(email: TransformedEmail): boolean {
    const cvKeywords = ['cv', 'resume', 'curriculum', 'vitae', 'application'];

    // Check subject
    const subjectLower = email.subject.toLowerCase();
    const hasKeywordInSubject = cvKeywords.some((kw) =>
      subjectLower.includes(kw),
    );

    if (hasKeywordInSubject) {
      return true;
    }

    // Check attachments
    const cvFileTypes = ['.pdf', '.doc', '.docx', '.rtf', '.txt'];
    const hasCVAttachment = email.attachments.some((att) => {
      const filenameLower = att.filename.toLowerCase();
      const hasCVExtension = cvFileTypes.some((ext) =>
        filenameLower.endsWith(ext),
      );
      const hasKeywordInFilename = cvKeywords.some((kw) =>
        filenameLower.includes(kw),
      );

      return hasCVExtension && hasKeywordInFilename;
    });

    return hasCVAttachment;
  }
}
