/**
 * Email Ingestion and Routing Service
 * ProActive People - Recruitment Automation System
 *
 * Handles incoming emails from SendGrid/SES webhooks and routes them
 * to appropriate handlers based on AI classification.
 */

import { Injectable, Logger } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Queue } from 'bull';
import { InjectQueue } from '@nestjs/bull';
import {
  Email,
  EmailCategory,
  EmailClassification,
  EmailPriority,
  EmailAddress,
  EmailAttachment
} from '../models/email.model';
import { PythonShell } from 'python-shell';

@Injectable()
export class EmailIngestionService {
  private readonly logger = new Logger(EmailIngestionService.name);

  constructor(
    @InjectRepository(Email)
    private emailRepository: Repository<Email>,
    @InjectQueue('email-processing') private emailQueue: Queue,
    @InjectQueue('email-routing') private routingQueue: Queue
  ) {}

  /**
   * Process incoming email webhook from SendGrid
   */
  async processSendGridWebhook(payload: any): Promise<void> {
    try {
      const email = this.parseSendGridPayload(payload);
      await this.ingestEmail(email);
    } catch (error) {
      this.logger.error(`SendGrid webhook processing failed: ${error.message}`, error.stack);
      throw error;
    }
  }

  /**
   * Process incoming email webhook from AWS SES
   */
  async processSESWebhook(payload: any): Promise<void> {
    try {
      const email = this.parseSESPayload(payload);
      await this.ingestEmail(email);
    } catch (error) {
      this.logger.error(`SES webhook processing failed: ${error.message}`, error.stack);
      throw error;
    }
  }

  /**
   * Main email ingestion pipeline
   */
  async ingestEmail(emailData: Partial<Email>): Promise<Email> {
    const startTime = Date.now();

    try {
      // 1. Store raw email
      const email = this.emailRepository.create({
        ...emailData,
        receivedAt: new Date(),
        processed: false,
        routed: false,
        archived: false,
        createdAt: new Date(),
        updatedAt: new Date()
      });

      await this.emailRepository.save(email);
      this.logger.log(`Email ${email.id} ingested from ${email.from.email}`);

      // 2. Queue for classification
      await this.emailQueue.add('classify', {
        emailId: email.id,
        priority: this.determinePriority(email)
      }, {
        priority: this.getQueuePriority(email),
        attempts: 3,
        backoff: {
          type: 'exponential',
          delay: 2000
        }
      });

      this.logger.log(`Email ${email.id} queued for classification (${Date.now() - startTime}ms)`);

      return email;

    } catch (error) {
      this.logger.error(`Email ingestion failed: ${error.message}`, error.stack);
      throw error;
    }
  }

  /**
   * Classify email using Python AI classifier
   */
  async classifyEmail(emailId: string): Promise<EmailClassification> {
    const email = await this.emailRepository.findOne({ where: { id: emailId } });

    if (!email) {
      throw new Error(`Email ${emailId} not found`);
    }

    try {
      // Call Python email classifier
      const classification = await this.runPythonClassifier(email);

      // Update email with classification
      email.classification = classification;
      email.processed = true;
      email.processedAt = new Date();
      email.updatedAt = new Date();

      await this.emailRepository.save(email);
      this.logger.log(`Email ${emailId} classified as ${classification.category} (confidence: ${classification.confidence})`);

      // Queue for routing
      await this.routingQueue.add('route', {
        emailId: email.id,
        category: classification.category,
        priority: classification.priority
      }, {
        priority: classification.priority === EmailPriority.URGENT ? 1 : 5
      });

      return classification;

    } catch (error) {
      this.logger.error(`Classification failed for email ${emailId}: ${error.message}`, error.stack);

      // Set default classification on error
      const fallbackClassification: EmailClassification = {
        category: EmailCategory.OTHER,
        confidence: 0.1,
        priority: EmailPriority.NORMAL,
        sentiment: 'neutral' as any,
        keywords: [],
        entities: {},
        requiresAction: false,
        classifiedAt: new Date(),
        classifiedBy: 'rule-based'
      };

      email.classification = fallbackClassification;
      email.processed = true;
      email.processedAt = new Date();
      await this.emailRepository.save(email);

      return fallbackClassification;
    }
  }

