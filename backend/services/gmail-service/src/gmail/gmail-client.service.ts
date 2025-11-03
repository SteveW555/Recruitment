import { Injectable, Logger } from '@nestjs/common';
import { google, gmail_v1 } from 'googleapis';
import { TokenRefreshService } from '../auth/token-refresh.service';

/**
 * Gmail API Client Wrapper
 * Handles low-level Gmail API interactions with automatic token management
 */
@Injectable()
export class GmailClientService {
  private readonly logger = new Logger(GmailClientService.name);

  constructor(private readonly tokenRefreshService: TokenRefreshService) {}

  /**
   * Get authenticated Gmail API client for a user
   * @param userId - User ID
   * @returns Authenticated Gmail API instance
   */
  async getGmailClient(userId: string): Promise<gmail_v1.Gmail> {
    const accessToken = await this.tokenRefreshService.getCachedToken(userId);

    const oauth2Client = new google.auth.OAuth2();
    oauth2Client.setCredentials({
      access_token: accessToken,
    });

    return google.gmail({ version: 'v1', auth: oauth2Client });
  }

  /**
   * List messages with query
   * @param userId - User ID
   * @param query - Gmail search query
   * @param maxResults - Maximum number of results (default 50, max 500)
   * @param pageToken - Page token for pagination
   * @returns List of message IDs and next page token
   */
  async listMessages(
    userId: string,
    query: string,
    maxResults: number = 50,
    pageToken?: string,
  ): Promise<{
    messages: gmail_v1.Schema$Message[];
    nextPageToken?: string;
    resultSizeEstimate?: number;
  }> {
    const gmail = await this.getGmailClient(userId);

    try {
      this.logger.log(`Listing messages for user ${userId} with query: ${query}`);

      const response = await gmail.users.messages.list({
        userId: 'me',
        q: query,
        maxResults,
        pageToken,
      });

      return {
        messages: response.data.messages || [],
        nextPageToken: response.data.nextPageToken,
        resultSizeEstimate: response.data.resultSizeEstimate,
      };
    } catch (error) {
      this.logger.error(
        `Failed to list messages for user ${userId}: ${error.message}`,
        error.stack,
      );
      throw error;
    }
  }

  /**
   * Get full message details
   * @param userId - User ID
   * @param messageId - Gmail message ID
   * @param format - Response format (full, metadata, minimal, raw)
   * @returns Full message data
   */
  async getMessage(
    userId: string,
    messageId: string,
    format: 'full' | 'metadata' | 'minimal' | 'raw' = 'full',
  ): Promise<gmail_v1.Schema$Message> {
    const gmail = await this.getGmailClient(userId);

    try {
      this.logger.log(`Getting message ${messageId} for user ${userId}`);

      const response = await gmail.users.messages.get({
        userId: 'me',
        id: messageId,
        format,
      });

      return response.data;
    } catch (error) {
      this.logger.error(
        `Failed to get message ${messageId} for user ${userId}: ${error.message}`,
        error.stack,
      );
      throw error;
    }
  }

  /**
   * Get multiple messages in batch
   * @param userId - User ID
   * @param messageIds - Array of Gmail message IDs
   * @param format - Response format
   * @returns Array of full message data
   */
  async getMessagesBatch(
    userId: string,
    messageIds: string[],
    format: 'full' | 'metadata' | 'minimal' = 'full',
  ): Promise<gmail_v1.Schema$Message[]> {
    const gmail = await this.getGmailClient(userId);

    try {
      this.logger.log(
        `Getting ${messageIds.length} messages in batch for user ${userId}`,
      );

      const messages = await Promise.all(
        messageIds.map((id) =>
          gmail.users.messages.get({
            userId: 'me',
            id,
            format,
          }),
        ),
      );

      return messages.map((response) => response.data);
    } catch (error) {
      this.logger.error(
        `Failed to get messages batch for user ${userId}: ${error.message}`,
        error.stack,
      );
      throw error;
    }
  }

  /**
   * Get attachment data
   * @param userId - User ID
   * @param messageId - Gmail message ID
   * @param attachmentId - Attachment ID
   * @returns Attachment data (base64 encoded)
   */
  async getAttachment(
    userId: string,
    messageId: string,
    attachmentId: string,
  ): Promise<gmail_v1.Schema$MessagePartBody> {
    const gmail = await this.getGmailClient(userId);

    try {
      this.logger.log(
        `Getting attachment ${attachmentId} from message ${messageId} for user ${userId}`,
      );

      const response = await gmail.users.messages.attachments.get({
        userId: 'me',
        messageId,
        id: attachmentId,
      });

      return response.data;
    } catch (error) {
      this.logger.error(
        `Failed to get attachment ${attachmentId} for user ${userId}: ${error.message}`,
        error.stack,
      );
      throw error;
    }
  }

  /**
   * Get user profile information
   * @param userId - User ID
   * @returns Gmail profile data
   */
  async getUserProfile(userId: string): Promise<gmail_v1.Schema$Profile> {
    const gmail = await this.getGmailClient(userId);

    try {
      this.logger.log(`Getting profile for user ${userId}`);

      const response = await gmail.users.getProfile({
        userId: 'me',
      });

      return response.data;
    } catch (error) {
      this.logger.error(
        `Failed to get profile for user ${userId}: ${error.message}`,
        error.stack,
      );
      throw error;
    }
  }
}
