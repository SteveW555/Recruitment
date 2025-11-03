# Data Model: Gmail Email Search & CV Extraction

**Feature**: 004-gmail-email-search
**Created**: 2025-11-03
**Status**: Phase 1

## Overview

This document defines the data models, relationships, and validation rules for the Gmail Email Search feature based on the specification entities and research findings.

## Entity Relationship Diagram

```
┌─────────────┐       ┌──────────────┐       ┌─────────────────┐
│   User      │──────<│ UserToken    │       │  EmailMessage   │
│             │       │              │       │                 │
└─────────────┘       └──────────────┘       └─────────────────┘
       │                                             │
       │                                             │
       │              ┌──────────────────┐           │
       └─────────────<│  SearchQuery     │           │
       │              │                  │           │
       │              └──────────────────┘           │
       │                                             │
       │              ┌──────────────────┐           │
       └─────────────<│  DownloadedFile  │───────────┘
                      │                  │
                      └──────────────────┘
                               │
                               │
                      ┌──────────────────┐
                      │   AuditLog       │
                      │                  │
                      └──────────────────┘
```

## Core Entities

### 1. User

**Purpose**: Represents a recruiter who connects their Gmail account

**Prisma Schema**:
```prisma
model User {
  id            String   @id @default(uuid())
  email         String   @unique
  name          String?
  gmailAddress  String   @unique
  createdAt     DateTime @default(now())
  updatedAt     DateTime @updatedAt
  lastLoginAt   DateTime?

  // Relationships
  tokens        UserToken[]
  searches      SearchQuery[]
  downloads     DownloadedFile[]
  auditLogs     AuditLog[]

  @@map("users")
}
```

**Validation Rules**:
- `email`: Valid email format, unique across system
- `gmailAddress`: Must be a valid Gmail address (@gmail.com), unique
- `name`: Optional, max 200 characters
- `lastLoginAt`: Updated on each OAuth login

**Business Rules**:
- Each user can only connect one Gmail account
- Users can re-connect by revoking and re-authorizing

---

### 2. UserToken

**Purpose**: Stores encrypted OAuth 2.0 tokens for Gmail API access

**Prisma Schema**:
```prisma
model UserToken {
  id            String   @id @default(uuid())
  userId        String
  accessToken   String   @db.Text // Encrypted with AES-256-GCM
  refreshToken  String   @db.Text // Encrypted with AES-256-GCM
  tokenExpiry   DateTime
  scopes        String[] // Array of granted OAuth scopes
  createdAt     DateTime @default(now())
  updatedAt     DateTime @updatedAt

  // Relationships
  user          User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([userId])
  @@index([tokenExpiry])
  @@map("user_tokens")
}
```

**Validation Rules**:
- `accessToken`: Required, encrypted before storage
- `refreshToken`: Required, encrypted before storage
- `tokenExpiry`: Must be in the future when created
- `scopes`: Must include 'gmail.readonly' at minimum

**Business Rules**:
- Tokens are encrypted at rest using AES-256-GCM
- Tokens are automatically refreshed 5 minutes before expiry
- Failed refresh triggers re-authentication flow
- Tokens are deleted on user account deletion (cascade)

**Security**:
```typescript
// Encryption format stored in DB
interface EncryptedToken {
  iv: string;        // Initialization vector (hex)
  encrypted: string; // Encrypted data (hex)
  authTag: string;   // GCM authentication tag (hex)
}
```

---

### 3. EmailMessage (Read-Only, Not Persisted)

**Purpose**: Represents an email from Gmail API (transient, not stored in database)

**TypeScript Interface**:
```typescript
interface EmailMessage {
  id: string;                    // Gmail message ID
  threadId: string;              // Gmail thread ID
  sender: EmailAddress;
  recipients: EmailAddress[];
  subject: string;
  snippet: string;               // First 200 chars of body
  body: {
    plain?: string;
    html?: string;
  };
  date: Date;                    // Received/sent date
  hasAttachments: boolean;
  attachments: Attachment[];
  labels: string[];              // Gmail labels
}

interface EmailAddress {
  name?: string;
  email: string;
}
```

**Validation Rules**:
- `id`: Required, Gmail message ID format
- `sender.email`: Valid email format
- `subject`: Max 998 characters (RFC 2822)
- `snippet`: Max 200 characters
- `date`: Valid ISO 8601 date

**Business Rules**:
- Email messages are never stored in database (privacy/GDPR)
- Fetched on-demand from Gmail API
- Cached in Redis for 5 minutes per search query
- All PDF/DOC/DOCX attachments flagged as potential CVs

---

### 4. Attachment (Read-Only, Not Persisted Initially)

**Purpose**: Represents an email attachment (CV file)

**TypeScript Interface**:
```typescript
interface Attachment {
  id: string;           // Gmail attachment ID
  messageId: string;    // Parent message ID
  filename: string;
  mimeType: string;     // e.g., 'application/pdf'
  size: number;         // Bytes
  downloadUrl?: string; // Temporary download URL (after download)
}
```

