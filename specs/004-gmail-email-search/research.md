# Research: Gmail Email Search & CV Extraction

**Feature**: 004-gmail-email-search
**Created**: 2025-11-03
**Status**: Phase 0 Complete

## Overview

This document captures research findings, technology decisions, and best practices for implementing Gmail email search with CV extraction functionality.

## Research Areas

### 1. Gmail API Integration

**Decision**: Use googleapis npm package (official Google client) with Gmail API v1

**Rationale**:
- Official Google-maintained library with TypeScript support
- Comprehensive API coverage including messages.list, messages.get, attachments.get
- Built-in rate limiting and retry logic
- Strong community support and documentation
- OAuth 2.0 integration out of the box

**Alternatives Considered**:
- **IMAP Protocol**: Rejected because IMAP requires less secure app access (deprecated by Google), lacks attachment metadata, and has poor performance for large mailboxes
- **Third-party libraries** (node-gmail-api): Rejected due to lack of maintenance and TypeScript support

**Best Practices**:
- Use batch requests for fetching multiple emails (users.messages.batchGet)
- Implement incremental pagination with pageToken to handle large result sets
- Use `q` parameter for server-side filtering (Gmail search syntax)
- Request only needed fields using `fields` parameter to reduce payload size
- Enable gzip compression for API responses

**Key API Endpoints**:
```typescript
// List messages with query
gmail.users.messages.list({
  userId: 'me',
  q: 'after:2025/01/01 before:2025/01/31 has:attachment',
  maxResults: 50,
  pageToken: nextPageToken
})

// Get message details
gmail.users.messages.get({
  userId: 'me',
  id: messageId,
  format: 'full' // includes headers and body
})

// Get attachment
gmail.users.messages.attachments.get({
  userId: 'me',
  messageId: messageId,
  id: attachmentId
})
```

**Rate Limiting**:
- Gmail API: 250 quota units per user per second
- messages.list: 5 units, messages.get: 5 units, attachments.get: 5 units
- Implement exponential backoff with jitter for 429 errors
- Use Redis to track per-user quotas and queue requests

---

### 2. OAuth 2.0 Authentication Flow

**Decision**: Use passport-google-oauth20 with Google Identity Platform

**Rationale**:
- Industry-standard OAuth 2.0 implementation
- Seamless integration with NestJS via @nestjs/passport
- Handles token refresh automatically
- Supports offline access (refresh tokens)
- Compliant with Google OAuth policies (individual user consent)

**Alternatives Considered**:
- **Service Account**: Rejected - requires domain-wide delegation which doesn't fit individual recruiter authentication model
- **API Keys**: Rejected - not suitable for user-specific Gmail access
- **Custom OAuth implementation**: Rejected - reinventing the wheel, higher security risk

**OAuth Scopes Required**:
```typescript
const scopes = [
  'https://www.googleapis.com/auth/gmail.readonly',    // Read email messages
  'https://www.googleapis.com/auth/gmail.modify',      // Modify messages (for labels if needed)
  'https://www.googleapis.com/auth/userinfo.email',    // User email address
  'https://www.googleapis.com/auth/userinfo.profile'   // User profile info
];
```

**Token Storage Strategy**:
```typescript
// PostgreSQL schema for tokens
table user_tokens {
  id: uuid
  user_id: uuid
  access_token: text (encrypted)     // AES-256-GCM encryption
  refresh_token: text (encrypted)    // AES-256-GCM encryption
  token_expiry: timestamp
  scopes: text[]
  created_at: timestamp
  updated_at: timestamp
}

// Redis cache for active sessions
redis_key: `session:${userId}:token`
ttl: token_expiry - now - 5minutes  // Refresh 5min before expiry
```

**Token Refresh Logic**:
- Check expiry before each Gmail API call
- Refresh if expiring within 5 minutes
- Use Redis lock to prevent concurrent refresh requests
- Update both PostgreSQL and Redis on successful refresh
- Handle refresh failures gracefully (re-authentication flow)

**Best Practices**:
- Never log tokens (use masking in logs: `token: ***abc123`)
- Use HTTPS-only for OAuth callbacks
- Implement CSRF protection with state parameter
- Set appropriate callback URL whitelist in Google Console
- Implement session timeout on browser close (no server-side timeout per spec)

---

### 3. File Handling & Cleanup

