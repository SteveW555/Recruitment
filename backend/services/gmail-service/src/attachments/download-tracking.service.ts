import { Injectable, Logger } from '@nestjs/common';
import { PrismaClient } from '@prisma/client';

export interface TrackDownloadDto {
  userId: string;
  emailId: string;
  attachmentId: string;
  filename: string;
  mimeType: string;
  size: number;
  localPath: string;
  expiresAt: Date;
}

/**
 * Download Tracking Service
 * Manages database records for downloaded files
 * Tracks downloads for 24-hour retention period (FR-010)
 */
@Injectable()
export class DownloadTrackingService {
  private readonly logger = new Logger(DownloadTrackingService.name);
  private readonly prisma: PrismaClient;

  constructor() {
    this.prisma = new PrismaClient();
  }

  /**
   * Track a new download in the database
   * @param data - Download information
   * @returns Created download record
   */
  async trackDownload(data: TrackDownloadDto) {
    try {
      const download = await this.prisma.downloadedFile.create({
        data: {
          userId: data.userId,
          emailId: data.emailId,
          attachmentId: data.attachmentId,
          filename: data.filename,
          mimeType: data.mimeType,
          size: data.size,
          localPath: data.localPath,
          expiresAt: data.expiresAt,
        },
      });

      this.logger.log(
        `Tracked download: ${download.id} for user ${data.userId}`,
      );

      return {
        ...download,
        size: Number(download.size), // Convert BigInt to number for serialization
      };
    } catch (error) {
      this.logger.error(`Failed to track download: ${error.message}`);
      throw error;
    }
  }

  /**
   * Get download record by ID
   * @param downloadId - Download record ID
   * @returns Download record or null
   */
  async getDownload(downloadId: string) {
    try {
      const download = await this.prisma.downloadedFile.findUnique({
        where: { id: downloadId },
      });

      if (!download) {
        return null;
      }

      return {
        ...download,
        size: Number(download.size),
      };
    } catch (error) {
      this.logger.error(
        `Failed to get download ${downloadId}: ${error.message}`,
      );
      return null;
    }
  }

  /**
   * Get all downloads for user
   * @param userId - User ID
   * @returns List of downloads
   */
  async getUserDownloads(userId: string) {
    try {
      const downloads = await this.prisma.downloadedFile.findMany({
        where: {
          userId,
          deletedAt: null,
        },
        orderBy: {
          downloadedAt: 'desc',
        },
      });

      return downloads.map((download) => ({
        ...download,
        size: Number(download.size),
      }));
    } catch (error) {
      this.logger.error(
        `Failed to get downloads for user ${userId}: ${error.message}`,
      );
      return [];
    }
  }

  /**
   * Get expired downloads
   * @returns List of expired download records
   */
  async getExpiredDownloads() {
    try {
      const now = new Date();

      const downloads = await this.prisma.downloadedFile.findMany({
        where: {
          expiresAt: {
            lt: now,
          },
          deletedAt: null,
        },
      });

      return downloads.map((download) => ({
        ...download,
        size: Number(download.size),
      }));
    } catch (error) {
      this.logger.error(`Failed to get expired downloads: ${error.message}`);
      return [];
    }
  }

  /**
   * Mark download as deleted
   * @param downloadId - Download record ID
   */
  async deleteDownload(downloadId: string): Promise<void> {
    try {
      await this.prisma.downloadedFile.update({
        where: { id: downloadId },
        data: {
          deletedAt: new Date(),
        },
      });

      this.logger.log(`Marked download ${downloadId} as deleted`);
    } catch (error) {
      this.logger.error(
        `Failed to delete download ${downloadId}: ${error.message}`,
      );
      throw error;
    }
  }

  /**
   * Permanently delete download record
   * @param downloadId - Download record ID
   */
  async permanentlyDeleteDownload(downloadId: string): Promise<void> {
    try {
      await this.prisma.downloadedFile.delete({
        where: { id: downloadId },
      });

      this.logger.log(`Permanently deleted download record ${downloadId}`);
    } catch (error) {
      this.logger.error(
        `Failed to permanently delete download ${downloadId}: ${error.message}`,
      );
      throw error;
    }
  }

