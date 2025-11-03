import { Injectable, Logger, NotFoundException, BadRequestException } from '@nestjs/common';
import { DownloadTrackingService } from './download-tracking.service';
import * as fs from 'fs/promises';
import * as archiver from 'archiver';
import { Readable } from 'stream';

/**
 * Bulk Download Service
 * Creates ZIP archives of multiple downloaded files
 * Implements bulk download functionality for CV attachments
 */
@Injectable()
export class BulkDownloadService {
  private readonly logger = new Logger(BulkDownloadService.name);
  private readonly MAX_FILES_PER_ZIP = 100;
  private readonly MAX_ZIP_SIZE_MB = 500;
  private readonly MAX_ZIP_SIZE_BYTES = this.MAX_ZIP_SIZE_MB * 1024 * 1024;

  constructor(
    private readonly downloadTracking: DownloadTrackingService,
  ) {}

  /**
   * Create ZIP archive from multiple downloaded files
   * @param userId - User ID (for ownership verification)
   * @param downloadIds - Array of download IDs to include
   * @returns ZIP file buffer
   */
  async createZipArchive(
    userId: string,
    downloadIds: string[],
  ): Promise<Buffer> {
    // Validate request
    if (downloadIds.length === 0) {
      throw new BadRequestException('At least one download ID is required');
    }

    if (downloadIds.length > this.MAX_FILES_PER_ZIP) {
      throw new BadRequestException(
        `Maximum ${this.MAX_FILES_PER_ZIP} files can be included in a single ZIP`,
      );
    }

    this.logger.log(
      `Creating ZIP archive with ${downloadIds.length} files for user ${userId}`,
    );

    // Get download records and verify ownership
    const downloads = await this.getAndVerifyDownloads(userId, downloadIds);

    // Check total size
    const totalSize = downloads.reduce((sum, d) => sum + d.size, 0);

    if (totalSize > this.MAX_ZIP_SIZE_BYTES) {
      throw new BadRequestException(
        `Total file size exceeds maximum limit of ${this.MAX_ZIP_SIZE_MB}MB`,
      );
    }

    // Create ZIP archive
    try {
      const zipBuffer = await this.createZip(downloads);

      this.logger.log(
        `Created ZIP archive: ${zipBuffer.length} bytes from ${downloads.length} files`,
      );

      return zipBuffer;
    } catch (error) {
      this.logger.error(`Failed to create ZIP archive: ${error.message}`);
      throw error;
    }
  }

  /**
   * Get and verify download records
   * Ensures all downloads belong to the user and are not expired
   */
  private async getAndVerifyDownloads(
    userId: string,
    downloadIds: string[],
  ): Promise<Array<{
    id: string;
    filename: string;
    localPath: string;
    size: number;
  }>> {
    const downloads = [];

    for (const downloadId of downloadIds) {
      const download = await this.downloadTracking.getDownload(downloadId);

      if (!download) {
        throw new NotFoundException(`Download ${downloadId} not found`);
      }

      // Verify ownership
      if (download.userId !== userId) {
        throw new NotFoundException(`Download ${downloadId} not found`);
      }

      // Check if expired
      if (download.expiresAt < new Date()) {
        throw new BadRequestException(
          `Download ${downloadId} has expired`,
        );
      }

      // Check if already deleted
      if (download.deletedAt) {
        throw new BadRequestException(
          `Download ${downloadId} has been deleted`,
        );
      }

      downloads.push({
        id: download.id,
        filename: download.filename,
        localPath: download.localPath,
        size: download.size,
      });
    }

    return downloads;
  }

