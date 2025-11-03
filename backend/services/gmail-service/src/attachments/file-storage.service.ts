import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as fs from 'fs/promises';
import * as path from 'path';
import * as crypto from 'crypto';

/**
 * File Storage Service
 * Manages file storage with 24-hour retention (FR-010)
 * Implements secure file storage with user isolation
 */
@Injectable()
export class FileStorageService {
  private readonly logger = new Logger(FileStorageService.name);
  private readonly downloadDir: string;

  constructor(private readonly configService: ConfigService) {
    this.downloadDir =
      this.configService.get<string>('DOWNLOAD_DIR') || './downloads';
  }

  /**
   * Initialize storage directory
   * Called during module initialization
   */
  async initialize(): Promise<void> {
    try {
      await fs.mkdir(this.downloadDir, { recursive: true });
      this.logger.log(`Storage directory initialized: ${this.downloadDir}`);
    } catch (error) {
      this.logger.error(
        `Failed to initialize storage directory: ${error.message}`,
      );
      throw error;
    }
  }

  /**
   * Save file to storage
   * @param userId - User ID (for directory isolation)
   * @param filename - Original filename
   * @param buffer - File content
   * @param mimeType - MIME type
   * @returns Absolute path to saved file
   */
  async saveFile(
    userId: string,
    filename: string,
    buffer: Buffer,
    mimeType: string,
  ): Promise<string> {
    // Create user-specific directory
    const userDir = path.join(this.downloadDir, userId);
    await fs.mkdir(userDir, { recursive: true });

    // Generate unique filename to avoid collisions
    const uniqueFilename = this.generateUniqueFilename(filename);

    // Full path
    const filePath = path.join(userDir, uniqueFilename);

    try {
      // Write file to disk
      await fs.writeFile(filePath, buffer);

      this.logger.log(
        `Saved file: ${filePath} (${buffer.length} bytes, ${mimeType})`,
      );

      return filePath;
    } catch (error) {
      this.logger.error(`Failed to save file ${filePath}: ${error.message}`);
      throw error;
    }
  }

  /**
   * Delete file from storage
   * @param filePath - Absolute path to file
   */
  async deleteFile(filePath: string): Promise<void> {
    try {
      await fs.unlink(filePath);
      this.logger.log(`Deleted file: ${filePath}`);
    } catch (error) {
      if (error.code === 'ENOENT') {
        this.logger.warn(`File not found for deletion: ${filePath}`);
        return;
      }

      this.logger.error(`Failed to delete file ${filePath}: ${error.message}`);
      throw error;
    }
  }

