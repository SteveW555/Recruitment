import { Injectable, Logger, OnModuleInit } from '@nestjs/common';
import { Cron, CronExpression } from '@nestjs/schedule';
import { InjectQueue } from '@nestjs/bull';
import { Queue } from 'bull';
import { FileStorageService } from './file-storage.service';
import { DownloadTrackingService } from './download-tracking.service';

/**
 * File Cleanup Service
 * Implements 24-hour file retention policy (FR-010)
 * Uses Bull queue for scheduled cleanup and cron for periodic checks
 */
@Injectable()
export class FileCleanupService implements OnModuleInit {
  private readonly logger = new Logger(FileCleanupService.name);

  constructor(
    @InjectQueue('file-cleanup') private readonly cleanupQueue: Queue,
    private readonly fileStorage: FileStorageService,
    private readonly downloadTracking: DownloadTrackingService,
  ) {}

  /**
   * Initialize service - schedule initial cleanup
   */
  async onModuleInit() {
    this.logger.log('File cleanup service initialized');

    // Schedule immediate cleanup check on startup
    await this.scheduleCleanupCheck();
  }

  /**
   * Schedule cleanup job for a specific file
   * Called when file is downloaded - schedules cleanup 24 hours later
   * @param downloadId - Download record ID
   * @param expiresAt - Expiry date
   */
  async scheduleFileCleanup(
    downloadId: string,
    expiresAt: Date,
  ): Promise<void> {
    const delay = expiresAt.getTime() - Date.now();

    if (delay <= 0) {
      // Already expired - cleanup immediately
      this.logger.warn(
        `File ${downloadId} already expired, scheduling immediate cleanup`,
      );
      await this.cleanupQueue.add(
        'cleanup-file',
        { downloadId },
        { delay: 0 },
      );
      return;
    }

    // Schedule cleanup job
    await this.cleanupQueue.add(
      'cleanup-file',
      { downloadId },
      {
        delay, // Delay in milliseconds
        removeOnComplete: true,
        removeOnFail: false,
      },
    );

    this.logger.log(
      `Scheduled cleanup for ${downloadId} in ${Math.round(delay / 1000 / 60)} minutes`,
    );
  }

  /**
   * Process cleanup job (Bull queue processor)
   * @param downloadId - Download record ID
   */
  async processFileCleanup(downloadId: string): Promise<void> {
    try {
      this.logger.log(`Processing cleanup for download ${downloadId}`);

      // Get download record
      const download = await this.downloadTracking.getDownload(downloadId);

      if (!download) {
        this.logger.warn(`Download ${downloadId} not found, skipping cleanup`);
        return;
      }

      if (download.deletedAt) {
        this.logger.warn(
          `Download ${downloadId} already deleted, skipping cleanup`,
        );
        return;
      }

      // Delete file from storage
      await this.fileStorage.deleteFile(download.localPath);

      // Mark as deleted in database
      await this.downloadTracking.deleteDownload(downloadId);

      this.logger.log(
        `Successfully cleaned up download ${downloadId} (${download.filename})`,
      );
    } catch (error) {
      this.logger.error(
        `Failed to cleanup download ${downloadId}: ${error.message}`,
        error.stack,
      );
      throw error; // Re-throw to trigger Bull retry
    }
  }

  /**
   * Schedule cleanup check (called on startup and periodically)
   */
  async scheduleCleanupCheck(): Promise<void> {
    await this.cleanupQueue.add(
      'cleanup-check',
      {},
      {
        delay: 0,
        removeOnComplete: true,
      },
    );

    this.logger.log('Scheduled cleanup check');
  }

  /**
   * Cron job: Check for expired files every hour
   * Implements FR-010: 24-hour retention policy
   */
  @Cron(CronExpression.EVERY_HOUR)
  async handleHourlyCleanup(): Promise<void> {
    this.logger.log('Running hourly cleanup check');

    try {
      // Get all expired downloads
      const expiredDownloads = await this.downloadTracking.getExpiredDownloads();

      if (expiredDownloads.length === 0) {
        this.logger.log('No expired files found');
        return;
      }

      this.logger.log(`Found ${expiredDownloads.length} expired files`);

      // Process each expired download
      for (const download of expiredDownloads) {
        try {
          await this.processFileCleanup(download.id);
        } catch (error) {
          this.logger.error(
            `Failed to cleanup ${download.id}: ${error.message}`,
          );
          // Continue with next file
        }
      }

      this.logger.log(`Hourly cleanup completed`);
    } catch (error) {
      this.logger.error(`Hourly cleanup failed: ${error.message}`);
    }
  }