**Decision**: Temporary file system storage with Bull queue for 24-hour cleanup

**Rationale**:
- Simple file system is sufficient for temporary storage
- Bull provides reliable job scheduling for cleanup
- No need for complex object storage (S3) for short-lived files
- Easy to implement file size checks and MIME validation
- Supports atomic file writes and cleanup

**Alternatives Considered**:
- **S3/Cloud Storage**: Rejected - overkill for 24-hour retention, adds latency and cost
- **Database BLOB storage**: Rejected - poor performance for large files, bloats database
- **In-memory storage**: Rejected - limited capacity, lost on restart

**Storage Strategy**:
```typescript
// File storage path
const filePath = `/tmp/gmail-attachments/${userId}/${messageId}/${attachmentId}/${filename}`;

// Metadata storage in PostgreSQL
table downloaded_files {
  id: uuid
  user_id: uuid
  message_id: string
  attachment_id: string
  filename: string
  mime_type: string
  file_size: bigint
  file_path: string
  downloaded_at: timestamp
  cleanup_scheduled_at: timestamp
  indexes: (user_id, downloaded_at), (cleanup_scheduled_at)
}
```

**Cleanup Job (Bull Queue)**:
```typescript
// Schedule cleanup job immediately after download
await cleanupQueue.add('delete-file', {
  fileId: downloadedFile.id,
  filePath: downloadedFile.file_path
}, {
  delay: 24 * 60 * 60 * 1000, // 24 hours
  attempts: 3,
  backoff: { type: 'exponential', delay: 60000 }
});

// Cleanup processor
cleanupQueue.process('delete-file', async (job) => {
  const { fileId, filePath } = job.data;

  // Delete file
  await fs.promises.unlink(filePath);

  // Update database
  await prisma.downloadedFile.update({
    where: { id: fileId },
    data: { deleted_at: new Date() }
  });
});

// Failsafe: Cron job to clean up any orphaned files older than 25 hours
@Cron('0 * * * *') // Every hour
async cleanupOrphanedFiles() {
  const cutoff = new Date(Date.now() - 25 * 60 * 60 * 1000);
  const orphaned = await prisma.downloadedFile.findMany({
    where: {
      downloaded_at: { lt: cutoff },
      deleted_at: null
    }
  });

  for (const file of orphaned) {
    try {
      await fs.promises.unlink(file.file_path);
      await prisma.downloadedFile.update({
        where: { id: file.id },
        data: { deleted_at: new Date() }
      });
    } catch (error) {
      logger.warn(`Failed to cleanup orphaned file: ${file.id}`, error);
    }
  }
}
```

**File Size Handling**:
- Check `Content-Length` header before download
- Warn user for files > 25MB (per spec)
- Allow download after user acknowledgment
- Stream large files to avoid memory issues
- Implement download progress tracking

**MIME Type Detection**:
```typescript
// Primary: Gmail API provides mimeType
const mimeType = attachment.mimeType;

// Fallback: Use file extension and file-type library
import { fileTypeFromBuffer } from 'file-type';

const detectedType = await fileTypeFromBuffer(buffer);
const supportedTypes = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
];

if (!supportedTypes.includes(mimeType)) {
  throw new UnsupportedFileTypeError(`File type ${mimeType} not supported`);
}
```

**Best Practices**:
- Use atomic writes (write to .tmp then rename)
- Implement file download retries with exponential backoff
- Log all file operations for audit trail
- Use streaming for files > 10MB
- Implement virus scanning (ClamAV) before serving files to users

---

### 4. Rate Limiting & Performance

**Decision**: Multi-layer rate limiting with Redis-backed token bucket

**Rationale**:
- Gmail API has strict per-user quotas (250 units/second)
- Need to prevent quota exhaustion from concurrent operations
- Redis provides fast distributed rate limiting
- Token bucket algorithm allows burst capacity

