import { Injectable, Logger, NotFoundException } from '@nestjs/common';
import { GmailClientService } from './gmail-client.service';
import { GmailAuthHelper } from './gmail-auth.helper';
import { gmail_v1 } from 'googleapis';

export interface EmailPreview {
  id: string;
  threadId: string;
  subject: string;
  from: {
    name?: string;
    email: string;
  };
  to: Array<{
    name?: string;
    email: string;
  }>;
  cc?: Array<{
    name?: string;
    email: string;
  }>;
  date: Date;
  snippet: string;
  body: {
    html?: string;
    text?: string;
  };
  attachments: Array<{
    attachmentId: string;
    filename: string;
    mimeType: string;
    size: number;
  }>;
  labels: string[];
  isRead: boolean;
  isStarred: boolean;
  hasAttachments: boolean;
}

/**
 * Email Preview Service
 * Fetches full email content for preview display
 * Implements FR-018: Email Preview
 */
@Injectable()
export class EmailPreviewService {
  private readonly logger = new Logger(EmailPreviewService.name);

  constructor(
    private readonly gmailClient: GmailClientService,
    private readonly gmailAuthHelper: GmailAuthHelper,
  ) {}

  /**
   * Get full email preview with body content
   * @param userId - User ID
   * @param emailId - Gmail message ID
   * @returns Complete email preview data
   */
  async getEmailPreview(userId: string, emailId: string): Promise<EmailPreview> {
    // Validate authentication
    await this.gmailAuthHelper.validateGmailAuth(userId);

    try {
      // Fetch full message with body
      const message = await this.gmailClient.getMessage(userId, emailId, 'full');

      if (!message) {
        throw new NotFoundException(`Email ${emailId} not found`);
      }

      return this.transformToPreview(message);
    } catch (error) {
      this.logger.error(
        `Failed to get email preview for ${emailId}: ${error.message}`,
      );
      throw error;
    }
  }

  /**
   * Transform Gmail message to preview format
   */
  private transformToPreview(message: gmail_v1.Schema$Message): EmailPreview {
    const headers = this.parseHeaders(message.payload?.headers || []);
    const body = this.extractBody(message.payload);
    const attachments = this.extractAttachments(message.payload);

    return {
      id: message.id!,
      threadId: message.threadId!,
      subject: headers.subject || '(No Subject)',
      from: this.parseAddress(headers.from),
      to: this.parseAddressList(headers.to),
      cc: headers.cc ? this.parseAddressList(headers.cc) : undefined,
      date: new Date(headers.date || message.internalDate || Date.now()),
      snippet: message.snippet || '',
      body,
      attachments,
      labels: message.labelIds || [],
      isRead: !message.labelIds?.includes('UNREAD'),
      isStarred: message.labelIds?.includes('STARRED') || false,
      hasAttachments: attachments.length > 0,
    };
  }

  /**
   * Parse email headers into key-value map
   */
  private parseHeaders(
    headers: gmail_v1.Schema$MessagePartHeader[],
  ): Record<string, string> {
    const headerMap: Record<string, string> = {};

    for (const header of headers) {
      if (header.name && header.value) {
        headerMap[header.name.toLowerCase()] = header.value;
      }
    }

    return headerMap;
  }

  /**
   * Extract email body (HTML and text)
   */
  private extractBody(
    payload?: gmail_v1.Schema$MessagePart,
  ): { html?: string; text?: string } {
    const body: { html?: string; text?: string } = {};

    if (!payload) {
      return body;
    }

    // Check for multipart message
    if (payload.mimeType?.startsWith('multipart/')) {
      return this.extractMultipartBody(payload.parts || []);
    }

    // Single part message
    const mimeType = payload.mimeType || '';
    const data = payload.body?.data;

    if (data) {
      const decodedContent = this.decodeBase64Url(data);

      if (mimeType === 'text/html') {
        body.html = decodedContent;
      } else if (mimeType === 'text/plain') {
        body.text = decodedContent;
      }
    }

    return body;
  }