  /**
   * Route email to appropriate handlers based on classification
   */
  async routeEmail(emailId: string): Promise<void> {
    const email = await this.emailRepository.findOne({
      where: { id: emailId },
      relations: ['classification']
    });

    if (!email || !email.classification) {
      throw new Error(`Email ${emailId} not found or not classified`);
    }

    const { category, subCategory, priority, requiresAction } = email.classification;
    const routes: string[] = [];

    try {
      // Route based on category
      switch (category) {
        case EmailCategory.CANDIDATE:
          routes.push(...await this.routeCandidateEmail(email));
          break;

        case EmailCategory.CLIENT:
          routes.push(...await this.routeClientEmail(email));
          break;

        case EmailCategory.SUPPLIER:
          routes.push(...await this.routeSupplierEmail(email));
          break;

        case EmailCategory.STAFF:
          routes.push(...await this.routeStaffEmail(email));
          break;

        case EmailCategory.OTHER:
        default:
          routes.push('general-inbox');
          break;
      }

      // Special handling for urgent/high priority
      if (priority === EmailPriority.URGENT || priority === EmailPriority.HIGH) {
        routes.push('priority-queue');
        await this.sendUrgentNotification(email);
      }

      // Update email routing info
      email.routed = true;
      email.routedTo = routes;
      email.updatedAt = new Date();
      await this.emailRepository.save(email);

      this.logger.log(`Email ${emailId} routed to: ${routes.join(', ')}`);

    } catch (error) {
      this.logger.error(`Routing failed for email ${emailId}: ${error.message}`, error.stack);
      throw error;
    }
  }

  /**
   * Route candidate emails to appropriate handlers
   */
  private async routeCandidateEmail(email: Email): Promise<string[]> {
    const routes: string[] = ['candidate-service'];

    const subCategory = email.classification?.subCategory;

    // Parse CV if attached
    if (email.attachments?.some(att => att.isCV)) {
      await this.emailQueue.add('parse-cv', {
        emailId: email.id,
        attachments: email.attachments.filter(att => att.isCV)
      });
      routes.push('cv-parser');
    }

    // Route based on subcategory
    switch (subCategory) {
      case 'application':
      case 'cv_submission':
        routes.push('recruitment-team', 'matching-engine');
        break;

      case 'interview_response':
        routes.push('scheduling-service');
        break;

      case 'availability_update':
        routes.push('workflow-service');
        break;

      case 'reference_check':
        routes.push('placement-service');
        break;
    }

    return routes;
  }

  /**
   * Route client emails to appropriate handlers
   */
  private async routeClientEmail(email: Email): Promise<string[]> {
    const routes: string[] = ['client-service'];

    const subCategory = email.classification?.subCategory;

    switch (subCategory) {
      case 'job_brief':
        routes.push('job-service', 'account-manager');
        break;

      case 'feedback':
        routes.push('workflow-service', 'recruitment-consultant');
        break;

      case 'interview_request':
        routes.push('scheduling-service');
        break;

      case 'placement_update':
        routes.push('placement-service');
        break;

      case 'contract_query':
        routes.push('finance-service', 'contracts-team');
        break;

      default:
        routes.push('account-manager');
    }

    return routes;
  }

  /**
   * Route supplier emails to appropriate handlers
   */
  private async routeSupplierEmail(email: Email): Promise<string[]> {
    const routes: string[] = ['integration-hub'];

    const subCategory = email.classification?.subCategory;
    const fromDomain = email.from.email.split('@')[1].toLowerCase();

    // Route to specific integration handlers
    if (fromDomain.includes('bullhorn')) {
      routes.push('bullhorn-sync');
    } else if (fromDomain.includes('broadbean')) {
      routes.push('broadbean-service');
    }

    switch (subCategory) {
      case 'invoice':
        routes.push('finance-service', 'accounts-payable');
        break;

      case 'service_update':
      case 'integration_issue':
        routes.push('it-team');
        break;
    }

    return routes;
  }

  /**
   * Route staff emails to appropriate handlers
   */
  private async routeStaffEmail(email: Email): Promise<string[]> {
    const routes: string[] = ['internal-inbox'];

    const subCategory = email.classification?.subCategory;

    switch (subCategory) {
      case 'hr_matter':
        routes.push('hr-team');
        break;

      case 'team_update':
        routes.push('team-broadcast');
        break;

      default:
        // Parse recipient to route to specific user
        if (email.to.length > 0) {
          const recipientEmail = email.to[0].email;
          routes.push(`user:${recipientEmail}`);
        }
    }

    return routes;
  }

  /**
   * Send urgent notification for high priority emails
   */
  private async sendUrgentNotification(email: Email): Promise<void> {
    // This would integrate with your notification service
    this.logger.warn(`URGENT EMAIL: ${email.subject} from ${email.from.email}`);

    // Could send Slack notification, SMS, push notification, etc.
    // await this.notificationService.sendUrgent({
    //   title: `Urgent Email: ${email.classification?.category}`,
    //   message: email.subject,
    //   from: email.from.email
    // });
  }