**Validation Rules**:
- `filename`: Max 255 characters, no path traversal characters
- `mimeType`: Must be one of: 'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
- `size`: Max 25MB, warn if exceeds

**Business Rules**:
- Only PDF/DOC/DOCX files are treated as CVs (per spec)
- Files are downloaded to temporary storage on user request
- MIME type validation on download (fallback to file-type detection)
- Unicode filenames supported

---

### 5. DownloadedFile

**Purpose**: Tracks downloaded CV files for cleanup and audit

**Prisma Schema**:
```prisma
model DownloadedFile {
  id            String   @id @default(uuid())
  userId        String
  messageId     String   // Gmail message ID
  attachmentId  String   // Gmail attachment ID
  filename      String
  mimeType      String
  fileSize      BigInt
  filePath      String   // File system path
  downloadedAt  DateTime @default(now())
  scheduledCleanupAt DateTime // downloadedAt + 24 hours
  deletedAt     DateTime?

  // Relationships
  user          User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([userId, downloadedAt])
  @@index([scheduledCleanupAt])
  @@map("downloaded_files")
}
```

**Validation Rules**:
- `filename`: Max 255 characters, sanitized
- `mimeType`: Valid MIME type
- `fileSize`: Positive integer
- `filePath`: Absolute file system path
- `scheduledCleanupAt`: Must be exactly 24 hours after `downloadedAt`

**Business Rules**:
- Files are scheduled for deletion 24 hours after download (GDPR requirement)
- Bull queue job scheduled at `scheduledCleanupAt`
- Files are deleted from file system and record marked `deletedAt`
- Failsafe cron job cleans orphaned files older than 25 hours
- Record retained for audit trail even after file deletion

**File Path Structure**:
```
/tmp/gmail-attachments/{userId}/{messageId}/{attachmentId}/{sanitized-filename}
```

---

### 6. SearchQuery (Audit Only, Optional)

**Purpose**: Logs search queries for analytics and debugging

**Prisma Schema**:
```prisma
model SearchQuery {
  id            String   @id @default(uuid())
  userId        String
  startDate     DateTime
  endDate       DateTime
  senderFilter  String?
  subjectFilter String?
  bodyFilter    String?
  resultCount   Int
  executionTime Int      // Milliseconds
  createdAt     DateTime @default(now())

  // Relationships
  user          User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([userId, createdAt])
  @@map("search_queries")
}
```

**Validation Rules**:
- `startDate`: Must be before `endDate`
- `endDate`: Cannot be in the future
- `senderFilter`: Valid email format or domain
- `subjectFilter`: Max 200 characters
- `bodyFilter`: Max 500 characters
- `resultCount`: Non-negative integer

**Business Rules**:
- Logged after successful search completion
- Used for analytics (popular search patterns, performance)
- Helps identify slow queries for optimization
- Retained for 90 days then archived

---

### 7. AuditLog

**Purpose**: Comprehensive audit trail for security and compliance

**Prisma Schema**:
```prisma
model AuditLog {
  id            String   @id @default(uuid())
  userId        String?  // Nullable for system events
  action        String   // Enum: oauth_login, search_emails, download_attachment, etc.
  resourceType  String?  // gmail_message, attachment, etc.
  resourceId    String?  // Gmail message ID or attachment ID
  metadata      Json?    // Additional context
  ipAddress     String
  userAgent     String
  createdAt     DateTime @default(now())

  // Relationships
  user          User?    @relation(fields: [userId], references: [id], onDelete: SetNull)

  @@index([userId, createdAt])
  @@index([action, createdAt])
  @@map("audit_logs")
}
```

**Validation Rules**:
- `action`: Must be one of predefined enum values
- `ipAddress`: Valid IPv4 or IPv6 format
- `userAgent`: Max 500 characters
- `metadata`: Valid JSON

**Action Enum Values**:
```typescript
enum AuditAction {
  // Authentication
  OAUTH_INITIATED = 'oauth_initiated',
  OAUTH_COMPLETED = 'oauth_completed',
  OAUTH_FAILED = 'oauth_failed',
  OAUTH_REVOKED = 'oauth_revoked',
  TOKEN_REFRESHED = 'token_refreshed',

  // Search
  SEARCH_EMAILS = 'search_emails',
  VIEW_EMAIL = 'view_email',

  // Attachments
  VIEW_ATTACHMENT = 'view_attachment',
  DOWNLOAD_ATTACHMENT = 'download_attachment',
  BULK_DOWNLOAD = 'bulk_download',

  // File Management
  FILE_DELETED = 'file_deleted',
  FILE_CLEANUP_FAILED = 'file_cleanup_failed',

  // Admin
  USER_CREATED = 'user_created',
  USER_DELETED = 'user_deleted'
}
```

