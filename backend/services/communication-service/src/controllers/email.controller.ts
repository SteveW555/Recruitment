/**
 * Email Classification API Controller
 * ProActive People - Recruitment Automation System
 */

import {
  Controller,
  Get,
  Post,
  Body,
  Param,
  Query,
  UseGuards,
  HttpStatus,
  HttpException
} from '@nestjs/common';
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiBearerAuth,
  ApiQuery
} from '@nestjs/swagger';
import { JwtAuthGuard } from '../guards/jwt-auth.guard';
import { RolesGuard } from '../guards/roles.guard';
import { Roles } from '../decorators/roles.decorator';
import { EmailIngestionService } from '../services/email-ingestion.service';
import {
  Email,
  EmailCategory,
  ClassificationRequest,
  ClassificationResponse,
  BulkClassificationRequest,
  BulkClassificationResponse
} from '../models/email.model';

@ApiTags('Email Classification')
@Controller('api/v1/emails')
@UseGuards(JwtAuthGuard, RolesGuard)
@ApiBearerAuth()
export class EmailController {
  constructor(
    private readonly emailIngestionService: EmailIngestionService
  ) {}

  /**
   * Webhook endpoint for SendGrid inbound emails
   */
  @Post('webhooks/sendgrid')
  @ApiOperation({ summary: 'Receive inbound email from SendGrid' })
  @ApiResponse({ status: 200, description: 'Email received and queued for processing' })
  async sendGridWebhook(@Body() payload: any) {
    try {
      await this.emailIngestionService.processSendGridWebhook(payload);
      return {
        success: true,
        message: 'Email received and queued for processing'
      };
    } catch (error) {
      throw new HttpException(
        `SendGrid webhook processing failed: ${error.message}`,
        HttpStatus.INTERNAL_SERVER_ERROR
      );
    }
  }

  /**
   * Webhook endpoint for AWS SES inbound emails
   */
  @Post('webhooks/ses')
  @ApiOperation({ summary: 'Receive inbound email from AWS SES' })
  @ApiResponse({ status: 200, description: 'Email received and queued for processing' })
  async sesWebhook(@Body() payload: any) {
    try {
      await this.emailIngestionService.processSESWebhook(payload);
      return {
        success: true,
        message: 'Email received and queued for processing'
      };
    } catch (error) {
      throw new HttpException(
        `SES webhook processing failed: ${error.message}`,
        HttpStatus.INTERNAL_SERVER_ERROR
      );
    }
  }

  /**
   * Classify a single email (manual trigger)
   */
  @Post('classify')
  @Roles('admin', 'recruiter', 'manager')
  @ApiOperation({ summary: 'Classify an email using AI' })
  @ApiResponse({
    status: 200,
    description: 'Email classified successfully',
    type: ClassificationResponse
  })
  async classifyEmail(
    @Body() request: ClassificationRequest
  ): Promise<ClassificationResponse> {
    const startTime = Date.now();

    try {
      const classification = await this.emailIngestionService.classifyEmail(
        request.emailId
      );

      return {
        emailId: request.emailId,
        classification,
        processingTimeMs: Date.now() - startTime
      };
    } catch (error) {
      throw new HttpException(
        `Classification failed: ${error.message}`,
        HttpStatus.INTERNAL_SERVER_ERROR
      );
    }
  }

  /**
   * Classify multiple emails in batch
   */
  @Post('classify/batch')
  @Roles('admin', 'manager')
  @ApiOperation({ summary: 'Classify multiple emails in batch' })
  @ApiResponse({
    status: 200,
    description: 'Batch classification completed',
    type: BulkClassificationResponse
  })
  async classifyBatch(
    @Body() request: BulkClassificationRequest
  ): Promise<BulkClassificationResponse> {
    const results: ClassificationResponse[] = [];
    const errors: Array<{ emailId: string; error: string }> = [];

    for (const emailId of request.emailIds) {
      const startTime = Date.now();

      try {
        const classification = await this.emailIngestionService.classifyEmail(emailId);

        results.push({
          emailId,
          classification,
          processingTimeMs: Date.now() - startTime
        });
      } catch (error) {
        errors.push({
          emailId,
          error: error.message
        });
      }
    }

    return {
      total: request.emailIds.length,
      successful: results.length,
      failed: errors.length,
      results,
      errors: errors.length > 0 ? errors : undefined
    };
  }