**Rate Limiting Strategy**:
```typescript
// Rate limiter configuration
const rateLimitConfig = {
  // Per-user Gmail API quota
  gmailApi: {
    points: 250,           // 250 quota units
    duration: 1,           // per second
    blockDuration: 60      // Block for 60s if exceeded
  },

  // Per-user search requests
  searchRequests: {
    points: 10,            // 10 searches
    duration: 60,          // per minute
    blockDuration: 300     // Block for 5min if exceeded
  },

  // Global attachment downloads
  attachmentDownloads: {
    points: 100,           // 100 concurrent downloads
    duration: 60,          // per minute
    blockDuration: 0       // Queue instead of block
  }
};

// Implementation with rate-limiter-flexible
import { RateLimiterRedis } from 'rate-limiter-flexible';

const gmailRateLimiter = new RateLimiterRedis({
  storeClient: redisClient,
  keyPrefix: 'ratelimit:gmail',
  points: 250,
  duration: 1,
  blockDuration: 60
});

// Before each Gmail API call
async makeGmailApiCall(userId: string, quotaUnits: number) {
  try {
    await gmailRateLimiter.consume(userId, quotaUnits);
    // Proceed with API call
  } catch (error) {
    if (error instanceof RateLimiterRes) {
      throw new TooManyRequestsException(
        `Rate limit exceeded. Retry after ${error.msBeforeNext}ms`
      );
    }
    throw error;
  }
}
```

**Performance Optimization**:
```typescript
// 1. Batch Gmail API requests
const messages = await gmail.users.messages.batchGet({
  userId: 'me',
  ids: messageIds  // Up to 1000 messages per batch
});

// 2. Parallel attachment downloads with concurrency limit
const pLimit = require('p-limit');
const limit = pLimit(5);  // Max 5 concurrent downloads

const downloads = attachments.map(att =>
  limit(() => downloadAttachment(att))
);
await Promise.all(downloads);

// 3. Redis caching for search results
const cacheKey = `search:${userId}:${hashQuery(query)}`;
const cached = await redis.get(cacheKey);
if (cached) return JSON.parse(cached);

const results = await performSearch(query);
await redis.setex(cacheKey, 300, JSON.stringify(results));  // 5min TTL

// 4. Database query optimization
// Use proper indexes
@@index([user_id, downloaded_at])
@@index([cleanup_scheduled_at])

// Use connection pooling
const prisma = new PrismaClient({
  datasources: {
    db: {
      url: process.env.DATABASE_URL,
      connectionLimit: 20
    }
  }
});

// 5. Frontend pagination
// Use cursor-based pagination instead of offset
interface PaginationParams {
  cursor?: string;  // Last message ID
  limit: number;    // Default 50
}
```

**Monitoring**:
- Track API quota usage per user (Redis counters)
- Alert when user reaches 80% of quota
- Log slow queries (>1s)
- Monitor Bull queue depth for cleanup jobs
- Track file storage disk usage

---

### 5. Security & Encryption

**Decision**: Multi-layer security with encryption at rest and in transit

**Rationale**:
- GDPR compliance requires encryption of personal data
- OAuth tokens are sensitive credentials
- Audit trail needed for compliance
- Defense in depth approach

**Encryption Strategy**:
```typescript
// 1. Token encryption (AES-256-GCM)
import crypto from 'crypto';

const ENCRYPTION_KEY = process.env.ENCRYPTION_KEY;  // 32 bytes
const IV_LENGTH = 16;

function encryptToken(token: string): string {
  const iv = crypto.randomBytes(IV_LENGTH);
  const cipher = crypto.createCipheriv('aes-256-gcm', ENCRYPTION_KEY, iv);

  let encrypted = cipher.update(token, 'utf8', 'hex');
  encrypted += cipher.final('hex');

  const authTag = cipher.getAuthTag();

  return JSON.stringify({
    iv: iv.toString('hex'),
    encrypted,
    authTag: authTag.toString('hex')
  });
}

function decryptToken(encryptedData: string): string {
  const { iv, encrypted, authTag } = JSON.parse(encryptedData);

  const decipher = crypto.createDecipheriv(
    'aes-256-gcm',
    ENCRYPTION_KEY,
    Buffer.from(iv, 'hex')
  );

  decipher.setAuthTag(Buffer.from(authTag, 'hex'));

  let decrypted = decipher.update(encrypted, 'hex', 'utf8');
  decrypted += decipher.final('utf8');

  return decrypted;
}

// 2. Password hashing for admin users (if needed)
import bcrypt from 'bcrypt';

const SALT_ROUNDS = 12;

async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, SALT_ROUNDS);
}

// 3. Secure session management
import session from 'express-session';
import RedisStore from 'connect-redis';

app.use(session({
  store: new RedisStore({ client: redisClient }),
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: true,      // HTTPS only
    httpOnly: true,    // No JavaScript access
    sameSite: 'lax',   // CSRF protection
    maxAge: null       // Session cookie (browser close)
  }
}));
```