**Business Rules**:
- All security-relevant actions are logged
- Logs are immutable (no updates/deletes)
- Logs are retained for 7 years (compliance requirement)
- Sensitive data is never logged (tokens, file contents)
- Personal data in logs follows GDPR right-to-erasure

---

## Data Validation Summary

### Date Range Validation
```typescript
function validateDateRange(startDate: Date, endDate: Date): void {
  if (startDate >= endDate) {
    throw new ValidationError('Start date must be before end date');
  }

  const maxRange = 365; // days
  const daysDiff = (endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24);
  if (daysDiff > maxRange) {
    throw new ValidationError(`Date range cannot exceed ${maxRange} days`);
  }

  if (endDate > new Date()) {
    throw new ValidationError('End date cannot be in the future');
  }
}
```

### Email Validation
```typescript
function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

function validateGmailAddress(email: string): boolean {
  return email.endsWith('@gmail.com') && validateEmail(email);
}
```

### File Validation
```typescript
const SUPPORTED_MIME_TYPES = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
];

const MAX_FILE_SIZE = 25 * 1024 * 1024; // 25MB
const WARN_FILE_SIZE = 25 * 1024 * 1024; // 25MB

function validateAttachment(attachment: Attachment): ValidationResult {
  if (!SUPPORTED_MIME_TYPES.includes(attachment.mimeType)) {
    return {
      valid: false,
      error: `Unsupported file type: ${attachment.mimeType}`
    };
  }

  if (attachment.size > MAX_FILE_SIZE) {
    return {
      valid: true,
      warning: `File size (${formatBytes(attachment.size)}) exceeds recommended limit of 25MB`
    };
  }

  return { valid: true };
}
```

### Filename Sanitization
```typescript
function sanitizeFilename(filename: string): string {
  return filename
    .replace(/[<>:"/\\|?*\x00-\x1F]/g, '_')  // Remove invalid chars
    .replace(/^\.+/, '')                      // Remove leading dots
    .replace(/\s+/g, '_')                     // Replace spaces
    .substring(0, 255);                       // Limit length
}
```

---

## Database Indexes

**Critical Indexes** (for performance):
```prisma
// User lookups
@@index([email])
@@index([gmailAddress])

// Token management
@@index([userId])
@@index([tokenExpiry])

// File cleanup
@@index([scheduledCleanupAt])
@@index([userId, downloadedAt])

// Audit trail
@@index([userId, createdAt])
@@index([action, createdAt])

// Search history
@@index([userId, createdAt])
```

---

## State Transitions

### User Token Lifecycle
```
[Not Connected] → [OAuth Flow] → [Token Active]
                       ↓              ↓
                   [Failed]      [Refresh]
                                     ↓
                                [Updated]
                                     ↓
                                [Revoked]
```

### Downloaded File Lifecycle
```
[Not Downloaded] → [Download Request] → [Downloaded]
                                            ↓
                                    [24h Timer Started]
                                            ↓
                                    [Cleanup Job Queued]
                                            ↓
                                    [File Deleted]
                                            ↓
                                    [Record Marked Deleted]
```

---

## Redis Cache Schema

**Session Store**:
```typescript
// Key format: session:{sessionId}
interface SessionData {
  userId: string;
  gmailAddress: string;
  name: string;
  lastActivity: number;  // Unix timestamp
}
// TTL: Until browser close (managed by connect-redis)
```

**Token Cache**:
```typescript
// Key format: token:{userId}
interface CachedToken {
  accessToken: string;  // Encrypted
  expiry: number;       // Unix timestamp
}
// TTL: token_expiry - now - 5min
```

**Search Results Cache**:
```typescript
// Key format: search:{userId}:{queryHash}
interface CachedSearchResults {
  emails: EmailMessage[];
  totalCount: number;
  nextPageToken?: string;
}
// TTL: 300 seconds (5 minutes)
```

**Rate Limiting**:
```typescript
// Key format: ratelimit:gmail:{userId}
// Value: consumed quota units
// TTL: 1 second

// Key format: ratelimit:search:{userId}
// Value: search count
// TTL: 60 seconds
```

---

## Migration Strategy

### Initial Schema Creation
```bash
# Generate Prisma migration
npx prisma migrate dev --name init

# Apply to database
npx prisma migrate deploy

# Generate Prisma Client
npx prisma generate
```

### Future Schema Changes
```bash
# Create new migration
npx prisma migrate dev --name add_field_name

# Review migration SQL
# Apply to staging, then production
```

### Data Seeding (Development Only)
```typescript
// prisma/seed.ts
async function seed() {
  // Create test user
  await prisma.user.create({
    data: {
      email: 'test@example.com',
      name: 'Test Recruiter',
      gmailAddress: 'test@gmail.com'
    }
  });
}
```

---

## Phase 1 Status

✅ **Data models defined** with Prisma schemas
✅ **Validation rules** documented
✅ **Relationships** mapped
✅ **Indexes** identified for performance
✅ **State transitions** documented
✅ **Cache schemas** defined

**Next**: Create API contracts (OpenAPI specification)