  /**
   * Get email by ID
   */
  @Get(':id')
  @Roles('admin', 'recruiter', 'manager', 'user')
  @ApiOperation({ summary: 'Get email by ID' })
  @ApiResponse({ status: 200, description: 'Email retrieved successfully' })
  @ApiResponse({ status: 404, description: 'Email not found' })
  async getEmail(@Param('id') id: string): Promise<Email> {
    try {
      const email = await this.emailIngestionService['emailRepository'].findOne({
        where: { id }
      });

      if (!email) {
        throw new HttpException('Email not found', HttpStatus.NOT_FOUND);
      }

      return email;
    } catch (error) {
      if (error instanceof HttpException) {
        throw error;
      }
      throw new HttpException(
        `Failed to retrieve email: ${error.message}`,
        HttpStatus.INTERNAL_SERVER_ERROR
      );
    }
  }

  /**
   * List emails with filtering
   */
  @Get()
  @Roles('admin', 'recruiter', 'manager')
  @ApiOperation({ summary: 'List emails with filtering' })
  @ApiQuery({ name: 'category', required: false, enum: EmailCategory })
  @ApiQuery({ name: 'processed', required: false, type: Boolean })
  @ApiQuery({ name: 'startDate', required: false, type: Date })
  @ApiQuery({ name: 'endDate', required: false, type: Date })
  @ApiQuery({ name: 'limit', required: false, type: Number })
  @ApiQuery({ name: 'offset', required: false, type: Number })
  @ApiResponse({ status: 200, description: 'Emails retrieved successfully' })
  async listEmails(
    @Query('category') category?: EmailCategory,
    @Query('processed') processed?: boolean,
    @Query('startDate') startDate?: Date,
    @Query('endDate') endDate?: Date,
    @Query('limit') limit: number = 50,
    @Query('offset') offset: number = 0
  ) {
    try {
      const query = this.emailIngestionService['emailRepository']
        .createQueryBuilder('email')
        .orderBy('email.receivedAt', 'DESC')
        .take(limit)
        .skip(offset);

      if (category) {
        query.andWhere('email.classification.category = :category', { category });
      }

      if (processed !== undefined) {
        query.andWhere('email.processed = :processed', { processed });
      }

      if (startDate) {
        query.andWhere('email.receivedAt >= :startDate', { startDate });
      }

      if (endDate) {
        query.andWhere('email.receivedAt <= :endDate', { endDate });
      }

      const [emails, total] = await query.getManyAndCount();

      return {
        data: emails,
        total,
        limit,
        offset,
        hasMore: total > offset + limit
      };
    } catch (error) {
      throw new HttpException(
        `Failed to list emails: ${error.message}`,
        HttpStatus.INTERNAL_SERVER_ERROR
      );
    }
  }

  /**
   * Get email statistics
   */
  @Get('stats/overview')
  @Roles('admin', 'manager')
  @ApiOperation({ summary: 'Get email classification statistics' })
  @ApiQuery({ name: 'startDate', required: false, type: Date })
  @ApiQuery({ name: 'endDate', required: false, type: Date })
  @ApiResponse({ status: 200, description: 'Statistics retrieved successfully' })
  async getStats(
    @Query('startDate') startDate?: Date,
    @Query('endDate') endDate?: Date
  ) {
    try {
      return await this.emailIngestionService.getStats(startDate, endDate);
    } catch (error) {
      throw new HttpException(
        `Failed to retrieve statistics: ${error.message}`,
        HttpStatus.INTERNAL_SERVER_ERROR
      );
    }
  }