  /**
   * Extract body from multipart message
   */
  private extractMultipartBody(
    parts: gmail_v1.Schema$MessagePart[],
  ): { html?: string; text?: string } {
    const body: { html?: string; text?: string } = {};

    for (const part of parts) {
      const mimeType = part.mimeType || '';

      // Handle nested multipart
      if (mimeType.startsWith('multipart/')) {
        const nestedBody = this.extractMultipartBody(part.parts || []);
        if (nestedBody.html) body.html = nestedBody.html;
        if (nestedBody.text) body.text = nestedBody.text;
        continue;
      }

      // Skip attachments
      if (part.filename && part.filename.length > 0) {
        continue;
      }

      // Extract text/html parts
      const data = part.body?.data;
      if (data) {
        const decodedContent = this.decodeBase64Url(data);

        if (mimeType === 'text/html' && !body.html) {
          body.html = decodedContent;
        } else if (mimeType === 'text/plain' && !body.text) {
          body.text = decodedContent;
        }
      }
    }

    return body;
  }

  /**
   * Extract attachment metadata
   */
  private extractAttachments(
    payload?: gmail_v1.Schema$MessagePart,
  ): Array<{
    attachmentId: string;
    filename: string;
    mimeType: string;
    size: number;
  }> {
    const attachments: Array<{
      attachmentId: string;
      filename: string;
      mimeType: string;
      size: number;
    }> = [];

    if (!payload) {
      return attachments;
    }

    // Check for multipart
    if (payload.parts) {
      for (const part of payload.parts) {
        attachments.push(...this.extractAttachments(part));
      }
    }

    // Check if this part is an attachment
    if (
      payload.filename &&
      payload.filename.length > 0 &&
      payload.body?.attachmentId
    ) {
      attachments.push({
        attachmentId: payload.body.attachmentId,
        filename: payload.filename,
        mimeType: payload.mimeType || 'application/octet-stream',
        size: payload.body.size || 0,
      });
    }

    return attachments;
  }

  /**
   * Parse single email address
   */
  private parseAddress(addressString?: string): {
    name?: string;
    email: string;
  } {
    if (!addressString) {
      return { email: '' };
    }

    // Format: "Name <email@example.com>" or "email@example.com"
    const match = addressString.match(/^(.+?)\s*<(.+?)>$/) ||
      addressString.match(/^(.+)$/);

    if (!match) {
      return { email: '' };
    }

    if (match.length === 3) {
      return {
        name: match[1].trim().replace(/^["']|["']$/g, ''),
        email: match[2].trim(),
      };
    }

    return { email: match[1].trim() };
  }

  /**
   * Parse comma-separated address list
   */
  private parseAddressList(
    addressString?: string,
  ): Array<{ name?: string; email: string }> {
    if (!addressString) {
      return [];
    }

    // Split by comma, but not commas inside quotes or angle brackets
    const addresses = addressString.split(/,(?=(?:[^"]*"[^"]*")*[^"]*$)/);

    return addresses.map((addr) => this.parseAddress(addr.trim()));
  }

  /**
   * Decode base64url-encoded string
   */
  private decodeBase64Url(data: string): string {
    try {
      // Convert base64url to base64
      const base64 = data.replace(/-/g, '+').replace(/_/g, '/');

      // Decode from base64
      const buffer = Buffer.from(base64, 'base64');

      return buffer.toString('utf-8');
    } catch (error) {
      this.logger.error(`Failed to decode base64url data: ${error.message}`);
      return '';
    }
  }

  /**
   * Get email thread preview
   * Returns all messages in a thread
   * @param userId - User ID
   * @param threadId - Gmail thread ID
   * @returns Array of email previews in thread
   */
  async getThreadPreview(
    userId: string,
    threadId: string,
  ): Promise<EmailPreview[]> {
    await this.gmailAuthHelper.validateGmailAuth(userId);

    try {
      const thread = await this.gmailClient.getThread(userId, threadId);

      if (!thread || !thread.messages) {
        throw new NotFoundException(`Thread ${threadId} not found`);
      }

      return thread.messages.map((message) => this.transformToPreview(message));
    } catch (error) {
      this.logger.error(
        `Failed to get thread preview for ${threadId}: ${error.message}`,
      );
      throw error;
    }
  }

  /**
   * Check if email has CV-related content
   * Useful for highlighting CV emails in preview
   */
  isCVEmail(preview: EmailPreview): boolean {
    const cvKeywords = [
      'cv',
      'resume',
      'curriculum vitae',
      'application',
      'apply',
    ];

    // Check subject
    const subjectLower = preview.subject.toLowerCase();
    if (cvKeywords.some((keyword) => subjectLower.includes(keyword))) {
      return true;
    }

    // Check attachments
    const hasCVAttachment = preview.attachments.some((attachment) => {
      const filenameLower = attachment.filename.toLowerCase();
      return cvKeywords.some((keyword) => filenameLower.includes(keyword));
    });

    return hasCVAttachment;
  }
}
