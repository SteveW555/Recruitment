import { Injectable, Logger, NotFoundException, BadRequestException } from '@nestjs/common';
import { GmailClientService } from '../gmail/gmail-client.service';
import { GmailAuthHelper } from '../gmail/gmail-auth.helper';
import { FileStorageService } from './file-storage.service';
import { MimeValidationService } from './mime-validation.service';
import { DownloadTrackingService } from './download-tracking.service';
import * as path from 'path';
import * as fs from 'fs/promises';

export interface DownloadAttachmentDto {
  emailId: string;
  attachmentId: string;
  filename: string;
}

export interface DownloadedAttachment {
  downloadId: string;
  filename: string;
  mimeType: string;
  size: number;
  localPath: string;
  expiresAt: Date;
  downloadUrl: string;
}

/**
 * Attachment Service
 * Handles attachment downloads from Gmail with MIME validation and storage
 * Implements FR-007: Download CV attachments with 24-hour retention (FR-010)
 */
@Injectable()
export class AttachmentService {
  private readonly logger = new Logger(AttachmentService.name);
  private readonly MAX_FILE_SIZE_MB = 25;
  private readonly MAX_FILE_SIZE_BYTES = this.MAX_FILE_SIZE_MB * 1024 * 1024;

  constructor(
    private readonly gmailClient: GmailClientService,
    private readonly gmailAuthHelper: GmailAuthHelper,
    private readonly fileStorage: FileStorageService,
    private readonly mimeValidation: MimeValidationService,
    private readonly downloadTracking: DownloadTrackingService,
  ) {}