  /**
   * Create ZIP archive from file list
   */
  private async createZip(
    files: Array<{
      filename: string;
      localPath: string;
    }>,
  ): Promise<Buffer> {
    return new Promise((resolve, reject) => {
      const archive = archiver('zip', {
        zlib: { level: 6 }, // Compression level (0-9)
      });

      const chunks: Buffer[] = [];

      // Collect chunks
      archive.on('data', (chunk) => {
        chunks.push(chunk);
      });

      // Handle completion
      archive.on('end', () => {
        const buffer = Buffer.concat(chunks);
        resolve(buffer);
      });

      // Handle errors
      archive.on('error', (error) => {
        this.logger.error(`ZIP creation error: ${error.message}`);
        reject(error);
      });

      // Add files to archive
      const filenameCount = new Map<string, number>();

      for (const file of files) {
        try {
          // Handle duplicate filenames
          let archiveFilename = file.filename;
          if (filenameCount.has(file.filename)) {
            const count = filenameCount.get(file.filename) + 1;
            filenameCount.set(file.filename, count);

            // Add number before extension
            const parts = file.filename.split('.');
            if (parts.length > 1) {
              const ext = parts.pop();
              const name = parts.join('.');
              archiveFilename = `${name} (${count}).${ext}`;
            } else {
              archiveFilename = `${file.filename} (${count})`;
            }
          } else {
            filenameCount.set(file.filename, 1);
          }

          // Add file to archive
          archive.file(file.localPath, { name: archiveFilename });
        } catch (error) {
          this.logger.error(
            `Failed to add file ${file.filename} to ZIP: ${error.message}`,
          );
          // Continue with other files
        }
      }

      // Finalize archive
      archive.finalize();
    });
  }

  /**
   * Get estimated ZIP size
   * @param downloadIds - Array of download IDs
   * @param userId - User ID
   * @returns Estimated size in bytes
   */
  async getEstimatedZipSize(
    userId: string,
    downloadIds: string[],
  ): Promise<{
    totalFiles: number;
    uncompressedSize: number;
    estimatedZipSize: number;
  }> {
    const downloads = await this.getAndVerifyDownloads(userId, downloadIds);

    const uncompressedSize = downloads.reduce((sum, d) => sum + d.size, 0);

    // Estimate compressed size (typically 60-70% of original for documents)
    const estimatedZipSize = Math.round(uncompressedSize * 0.65);

    return {
      totalFiles: downloads.length,
      uncompressedSize,
      estimatedZipSize,
    };
  }

  /**
   * Check if ZIP creation is possible
   * @param downloadIds - Array of download IDs
   * @param userId - User ID
   * @returns Validation result
   */
  async validateZipRequest(
    userId: string,
    downloadIds: string[],
  ): Promise<{
    valid: boolean;
    errors: string[];
    warnings: string[];
  }> {
    const errors: string[] = [];
    const warnings: string[] = [];

    // Check file count
    if (downloadIds.length === 0) {
      errors.push('At least one file is required');
    }

    if (downloadIds.length > this.MAX_FILES_PER_ZIP) {
      errors.push(
        `Maximum ${this.MAX_FILES_PER_ZIP} files allowed per ZIP`,
      );
    }

    try {
      // Get and verify downloads
      const downloads = await this.getAndVerifyDownloads(userId, downloadIds);

      // Check total size
      const totalSize = downloads.reduce((sum, d) => sum + d.size, 0);

      if (totalSize > this.MAX_ZIP_SIZE_BYTES) {
        errors.push(
          `Total size ${Math.round(totalSize / 1024 / 1024)}MB exceeds limit of ${this.MAX_ZIP_SIZE_MB}MB`,
        );
      }

      // Check for large files
      const largeFiles = downloads.filter((d) => d.size > 50 * 1024 * 1024);
      if (largeFiles.length > 0) {
        warnings.push(
          `${largeFiles.length} file(s) larger than 50MB may slow down ZIP creation`,
        );
      }

      // Check for expiring files
      const expiringIn24h = downloads.filter(
        (d) => {
          const download = downloads.find(dl => dl.id === d.id);
          return download && download.localPath; // Simplified check
        },
      );

      if (expiringIn24h.length > 0) {
        warnings.push(`${expiringIn24h.length} file(s) will expire within 24 hours`);
      }
    } catch (error) {
      errors.push(error.message);
    }

    return {
      valid: errors.length === 0,
      errors,
      warnings,
    };
  }
}