  /**
   * Cron job: Cleanup empty directories every 6 hours
   */
  @Cron(CronExpression.EVERY_6_HOURS)
  async handleDirectoryCleanup(): Promise<void> {
    this.logger.log('Running directory cleanup');

    try {
      const cleanedCount = await this.fileStorage.cleanupEmptyDirectories();
      this.logger.log(`Cleaned up ${cleanedCount} empty directories`);
    } catch (error) {
      this.logger.error(`Directory cleanup failed: ${error.message}`);
    }
  }

  /**
   * Cron job: Database record cleanup (daily at 2 AM)
   * Remove old deleted records from database
   */
  @Cron('0 2 * * *') // Daily at 2 AM
  async handleDatabaseCleanup(): Promise<void> {
    this.logger.log('Running database cleanup');

    try {
      const cleanedCount = await this.downloadTracking.cleanupExpiredRecords();
      this.logger.log(`Cleaned up ${cleanedCount} old database records`);
    } catch (error) {
      this.logger.error(`Database cleanup failed: ${error.message}`);
    }
  }

  /**
   * Manual cleanup trigger (admin function)
   * Forces immediate cleanup of all expired files
   * @returns Cleanup results
   */
  async forceCleanup(): Promise<{
    filesDeleted: number;
    directoriesDeleted: number;
    recordsDeleted: number;
  }> {
    this.logger.log('Force cleanup triggered');

    try {
      // Cleanup expired files
      const expiredDownloads = await this.downloadTracking.getExpiredDownloads();

      for (const download of expiredDownloads) {
        await this.processFileCleanup(download.id);
      }

      // Cleanup empty directories
      const directoriesDeleted = await this.fileStorage.cleanupEmptyDirectories();

      // Cleanup database records
      const recordsDeleted = await this.downloadTracking.cleanupExpiredRecords();

      const result = {
        filesDeleted: expiredDownloads.length,
        directoriesDeleted,
        recordsDeleted,
      };

      this.logger.log(`Force cleanup completed: ${JSON.stringify(result)}`);

      return result;
    } catch (error) {
      this.logger.error(`Force cleanup failed: ${error.message}`);
      throw error;
    }
  }

  /**
   * Get cleanup queue statistics
   * @returns Queue statistics
   */
  async getQueueStats(): Promise<{
    waiting: number;
    active: number;
    completed: number;
    failed: number;
    delayed: number;
  }> {
    try {
      const [waiting, active, completed, failed, delayed] = await Promise.all([
        this.cleanupQueue.getWaitingCount(),
        this.cleanupQueue.getActiveCount(),
        this.cleanupQueue.getCompletedCount(),
        this.cleanupQueue.getFailedCount(),
        this.cleanupQueue.getDelayedCount(),
      ]);

      return {
        waiting,
        active,
        completed,
        failed,
        delayed,
      };
    } catch (error) {
      this.logger.error(`Failed to get queue stats: ${error.message}`);
      return {
        waiting: 0,
        active: 0,
        completed: 0,
        failed: 0,
        delayed: 0,
      };
    }
  }

  /**
   * Pause cleanup queue (admin function)
   */
  async pauseCleanup(): Promise<void> {
    await this.cleanupQueue.pause();
    this.logger.log('Cleanup queue paused');
  }

  /**
   * Resume cleanup queue (admin function)
   */
  async resumeCleanup(): Promise<void> {
    await this.cleanupQueue.resume();
    this.logger.log('Cleanup queue resumed');
  }

  /**
   * Clear all cleanup jobs (admin function - use with caution)
   */
  async clearAllJobs(): Promise<void> {
    await this.cleanupQueue.empty();
    this.logger.warn('Cleared all cleanup jobs from queue');
  }
}
