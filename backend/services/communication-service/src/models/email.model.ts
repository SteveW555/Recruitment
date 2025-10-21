/**
 * Email Categorization Models
 * ProActive People - Recruitment Automation System
 */

export enum EmailCategory {
  CANDIDATE = 'candidate',
  CLIENT = 'client',
  SUPPLIER = 'supplier',
  STAFF = 'staff',
  OTHER = 'other'
}

export enum EmailSubCategory {
  // Candidate subcategories
  APPLICATION = 'application',
  CV_SUBMISSION = 'cv_submission',
  INTERVIEW_RESPONSE = 'interview_response',
  AVAILABILITY_UPDATE = 'availability_update',
  REFERENCE_CHECK = 'reference_check',

  // Client subcategories
  JOB_BRIEF = 'job_brief',
  FEEDBACK = 'feedback',
  INTERVIEW_REQUEST = 'interview_request',
  PLACEMENT_UPDATE = 'placement_update',
  CONTRACT_QUERY = 'contract_query',

  // Supplier subcategories
  INVOICE = 'invoice',
  SERVICE_UPDATE = 'service_update',
  INTEGRATION_ISSUE = 'integration_issue',

  // Staff subcategories
  INTERNAL_COMMUNICATION = 'internal_communication',
  TEAM_UPDATE = 'team_update',
  HR_MATTER = 'hr_matter',

  // Other subcategories
  SPAM = 'spam',
  MARKETING = 'marketing',
  SYSTEM_NOTIFICATION = 'system_notification',
  UNCLASSIFIED = 'unclassified'
}

export enum EmailPriority {
  URGENT = 'urgent',
  HIGH = 'high',
  NORMAL = 'normal',
  LOW = 'low'
}

export enum EmailSentiment {
  POSITIVE = 'positive',
  NEUTRAL = 'neutral',
  NEGATIVE = 'negative',
  MIXED = 'mixed'
}

export interface EmailAddress {
  email: string;
  name?: string;
}

export interface EmailAttachment {
  filename: string;
  contentType: string;
  size: number;
  storageUrl?: string;
  isCV?: boolean;
}

export interface EmailClassification {
  category: EmailCategory;
  subCategory?: EmailSubCategory;
  confidence: number; // 0-1 score from AI
  priority: EmailPriority;
  sentiment: EmailSentiment;
  keywords: string[];
  entities: {
    candidates?: string[]; // Candidate IDs
    clients?: string[]; // Client IDs
    jobs?: string[]; // Job IDs
  };
  requiresAction: boolean;
  suggestedActions?: string[];
  classifiedAt: Date;
  classifiedBy: 'ai' | 'manual' | 'rule-based';
}

export interface Email {
  id: string;
  messageId: string; // Unique message ID from email provider
  threadId?: string; // Conversation thread ID

  // Sender/Recipients
  from: EmailAddress;
  to: EmailAddress[];
  cc?: EmailAddress[];
  bcc?: EmailAddress[];
  replyTo?: EmailAddress;

  // Content
  subject: string;
  bodyText: string;
  bodyHtml?: string;
  attachments?: EmailAttachment[];

  // Classification
  classification?: EmailClassification;

  // Metadata
  receivedAt: Date;
  sentAt?: Date;
  direction: 'inbound' | 'outbound';
  source: 'sendgrid' | 'ses' | 'smtp' | 'manual';

  // Processing
  processed: boolean;
  processedAt?: Date;
  routed: boolean;
  routedTo?: string[]; // Service/user IDs
  archived: boolean;

  // Relationships
  candidateId?: string;
  clientId?: string;
  jobId?: string;
  placementId?: string;

  // Audit
  createdAt: Date;
  updatedAt: Date;
}

export interface EmailTemplate {
  id: string;
  name: string;
  category: EmailCategory;
  subCategory?: EmailSubCategory;
  subject: string;
  bodyHtml: string;
  bodyText: string;
  variables: string[]; // e.g., ['candidateName', 'jobTitle']
  active: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface EmailRule {
  id: string;
  name: string;
  description?: string;
  priority: number;
  active: boolean;

  // Conditions
  conditions: {
    fromDomain?: string[];
    fromEmail?: string[];
    toDomain?: string[];
    subjectContains?: string[];
    bodyContains?: string[];
    hasAttachment?: boolean;
    attachmentType?: string[];
  };

  // Actions
  actions: {
    setCategory?: EmailCategory;
    setSubCategory?: EmailSubCategory;
    setPriority?: EmailPriority;
    routeTo?: string[];
    autoRespond?: boolean;
    responseTemplateId?: string;
    flag?: boolean;
  };

  createdAt: Date;
  updatedAt: Date;
}

export interface EmailCategoryStats {
  category: EmailCategory;
  count: number;
  percentage: number;
  avgResponseTime?: number; // in minutes
  avgConfidence?: number;
}

export interface ClassificationRequest {
  emailId: string;
  forceReclassify?: boolean;
}

export interface ClassificationResponse {
  emailId: string;
  classification: EmailClassification;
  processingTimeMs: number;
}

export interface BulkClassificationRequest {
  emailIds: string[];
  forceReclassify?: boolean;
}

export interface BulkClassificationResponse {
  total: number;
  successful: number;
  failed: number;
  results: ClassificationResponse[];
  errors?: Array<{
    emailId: string;
    error: string;
  }>;
}