  /**
   * Get emails by category
   */
  @Get('category/:category')
  @Roles('admin', 'recruiter', 'manager')
  @ApiOperation({ summary: 'Get emails by category' })
  @ApiResponse({ status: 200, description: 'Emails retrieved successfully' })
  async getEmailsByCategory(
    @Param('category') category: EmailCategory,
    @Query('limit') limit: number = 50,
    @Query('offset') offset: number = 0
  ) {
    try {
      const [emails, total] = await this.emailIngestionService['emailRepository']
        .createQueryBuilder('email')
        .where('email.classification.category = :category', { category })
        .orderBy('email.receivedAt', 'DESC')
        .take(limit)
        .skip(offset)
        .getManyAndCount();

      return {
        category,
        data: emails,
        total,
        limit,
        offset
      };
    } catch (error) {
      throw new HttpException(
        `Failed to retrieve emails: ${error.message}`,
        HttpStatus.INTERNAL_SERVER_ERROR
      );
    }
  }

  /**
   * Get unprocessed emails
   */
  @Get('processing/pending')
  @Roles('admin', 'manager')
  @ApiOperation({ summary: 'Get emails pending processing' })
  @ApiResponse({ status: 200, description: 'Pending emails retrieved successfully' })
  async getPendingEmails(
    @Query('limit') limit: number = 100
  ) {
    try {
      const emails = await this.emailIngestionService['emailRepository'].find({
        where: { processed: false },
        order: { receivedAt: 'ASC' },
        take: limit
      });

      return {
        count: emails.length,
        data: emails
      };
    } catch (error) {
      throw new HttpException(
        `Failed to retrieve pending emails: ${error.message}`,
        HttpStatus.INTERNAL_SERVER_ERROR
      );
    }
  }

  /**
   * Get emails requiring manual review
   */
  @Get('review/needed')
  @Roles('admin', 'manager')
  @ApiOperation({ summary: 'Get emails requiring manual review (low confidence)' })
  @ApiResponse({ status: 200, description: 'Emails needing review retrieved successfully' })
  async getReviewNeeded(
    @Query('confidenceThreshold') threshold: number = 0.6,
    @Query('limit') limit: number = 50
  ) {
    try {
      const emails = await this.emailIngestionService['emailRepository']
        .createQueryBuilder('email')
        .where('email.processed = :processed', { processed: true })
        .andWhere('email.classification.confidence < :threshold', { threshold })
        .orderBy('email.classification.confidence', 'ASC')
        .take(limit)
        .getMany();

      return {
        threshold,
        count: emails.length,
        data: emails
      };
    } catch (error) {
      throw new HttpException(
        `Failed to retrieve emails needing review: ${error.message}`,
        HttpStatus.INTERNAL_SERVER_ERROR
      );
    }
  }

  /**
   * Manually update email classification
   */
  @Post(':id/classification')
  @Roles('admin', 'manager')
  @ApiOperation({ summary: 'Manually update email classification' })
  @ApiResponse({ status: 200, description: 'Classification updated successfully' })
  async updateClassification(
    @Param('id') id: string,
    @Body() classification: Partial<any>
  ) {
    try {
      const email = await this.emailIngestionService['emailRepository'].findOne({
        where: { id }
      });

      if (!email) {
        throw new HttpException('Email not found', HttpStatus.NOT_FOUND);
      }

      email.classification = {
        ...email.classification,
        ...classification,
        classifiedBy: 'manual',
        classifiedAt: new Date()
      } as any;

      email.updatedAt = new Date();
      await this.emailIngestionService['emailRepository'].save(email);

      // Re-route if category changed
      if (classification.category && classification.category !== email.classification?.category) {
        await this.emailIngestionService.routeEmail(id);
      }

      return {
        success: true,
        email
      };
    } catch (error) {
      if (error instanceof HttpException) {
        throw error;
      }
      throw new HttpException(
        `Failed to update classification: ${error.message}`,
        HttpStatus.INTERNAL_SERVER_ERROR
      );
    }
  }

  /**
   * Health check endpoint
   */
  @Get('health')
  @ApiOperation({ summary: 'Health check for email service' })
  @ApiResponse({ status: 200, description: 'Service is healthy' })
  async healthCheck() {
    return {
      status: 'healthy',
      service: 'email-classification',
      timestamp: new Date().toISOString()
    };
  }
}