  /**
   * Call Python email classifier via shell
   */
  private async runPythonClassifier(email: Email): Promise<EmailClassification> {
    return new Promise((resolve, reject) => {
      const options = {
        mode: 'json' as const,
        pythonPath: 'python',
        scriptPath: process.env.PYTHON_SCRIPTS_PATH || './scripts',
        args: [
          '--from', email.from.email,
          '--subject', email.subject,
          '--body', email.bodyText,
          '--to', JSON.stringify(email.to.map(t => t.email)),
          '--attachments', JSON.stringify(email.attachments?.map(a => a.filename) || [])
        ]
      };

      PythonShell.run('classify_email.py', options, (err, results) => {
        if (err) {
          reject(err);
        } else if (results && results.length > 0) {
          const result = results[0] as any;

          const classification: EmailClassification = {
            category: result.category as EmailCategory,
            subCategory: result.subcategory,
            confidence: result.confidence,
            priority: result.priority as EmailPriority,
            sentiment: result.sentiment,
            keywords: result.keywords || [],
            entities: result.entities || {},
            requiresAction: result.requires_action || false,
            suggestedActions: result.suggested_actions || [],
            classifiedAt: new Date(),
            classifiedBy: 'ai'
          };

          resolve(classification);
        } else {
          reject(new Error('No classification result from Python script'));
        }
      });
    });
  }

  /**
   * Parse SendGrid webhook payload into Email object
   */
  private parseSendGridPayload(payload: any): Partial<Email> {
    return {
      messageId: payload.msg_id || payload.sg_message_id,
      from: {
        email: payload.from || payload.email,
        name: payload.from_name
      },
      to: payload.to ? [{ email: payload.to }] : [],
      subject: payload.subject,
      bodyText: payload.text,
      bodyHtml: payload.html,
      attachments: payload.attachments?.map((att: any) => ({
        filename: att.filename,
        contentType: att.type,
        size: att.size,
        storageUrl: att.url
      })),
      direction: 'inbound',
      source: 'sendgrid'
    };
  }

  /**
   * Parse AWS SES webhook payload into Email object
   */
  private parseSESPayload(payload: any): Partial<Email> {
    const mail = payload.mail;
    const content = payload.content;

    return {
      messageId: mail.messageId,
      from: {
        email: mail.source,
        name: mail.commonHeaders?.from?.[0]
      },
      to: mail.destination?.map((email: string) => ({ email })) || [],
      subject: mail.commonHeaders?.subject,
      bodyText: content?.textContent,
      bodyHtml: content?.htmlContent,
      direction: 'inbound',
      source: 'ses',
      sentAt: new Date(mail.timestamp)
    };
  }

  /**
   * Determine initial priority based on email characteristics
   */
  private determinePriority(email: Partial<Email>): EmailPriority {
    const subject = (email.subject || '').toLowerCase();
    const body = (email.bodyText || '').toLowerCase();

    // Check for urgent keywords
    const urgentKeywords = ['urgent', 'asap', 'emergency', 'critical', 'immediately'];
    if (urgentKeywords.some(keyword => subject.includes(keyword) || body.includes(keyword))) {
      return EmailPriority.URGENT;
    }

    // Check for high priority keywords
    const highPriorityKeywords = ['important', 'priority', 'time-sensitive', 'deadline'];
    if (highPriorityKeywords.some(keyword => subject.includes(keyword) || body.includes(keyword))) {
      return EmailPriority.HIGH;
    }

    return EmailPriority.NORMAL;
  }

  /**
   * Get Bull queue priority (lower number = higher priority)
   */
  private getQueuePriority(email: Partial<Email>): number {
    const priority = this.determinePriority(email);

    switch (priority) {
      case EmailPriority.URGENT:
        return 1;
      case EmailPriority.HIGH:
        return 3;
      case EmailPriority.NORMAL:
        return 5;
      case EmailPriority.LOW:
        return 7;
      default:
        return 5;
    }
  }

  /**
   * Get email statistics
   */
  async getStats(startDate?: Date, endDate?: Date) {
    const query = this.emailRepository.createQueryBuilder('email');

    if (startDate) {
      query.andWhere('email.receivedAt >= :startDate', { startDate });
    }
    if (endDate) {
      query.andWhere('email.receivedAt <= :endDate', { endDate });
    }

    const [emails, total] = await query.getManyAndCount();

    const stats = {
      total,
      byCategory: {} as Record<string, number>,
      byPriority: {} as Record<string, number>,
      avgConfidence: 0,
      needsReview: 0,
      processed: emails.filter(e => e.processed).length,
      routed: emails.filter(e => e.routed).length
    };

    let totalConfidence = 0;
    let confidenceCount = 0;

    emails.forEach(email => {
      if (email.classification) {
        const cat = email.classification.category;
        const pri = email.classification.priority;

        stats.byCategory[cat] = (stats.byCategory[cat] || 0) + 1;
        stats.byPriority[pri] = (stats.byPriority[pri] || 0) + 1;

        totalConfidence += email.classification.confidence;
        confidenceCount++;

        if (email.classification.confidence < 0.6) {
          stats.needsReview++;
        }
      }
    });

    stats.avgConfidence = confidenceCount > 0 ? totalConfidence / confidenceCount : 0;

    return stats;
  }
}