  /**
   * Download single attachment from Gmail
   * @param userId - User ID
   * @param emailId - Gmail message ID
   * @param attachmentId - Gmail attachment ID
   * @param filename - Original filename
   * @returns Download information
   */
  async downloadAttachment(
    userId: string,
    emailId: string,
    attachmentId: string,
    filename: string,
  ): Promise<DownloadedAttachment> {
    // Validate authentication
    await this.gmailAuthHelper.validateGmailAuth(userId);

    this.logger.log(
      `Downloading attachment ${attachmentId} from email ${emailId} for user ${userId}`,
    );

    try {
      // Fetch attachment from Gmail API
      const attachmentData = await this.gmailClient.getAttachment(
        userId,
        emailId,
        attachmentId,
      );

      if (!attachmentData.data) {
        throw new NotFoundException('Attachment data not found');
      }

      // Decode base64url data
      const fileBuffer = this.decodeBase64Url(attachmentData.data);

      // Validate file size
      if (fileBuffer.length > this.MAX_FILE_SIZE_BYTES) {
        throw new BadRequestException(
          `File size exceeds maximum limit of ${this.MAX_FILE_SIZE_MB}MB`,
        );
      }

      // Detect and validate MIME type
      const detectedMimeType = await this.mimeValidation.detectMimeType(
        fileBuffer,
        filename,
      );

      await this.mimeValidation.validateMimeType(detectedMimeType);

      // Save file to storage
      const storagePath = await this.fileStorage.saveFile(
        userId,
        filename,
        fileBuffer,
        detectedMimeType,
      );

      // Calculate expiry (24 hours from now)
      const expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000);

      // Track download in database
      const downloadRecord = await this.downloadTracking.trackDownload({
        userId,
        emailId,
        attachmentId,
        filename,
        mimeType: detectedMimeType,
        size: fileBuffer.length,
        localPath: storagePath,
        expiresAt,
      });

      this.logger.log(
        `Successfully downloaded attachment: ${filename} (${fileBuffer.length} bytes)`,
      );

      return {
        downloadId: downloadRecord.id,
        filename,
        mimeType: detectedMimeType,
        size: fileBuffer.length,
        localPath: storagePath,
        expiresAt,
        downloadUrl: `/api/v1/attachments/downloads/${downloadRecord.id}`,
      };
    } catch (error) {
      this.logger.error(
        `Failed to download attachment ${attachmentId}: ${error.message}`,
        error.stack,
      );

      if (error instanceof NotFoundException || error instanceof BadRequestException) {
        throw error;
      }

      this.gmailAuthHelper.handleGmailApiError(error, userId);
    }
  }

  /**
   * Download multiple attachments from an email
   * @param userId - User ID
   * @param emailId - Gmail message ID
   * @param attachments - Array of attachments to download
   * @returns Array of download information
   */
  async downloadEmailAttachments(
    userId: string,
    emailId: string,
    attachments: Array<{ attachmentId: string; filename: string }>,
  ): Promise<DownloadedAttachment[]> {
    await this.gmailAuthHelper.validateGmailAuth(userId);

    this.logger.log(
      `Downloading ${attachments.length} attachments from email ${emailId}`,
    );

    const downloads: DownloadedAttachment[] = [];

    for (const attachment of attachments) {
      try {
        const download = await this.downloadAttachment(
          userId,
          emailId,
          attachment.attachmentId,
          attachment.filename,
        );

        downloads.push(download);
      } catch (error) {
        this.logger.error(
          `Failed to download attachment ${attachment.filename}: ${error.message}`,
        );
        // Continue with other attachments even if one fails
      }
    }

    return downloads;
  }

  /**
   * Get downloaded file for serving
   * @param userId - User ID
   * @param downloadId - Download record ID
   * @returns File buffer and metadata
   */
  async getDownloadedFile(
    userId: string,
    downloadId: string,
  ): Promise<{
    buffer: Buffer;
    filename: string;
    mimeType: string;
  }> {
    // Get download record
    const download = await this.downloadTracking.getDownload(downloadId);

    if (!download) {
      throw new NotFoundException('Download not found');
    }

    // Verify ownership
    if (download.userId !== userId) {
      throw new NotFoundException('Download not found');
    }

    // Check if expired
    if (download.expiresAt < new Date()) {
      throw new NotFoundException('Download has expired');
    }

    // Read file from storage
    try {
      const buffer = await fs.readFile(download.localPath);

      return {
        buffer,
        filename: download.filename,
        mimeType: download.mimeType,
      };
    } catch (error) {
      this.logger.error(
        `Failed to read file ${download.localPath}: ${error.message}`,
      );
      throw new NotFoundException('File not found on disk');
    }
  }

  /**
   * List user's downloaded files
   * @param userId - User ID
   * @returns List of downloads
   */
  async listDownloads(userId: string): Promise<DownloadedAttachment[]> {
    const downloads = await this.downloadTracking.getUserDownloads(userId);

    return downloads.map((download) => ({
      downloadId: download.id,
      filename: download.filename,
      mimeType: download.mimeType,
      size: download.size,
      localPath: download.localPath,
      expiresAt: download.expiresAt,
      downloadUrl: `/api/v1/attachments/downloads/${download.id}`,
    }));
  }

  /**
   * Delete downloaded file
   * @param userId - User ID
   * @param downloadId - Download record ID
   */
  async deleteDownload(userId: string, downloadId: string): Promise<void> {
    const download = await this.downloadTracking.getDownload(downloadId);

    if (!download) {
      throw new NotFoundException('Download not found');
    }

    // Verify ownership
    if (download.userId !== userId) {
      throw new NotFoundException('Download not found');
    }

    // Delete file from storage
    await this.fileStorage.deleteFile(download.localPath);

    // Delete tracking record
    await this.downloadTracking.deleteDownload(downloadId);

    this.logger.log(`Deleted download ${downloadId} for user ${userId}`);
  }

  /**
   * Get download statistics for user
   * @param userId - User ID
   * @returns Download statistics
   */
  async getDownloadStats(userId: string): Promise<{
    totalDownloads: number;
    totalSize: number;
    activeDownloads: number;
    expiredDownloads: number;
  }> {
    return await this.downloadTracking.getUserStats(userId);
  }

  /**
   * Decode base64url encoded data
   * Gmail uses base64url (RFC 4648) encoding
   */
  private decodeBase64Url(data: string): Buffer {
    try {
      // Convert base64url to base64
      const base64 = data.replace(/-/g, '+').replace(/_/g, '/');

      // Decode from base64
      return Buffer.from(base64, 'base64');
    } catch (error) {
      this.logger.error(`Failed to decode base64url data: ${error.message}`);
      throw new BadRequestException('Invalid attachment data');
    }
  }

  /**
   * Check if file type is likely a CV
   * @param filename - File name
   * @param mimeType - MIME type
   * @returns True if likely a CV
   */
  isCVFile(filename: string, mimeType: string): boolean {
    const cvExtensions = ['.pdf', '.doc', '.docx', '.rtf', '.txt'];
    const ext = path.extname(filename).toLowerCase();

    if (!cvExtensions.includes(ext)) {
      return false;
    }

    const cvKeywords = ['cv', 'resume', 'curriculum', 'vitae'];
    const filenameLower = filename.toLowerCase();

    return cvKeywords.some((keyword) => filenameLower.includes(keyword));
  }
}