**Audit Logging**:
```typescript
// Audit log schema
table audit_logs {
  id: uuid
  user_id: uuid
  action: string  // 'oauth_login', 'search_emails', 'download_attachment', etc.
  resource_type: string  // 'gmail_message', 'attachment', etc.
  resource_id: string
  metadata: jsonb
  ip_address: string
  user_agent: string
  created_at: timestamp
  indexes: (user_id, created_at), (action, created_at)
}

// Log all security-relevant actions
async logAuditEvent(event: AuditEvent) {
  await prisma.auditLog.create({
    data: {
      user_id: event.userId,
      action: event.action,
      resource_type: event.resourceType,
      resource_id: event.resourceId,
      metadata: event.metadata,
      ip_address: event.ipAddress,
      user_agent: event.userAgent
    }
  });

  // Also send to centralized logging (e.g., ELK stack)
  logger.info('Audit event', {
    event_type: 'audit',
    ...event
  });
}
```

**Input Validation**:
```typescript
// Use class-validator for DTO validation
import { IsDateString, IsEmail, IsOptional, MaxLength } from 'class-validator';

export class SearchEmailsDto {
  @IsDateString()
  startDate: string;

  @IsDateString()
  endDate: string;

  @IsOptional()
  @IsEmail()
  senderFilter?: string;

  @IsOptional()
  @MaxLength(200)
  subjectFilter?: string;

  @IsOptional()
  @MaxLength(500)
  bodyFilter?: string;
}

// Sanitize user inputs to prevent XSS
import DOMPurify from 'isomorphic-dompurify';

function sanitizeInput(input: string): string {
  return DOMPurify.sanitize(input, { ALLOWED_TAGS: [] });
}
```

**Security Headers**:
```typescript
import helmet from 'helmet';

app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'unsafe-inline'"],  // For React
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", 'data:', 'https:'],
      connectSrc: ["'self'", 'https://www.googleapis.com'],
    }
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  }
}));
```

**Best Practices**:
- Rotate encryption keys annually
- Use separate keys for different environments (dev/staging/prod)
- Store keys in secure vault (AWS Secrets Manager, Azure Key Vault)
- Implement key versioning for zero-downtime rotation
- Use HTTPS/TLS 1.3 for all communications
- Enable CORS with strict origin whitelist
- Implement rate limiting on authentication endpoints
- Use security scanning tools (npm audit, Snyk)

---

## Decisions Summary

| Area | Decision | Key Rationale |
|------|----------|--------------|
| **Gmail API** | googleapis npm package | Official library, TypeScript support, built-in OAuth |
| **OAuth** | passport-google-oauth20 | Industry standard, NestJS integration, auto refresh |
| **Storage** | File system + Bull queue | Simple, reliable, appropriate for 24h retention |
| **Rate Limiting** | Redis token bucket | Distributed, fast, supports Gmail API quotas |
| **Encryption** | AES-256-GCM | GDPR compliant, strong encryption, auth tags |
| **Database** | PostgreSQL + Prisma | Existing stack, TypeScript ORM, migrations |
| **Caching** | Redis | Fast, session store, rate limiting, result cache |
| **Testing** | Jest + Supertest + Playwright | Full coverage, existing stack, E2E support |

---

## Risk Analysis

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Gmail API quota exhaustion | Medium | High | Implement strict rate limiting, user quotas, queue system |
| Large file downloads timeout | Low | Medium | Streaming downloads, progress tracking, retry logic |
| OAuth token refresh failures | Low | High | Graceful fallback, re-auth flow, user notification |
| File cleanup job failures | Low | Medium | Failsafe cron job, monitoring, alerts |
| Concurrent download spikes | Medium | Medium | Connection pooling, download queue, limits |

---

## Next Steps

1. ✅ **Phase 0 Complete**: Research and technology decisions documented
2. ⏭️ **Phase 1**: Create data models, API contracts, and quickstart guide
3. ⏭️ **Phase 2**: Generate actionable tasks from implementation plan

---

**Phase 0 Status**: ✅ COMPLETE - All technical unknowns resolved, ready for design phase