  /**
   * Check if file exists
   * @param filePath - Absolute path to file
   * @returns True if file exists
   */
  async fileExists(filePath: string): Promise<boolean> {
    try {
      await fs.access(filePath);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Get file size
   * @param filePath - Absolute path to file
   * @returns File size in bytes
   */
  async getFileSize(filePath: string): Promise<number> {
    try {
      const stats = await fs.stat(filePath);
      return stats.size;
    } catch (error) {
      this.logger.error(
        `Failed to get file size for ${filePath}: ${error.message}`,
      );
      return 0;
    }
  }

  /**
   * Delete expired files for user
   * @param userId - User ID
   * @param expiryDate - Delete files older than this date
   * @returns Number of files deleted
   */
  async deleteExpiredFiles(userId: string, expiryDate: Date): Promise<number> {
    const userDir = path.join(this.downloadDir, userId);

    try {
      const files = await fs.readdir(userDir);
      let deletedCount = 0;

      for (const file of files) {
        const filePath = path.join(userDir, file);
        const stats = await fs.stat(filePath);

        if (stats.mtime < expiryDate) {
          await this.deleteFile(filePath);
          deletedCount++;
        }
      }

      this.logger.log(
        `Deleted ${deletedCount} expired files for user ${userId}`,
      );

      return deletedCount;
    } catch (error) {
      if (error.code === 'ENOENT') {
        // User directory doesn't exist yet
        return 0;
      }

      this.logger.error(
        `Failed to delete expired files for user ${userId}: ${error.message}`,
      );
      return 0;
    }
  }

  /**
   * Delete all files for user
   * @param userId - User ID
   * @returns Number of files deleted
   */
  async deleteUserFiles(userId: string): Promise<number> {
    const userDir = path.join(this.downloadDir, userId);

    try {
      const files = await fs.readdir(userDir);

      for (const file of files) {
        const filePath = path.join(userDir, file);
        await this.deleteFile(filePath);
      }

      // Remove user directory if empty
      await fs.rmdir(userDir);

      this.logger.log(`Deleted all files for user ${userId} (${files.length})`);

      return files.length;
    } catch (error) {
      if (error.code === 'ENOENT') {
        return 0;
      }

      this.logger.error(
        `Failed to delete user files for ${userId}: ${error.message}`,
      );
      return 0;
    }
  }

  /**
   * Get storage statistics for user
   * @param userId - User ID
   * @returns Storage statistics
   */
  async getUserStorageStats(userId: string): Promise<{
    fileCount: number;
    totalSize: number;
  }> {
    const userDir = path.join(this.downloadDir, userId);

    try {
      const files = await fs.readdir(userDir);
      let totalSize = 0;

      for (const file of files) {
        const filePath = path.join(userDir, file);
        const stats = await fs.stat(filePath);
        totalSize += stats.size;
      }

      return {
        fileCount: files.length,
        totalSize,
      };
    } catch (error) {
      if (error.code === 'ENOENT') {
        return { fileCount: 0, totalSize: 0 };
      }

      this.logger.error(
        `Failed to get storage stats for user ${userId}: ${error.message}`,
      );
      return { fileCount: 0, totalSize: 0 };
    }
  }

  /**
   * Get global storage statistics
   * @returns Global storage statistics
   */
  async getGlobalStorageStats(): Promise<{
    userCount: number;
    totalFiles: number;
    totalSize: number;
  }> {
    try {
      const users = await fs.readdir(this.downloadDir);
      let totalFiles = 0;
      let totalSize = 0;

      for (const userId of users) {
        const stats = await this.getUserStorageStats(userId);
        totalFiles += stats.fileCount;
        totalSize += stats.totalSize;
      }

      return {
        userCount: users.length,
        totalFiles,
        totalSize,
      };
    } catch (error) {
      this.logger.error(`Failed to get global storage stats: ${error.message}`);
      return { userCount: 0, totalFiles: 0, totalSize: 0 };
    }
  }

  /**
   * Generate unique filename to avoid collisions
   * Format: timestamp-hash-originalname.ext
   * @param originalFilename - Original filename
   * @returns Unique filename
   */
  private generateUniqueFilename(originalFilename: string): string {
    const timestamp = Date.now();
    const randomHash = crypto.randomBytes(8).toString('hex');
    const ext = path.extname(originalFilename);
    const nameWithoutExt = path.basename(originalFilename, ext);

    // Sanitize name (remove special characters)
    const sanitized = nameWithoutExt.replace(/[^a-zA-Z0-9_-]/g, '_');

    return `${timestamp}-${randomHash}-${sanitized}${ext}`;
  }

  /**
   * Clean up empty user directories
   * @returns Number of directories cleaned
   */
  async cleanupEmptyDirectories(): Promise<number> {
    try {
      const users = await fs.readdir(this.downloadDir);
      let cleanedCount = 0;

      for (const userId of users) {
        const userDir = path.join(this.downloadDir, userId);

        try {
          const files = await fs.readdir(userDir);

          if (files.length === 0) {
            await fs.rmdir(userDir);
            cleanedCount++;
            this.logger.log(`Cleaned up empty directory: ${userDir}`);
          }
        } catch (error) {
          // Skip if directory doesn't exist or can't be accessed
          continue;
        }
      }

      return cleanedCount;
    } catch (error) {
      this.logger.error(`Failed to cleanup empty directories: ${error.message}`);
      return 0;
    }
  }
}
