import { Process, Processor } from '@nestjs/bull';
import { Logger } from '@nestjs/common';
import { Job } from 'bull';
import { FileCleanupService } from './file-cleanup.service';

/**
 * Bull Queue Processor for File Cleanup
 * Processes cleanup jobs from the file-cleanup queue
 */
@Processor('file-cleanup')
export class FileCleanupProcessor {
  private readonly logger = new Logger(FileCleanupProcessor.name);

  constructor(private readonly fileCleanupService: FileCleanupService) {}

  /**
   * Process individual file cleanup job
   * Triggered 24 hours after file download
   */
  @Process('cleanup-file')
  async handleFileCleanup(job: Job<{ downloadId: string }>) {
    const { downloadId } = job.data;

    this.logger.log(`Processing cleanup job for download ${downloadId}`);

    try {
      await this.fileCleanupService.processFileCleanup(downloadId);

      this.logger.log(`Cleanup job completed for download ${downloadId}`);

      return { success: true, downloadId };
    } catch (error) {
      this.logger.error(
        `Cleanup job failed for download ${downloadId}: ${error.message}`,
        error.stack,
      );

      throw error; // Re-throw to trigger Bull retry
    }
  }

  /**
   * Process cleanup check job
   * Scans for any expired files that weren't cleaned up
   */
  @Process('cleanup-check')
  async handleCleanupCheck(job: Job) {
    this.logger.log('Processing cleanup check job');

    try {
      await this.fileCleanupService.handleHourlyCleanup();

      this.logger.log('Cleanup check job completed');

      return { success: true };
    } catch (error) {
      this.logger.error(
        `Cleanup check job failed: ${error.message}`,
        error.stack,
      );

      throw error;
    }
  }
}