  /**
   * Get download statistics for user
   * @param userId - User ID
   * @returns Download statistics
   */
  async getUserStats(userId: string): Promise<{
    totalDownloads: number;
    totalSize: number;
    activeDownloads: number;
    expiredDownloads: number;
  }> {
    try {
      const now = new Date();

      // Get all downloads
      const allDownloads = await this.prisma.downloadedFile.findMany({
        where: {
          userId,
          deletedAt: null,
        },
      });

      // Calculate statistics
      const totalDownloads = allDownloads.length;
      const totalSize = allDownloads.reduce(
        (sum, d) => sum + Number(d.size),
        0,
      );

      const activeDownloads = allDownloads.filter(
        (d) => d.expiresAt > now,
      ).length;

      const expiredDownloads = allDownloads.filter(
        (d) => d.expiresAt <= now,
      ).length;

      return {
        totalDownloads,
        totalSize,
        activeDownloads,
        expiredDownloads,
      };
    } catch (error) {
      this.logger.error(
        `Failed to get stats for user ${userId}: ${error.message}`,
      );

      return {
        totalDownloads: 0,
        totalSize: 0,
        activeDownloads: 0,
        expiredDownloads: 0,
      };
    }
  }

  /**
   * Get global download statistics
   * @returns Global statistics
   */
  async getGlobalStats(): Promise<{
    totalUsers: number;
    totalDownloads: number;
    totalSize: number;
    activeDownloads: number;
    expiredDownloads: number;
  }> {
    try {
      const now = new Date();

      // Get unique user count
      const users = await this.prisma.downloadedFile.findMany({
        where: {
          deletedAt: null,
        },
        select: {
          userId: true,
        },
        distinct: ['userId'],
      });

      // Get all downloads
      const allDownloads = await this.prisma.downloadedFile.findMany({
        where: {
          deletedAt: null,
        },
      });

      const totalDownloads = allDownloads.length;
      const totalSize = allDownloads.reduce(
        (sum, d) => sum + Number(d.size),
        0,
      );

      const activeDownloads = allDownloads.filter(
        (d) => d.expiresAt > now,
      ).length;

      const expiredDownloads = allDownloads.filter(
        (d) => d.expiresAt <= now,
      ).length;

      return {
        totalUsers: users.length,
        totalDownloads,
        totalSize,
        activeDownloads,
        expiredDownloads,
      };
    } catch (error) {
      this.logger.error(`Failed to get global stats: ${error.message}`);

      return {
        totalUsers: 0,
        totalDownloads: 0,
        totalSize: 0,
        activeDownloads: 0,
        expiredDownloads: 0,
      };
    }
  }

  /**
   * Clean up expired download records
   * @returns Number of records cleaned
   */
  async cleanupExpiredRecords(): Promise<number> {
    try {
      const expiredDownloads = await this.getExpiredDownloads();

      for (const download of expiredDownloads) {
        await this.permanentlyDeleteDownload(download.id);
      }

      this.logger.log(`Cleaned up ${expiredDownloads.length} expired records`);

      return expiredDownloads.length;
    } catch (error) {
      this.logger.error(`Failed to cleanup expired records: ${error.message}`);
      return 0;
    }
  }

  /**
   * Get downloads by email ID
   * @param emailId - Gmail message ID
   * @returns List of downloads for this email
   */
  async getDownloadsByEmail(emailId: string) {
    try {
      const downloads = await this.prisma.downloadedFile.findMany({
        where: {
          emailId,
          deletedAt: null,
        },
        orderBy: {
          downloadedAt: 'desc',
        },
      });

      return downloads.map((download) => ({
        ...download,
        size: Number(download.size),
      }));
    } catch (error) {
      this.logger.error(
        `Failed to get downloads for email ${emailId}: ${error.message}`,
      );
      return [];
    }
  }

  /**
   * Close Prisma connection
   * Called during module cleanup
   */
  async onModuleDestroy() {
    await this.prisma.$disconnect();
  }
}
