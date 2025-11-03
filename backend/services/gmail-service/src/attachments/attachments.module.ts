import { Module, OnModuleInit } from '@nestjs/common';
import { BullModule } from '@nestjs/bull';

// Controllers
import { AttachmentsController } from './attachments.controller';

// Services
import { AttachmentService } from './attachment.service';
import { MimeValidationService } from './mime-validation.service';
import { FileStorageService } from './file-storage.service';
import { DownloadTrackingService } from './download-tracking.service';
import { BulkDownloadService } from './bulk-download.service';
import { FileCleanupService } from './file-cleanup.service';

// Processors
import { FileCleanupProcessor } from './file-cleanup.processor';

// Import Gmail module services
import { GmailModule } from '../gmail/gmail.module';

/**
 * Attachments Module
 * Handles file downloads, MIME validation, storage, and cleanup
 *
 * Features:
 * - Download attachments from Gmail (FR-007)
 * - MIME type validation (FR-009)
 * - 24-hour file retention (FR-010)
 * - Bulk download with ZIP creation
 * - Automated cleanup with Bull queue
 * - Cron jobs for expired file cleanup
 */
@Module({
  imports: [
    // Bull Queue for file cleanup
    BullModule.registerQueue({
      name: 'file-cleanup',
      defaultJobOptions: {
        attempts: 3, // Retry failed jobs 3 times
        backoff: {
          type: 'exponential',
          delay: 5000, // Start with 5 seconds
        },
        removeOnComplete: 100, // Keep last 100 completed jobs
        removeOnFail: false, // Keep failed jobs for debugging
      },
    }),

    // Import Gmail module for API access
    GmailModule,
  ],
  controllers: [AttachmentsController],
  providers: [
    // Core services
    AttachmentService,
    MimeValidationService,
    FileStorageService,
    DownloadTrackingService,
    BulkDownloadService,
    FileCleanupService,

    // Bull processors
    FileCleanupProcessor,
  ],
  exports: [
    // Export services for use in other modules
    AttachmentService,
    MimeValidationService,
    FileStorageService,
    DownloadTrackingService,
    BulkDownloadService,
    FileCleanupService,
  ],
})
export class AttachmentsModule implements OnModuleInit {
  constructor(private readonly fileStorage: FileStorageService) {}

  /**
   * Initialize module - ensure storage directory exists
   */
  async onModuleInit() {
    await this.fileStorage.initialize();
  }
}
