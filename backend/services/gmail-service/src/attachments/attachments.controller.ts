import {
  Controller,
  Get,
  Post,
  Delete,
  Param,
  Body,
  Res,
  Req,
  UseGuards,
  StreamableFile,
  BadRequestException,
} from '@nestjs/common';
import { Response, Request } from 'express';
import { AttachmentService } from './attachment.service';
import { BulkDownloadService } from './bulk-download.service';
import { FileCleanupService } from './file-cleanup.service';
import { AuthGuard } from '../auth/auth.guard';
import * as path from 'path';

/**
 * Attachments Controller
 * Handles attachment downloads, bulk downloads, and file management
 * Implements FR-007: Download CV attachments
 */
@Controller('attachments')
@UseGuards(AuthGuard)
export class AttachmentsController {
  constructor(
    private readonly attachmentService: AttachmentService,
    private readonly bulkDownloadService: BulkDownloadService,
    private readonly fileCleanupService: FileCleanupService,
  ) {}

  /**
   * Download single attachment from email
   * POST /api/v1/attachments/download
   * Body: { emailId, attachmentId, filename }
   */
  @Post('download')
  async downloadAttachment(
    @Req() req: Request,
    @Body('emailId') emailId: string,
    @Body('attachmentId') attachmentId: string,
    @Body('filename') filename: string,
  ) {
    const sessionData = req.session as any;
    const userId = sessionData.userId;

    if (!emailId || !attachmentId || !filename) {
      throw new BadRequestException(
        'emailId, attachmentId, and filename are required',
      );
    }

    const download = await this.attachmentService.downloadAttachment(
      userId,
      emailId,
      attachmentId,
      filename,
    );

    // Schedule cleanup after 24 hours
    await this.fileCleanupService.scheduleFileCleanup(
      download.downloadId,
      download.expiresAt,
    );

    return {
      success: true,
      data: download,
    };
  }

  /**
   * Download all attachments from an email
   * POST /api/v1/attachments/download-email
   * Body: { emailId, attachments: [{ attachmentId, filename }] }
   */
  @Post('download-email')
  async downloadEmailAttachments(
    @Req() req: Request,
    @Body('emailId') emailId: string,
    @Body('attachments') attachments: Array<{ attachmentId: string; filename: string }>,
  ) {
    const sessionData = req.session as any;
    const userId = sessionData.userId;

    if (!emailId || !Array.isArray(attachments)) {
      throw new BadRequestException(
        'emailId and attachments array are required',
      );
    }

    const downloads = await this.attachmentService.downloadEmailAttachments(
      userId,
      emailId,
      attachments,
    );

    // Schedule cleanup for all downloads
    for (const download of downloads) {
      await this.fileCleanupService.scheduleFileCleanup(
        download.downloadId,
        download.expiresAt,
      );
    }

    return {
      success: true,
      data: {
        totalDownloads: downloads.length,
        downloads,
      },
    };
  }

  /**
   * Get downloaded file (serve file)
   * GET /api/v1/attachments/downloads/:downloadId
   */
  @Get('downloads/:downloadId')
  async getDownloadedFile(
    @Req() req: Request,
    @Param('downloadId') downloadId: string,
    @Res({ passthrough: true }) res: Response,
  ) {
    const sessionData = req.session as any;
    const userId = sessionData.userId;

    const file = await this.attachmentService.getDownloadedFile(
      userId,
      downloadId,
    );

    // Set response headers
    res.set({
      'Content-Type': file.mimeType,
      'Content-Disposition': `attachment; filename="${file.filename}"`,
      'Content-Length': file.buffer.length,
    });

    return new StreamableFile(file.buffer);
  }

  /**
   * List user's downloads
   * GET /api/v1/attachments/downloads
   */
  @Get('downloads')
  async listDownloads(@Req() req: Request) {
    const sessionData = req.session as any;
    const userId = sessionData.userId;

    const downloads = await this.attachmentService.listDownloads(userId);

    return {
      success: true,
      data: {
        totalDownloads: downloads.length,
        downloads,
      },
    };
  }

  /**
   * Delete downloaded file
   * DELETE /api/v1/attachments/downloads/:downloadId
   */
  @Delete('downloads/:downloadId')
  async deleteDownload(
    @Req() req: Request,
    @Param('downloadId') downloadId: string,
  ) {
    const sessionData = req.session as any;
    const userId = sessionData.userId;

    await this.attachmentService.deleteDownload(userId, downloadId);

    return {
      success: true,
      message: 'Download deleted successfully',
    };
  }

  /**
   * Bulk download multiple files as ZIP
   * POST /api/v1/attachments/bulk-download
   * Body: { downloadIds: string[] }
   */
  @Post('bulk-download')
  async bulkDownload(
    @Req() req: Request,
    @Body('downloadIds') downloadIds: string[],
    @Res({ passthrough: true }) res: Response,
  ) {
    const sessionData = req.session as any;
    const userId = sessionData.userId;

    if (!Array.isArray(downloadIds) || downloadIds.length === 0) {
      throw new BadRequestException('downloadIds array is required and must not be empty');
    }

    const zipBuffer = await this.bulkDownloadService.createZipArchive(
      userId,
      downloadIds,
    );

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `attachments-${timestamp}.zip`;

    res.set({
      'Content-Type': 'application/zip',
      'Content-Disposition': `attachment; filename="${filename}"`,
      'Content-Length': zipBuffer.length,
    });

    return new StreamableFile(zipBuffer);
  }

  /**
   * Get download statistics
   * GET /api/v1/attachments/stats
   */
  @Get('stats')
  async getDownloadStats(@Req() req: Request) {
    const sessionData = req.session as any;
    const userId = sessionData.userId;

    const stats = await this.attachmentService.getDownloadStats(userId);

    return {
      success: true,
      data: stats,
    };
  }

  /**
   * Get cleanup queue statistics (admin)
   * GET /api/v1/attachments/cleanup/stats
   */
  @Get('cleanup/stats')
  async getCleanupStats() {
    const stats = await this.fileCleanupService.getQueueStats();

    return {
      success: true,
      data: stats,
    };
  }

  /**
   * Force cleanup of expired files (admin)
   * POST /api/v1/attachments/cleanup/force
   */
  @Post('cleanup/force')
  async forceCleanup() {
    const result = await this.fileCleanupService.forceCleanup();

    return {
      success: true,
      data: result,
    };
  }

  /**
   * Health check
   * GET /api/v1/attachments/health
   */
  @Get('health')
  async healthCheck() {
    return {
      success: true,
      service: 'attachments',
      timestamp: new Date().toISOString(),
      status: 'healthy',
    };
  }
}
