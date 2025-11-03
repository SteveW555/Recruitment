# Quickstart Guide: Gmail Email Search & CV Extraction

**Feature**: 004-gmail-email-search
**Last Updated**: 2025-11-03
**Target Audience**: Developers implementing this feature

## Overview

This guide provides a rapid setup path for implementing the Gmail Email Search feature. Follow these steps to get a working prototype running locally within 2-3 hours.

## Prerequisites

- Node.js 20 LTS
- Docker & Docker Compose
- Google Cloud Platform account
- PostgreSQL 15+ and Redis 7+ (or use Docker Compose)
- Basic familiarity with NestJS and Next.js

## Quick Setup (30 minutes)

### 1. Google Cloud Configuration (10 min)

```bash
# 1. Create Google Cloud Project
# Go to: https://console.cloud.google.com/
# Create new project: "gmail-cv-extractor-dev"

# 2. Enable Gmail API
# Go to: https://console.cloud.google.com/apis/library/gmail.googleapis.com
# Click "Enable"

# 3. Configure OAuth Consent Screen
# Go to: https://console.cloud.google.com/apis/credentials/consent
# - User Type: External
# - App name: "Gmail CV Extractor (Dev)"
# - Support email: your-email@example.com
# - Scopes: gmail.readonly, userinfo.email, userinfo.profile
# - Test users: Add your Gmail address

# 4. Create OAuth 2.0 Credentials
# Go to: https://console.cloud.google.com/apis/credentials
# Create credentials > OAuth client ID
# - Application type: Web application
# - Name: "Gmail CV Extractor Web Client"
# - Authorized redirect URIs:
#   http://localhost:8080/api/v1/auth/google/callback
# - Copy Client ID and Client Secret
```

### 2. Backend Setup (10 min)

```bash
# Clone or navigate to project
cd d:/Recruitment

# Create gmail-service directory
mkdir -p backend/services/gmail-service
cd backend/services/gmail-service

# Initialize NestJS project
npx @nestjs/cli new . --skip-git --package-manager npm

# Install dependencies
npm install --save \
  @nestjs/passport passport passport-google-oauth20 \
  @nestjs/jwt @nestjs/config \
  @prisma/client googleapis \
  bull @nestjs/bull \
  redis ioredis \
  bcrypt class-validator class-transformer \
  helmet

npm install --save-dev \
  @types/passport-google-oauth20 \
  @types/bcrypt \
  prisma \
  @nestjs/testing \
  supertest

# Initialize Prisma
npx prisma init

# Create environment file
cat > .env << 'EOF'
# Database
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/gmail_service_dev"

# Redis
REDIS_HOST="localhost"
REDIS_PORT=6379

# Google OAuth
GOOGLE_CLIENT_ID="your-client-id-here"
GOOGLE_CLIENT_SECRET="your-client-secret-here"
GOOGLE_CALLBACK_URL="http://localhost:8080/api/v1/auth/google/callback"

# Encryption
ENCRYPTION_KEY="generate-32-byte-key-here"  # openssl rand -hex 32
SESSION_SECRET="generate-session-secret"     # openssl rand -hex 32

# Application
NODE_ENV=development
PORT=8080
FRONTEND_URL="http://localhost:3000"

# File Storage
TEMP_STORAGE_PATH="/tmp/gmail-attachments"
MAX_FILE_SIZE_MB=25
EOF

# Generate encryption keys
echo "ENCRYPTION_KEY=$(openssl rand -hex 32)" >> .env
echo "SESSION_SECRET=$(openssl rand -hex 32)" >> .env
```

### 3. Database Setup (5 min)

```bash
# Copy Prisma schema from data-model.md
# (See specs/004-gmail-email-search/data-model.md for schema)

# Edit prisma/schema.prisma and paste the schema

# Create and run migration
npx prisma migrate dev --name init

# Generate Prisma Client
npx prisma generate
```

### 4. Docker Services (5 min)

```bash
# Create docker-compose.yml in project root
cat > docker-compose.dev.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: gmail_service_dev
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
EOF

# Start services
docker-compose -f docker-compose.dev.yml up -d
```

## Minimal Working Implementation (90 minutes)

### Phase 1: OAuth Authentication (30 min)

**File**: `src/auth/oauth.controller.ts`
```typescript
import { Controller, Get, Req, Res, UseGuards } from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';

@Controller('auth')
export class OAuthController {
  @Get('google')
  @UseGuards(AuthGuard('google'))
  async googleAuth() {
    // Initiates OAuth flow
  }

  @Get('google/callback')
  @UseGuards(AuthGuard('google'))
  async googleAuthCallback(@Req() req, @Res() res) {
    // Handle OAuth callback
    // Create session, store tokens
    res.redirect(process.env.FRONTEND_URL);
  }

  @Get('status')
  async authStatus(@Req() req) {
    return {
      authenticated: !!req.user,
      user: req.user
    };
  }
}
```

**File**: `src/auth/google.strategy.ts`
```typescript
import { Injectable } from '@nestjs/common';
import { PassportStrategy } from '@nestjs/passport';
import { Strategy, VerifyCallback } from 'passport-google-oauth20';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class GoogleStrategy extends PassportStrategy(Strategy, 'google') {
  constructor(private configService: ConfigService) {
    super({
      clientID: configService.get('GOOGLE_CLIENT_ID'),
      clientSecret: configService.get('GOOGLE_CLIENT_SECRET'),
      callbackURL: configService.get('GOOGLE_CALLBACK_URL'),
      scope: [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile'
      ]
    });
  }

  async validate(
    accessToken: string,
    refreshToken: string,
    profile: any,
    done: VerifyCallback
  ): Promise<any> {
    const user = {
      email: profile.emails[0].value,
      name: profile.displayName,
      accessToken,
      refreshToken
    };
    done(null, user);
  }
}
```

### Phase 2: Gmail Search (30 min)

**File**: `src/gmail/gmail.service.ts`
```typescript
import { Injectable } from '@nestjs/common';
import { google } from 'googleapis';

@Injectable()
export class GmailService {
  async searchEmails(accessToken: string, searchRequest: any) {
    const oauth2Client = new google.auth.OAuth2();
    oauth2Client.setCredentials({ access_token: accessToken });

    const gmail = google.gmail({ version: 'v1', auth: oauth2Client });

    // Build Gmail search query
    const query = this.buildQuery(searchRequest);

    // List messages
    const response = await gmail.users.messages.list({
      userId: 'me',
      q: query,
      maxResults: 50,
      pageToken: searchRequest.pageToken
    });

    // Get message details
    const messages = await this.getMessageDetails(
      gmail,
      response.data.messages || []
    );

    return {
      emails: messages,
      pagination: {
        nextPageToken: response.data.nextPageToken,
        totalCount: response.data.resultSizeEstimate
      }
    };
  }

  private buildQuery(searchRequest: any): string {
    const parts = [];

    // Date range
    parts.push(`after:${searchRequest.startDate.replace(/-/g, '/')}`);
    parts.push(`before:${searchRequest.endDate.replace(/-/g, '/')}`);

    // Has attachments
    parts.push('has:attachment');

    // Filters
    if (searchRequest.senderFilter) {
      parts.push(`from:${searchRequest.senderFilter}`);
    }
    if (searchRequest.subjectFilter) {
      parts.push(`subject:${searchRequest.subjectFilter}`);
    }
    if (searchRequest.bodyFilter) {
      parts.push(searchRequest.bodyFilter);
    }

    return parts.join(' ');
  }

  private async getMessageDetails(gmail: any, messages: any[]) {
    const details = await Promise.all(
      messages.map(async (msg) => {
        const fullMessage = await gmail.users.messages.get({
          userId: 'me',
          id: msg.id,
          format: 'full'
        });
        return this.transformMessage(fullMessage.data);
      })
    );
    return details;
  }

  private transformMessage(gmailMessage: any) {
    const headers = gmailMessage.payload.headers;
    const getHeader = (name: string) =>
      headers.find((h: any) => h.name === name)?.value;

    return {
      id: gmailMessage.id,
      threadId: gmailMessage.threadId,
      sender: { email: getHeader('From') },
      subject: getHeader('Subject'),
      snippet: gmailMessage.snippet,
      date: new Date(parseInt(gmailMessage.internalDate)),
      hasAttachments: this.hasAttachments(gmailMessage.payload),
      attachments: this.extractAttachments(gmailMessage)
    };
  }

  private hasAttachments(payload: any): boolean {
    return payload.parts?.some((part: any) => part.filename) || false;
  }

  private extractAttachments(gmailMessage: any) {
    const parts = gmailMessage.payload.parts || [];
    const attachments = parts
      .filter((part: any) => part.filename && this.isCVFile(part.mimeType))
      .map((part: any) => ({
        id: part.body.attachmentId,
        messageId: gmailMessage.id,
        filename: part.filename,
        mimeType: part.mimeType,
        size: part.body.size
      }));
    return attachments;
  }

  private isCVFile(mimeType: string): boolean {
    const supported = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ];
    return supported.includes(mimeType);
  }
}
```

### Phase 3: Attachment Download (30 min)

**File**: `src/attachments/attachments.service.ts`
```typescript
import { Injectable } from '@nestjs/common';
import { google } from 'googleapis';
import { createWriteStream } from 'fs';
import { mkdir } from 'fs/promises';
import { join } from 'path';

@Injectable()
export class AttachmentsService {
  private storagePath = process.env.TEMP_STORAGE_PATH;

  async downloadAttachment(
    accessToken: string,
    messageId: string,
    attachmentId: string
  ) {
    const oauth2Client = new google.auth.OAuth2();
    oauth2Client.setCredentials({ access_token: accessToken });

    const gmail = google.gmail({ version: 'v1', auth: oauth2Client });

    // Get attachment data
    const response = await gmail.users.messages.attachments.get({
      userId: 'me',
      messageId,
      id: attachmentId
    });

    // Decode base64url data
    const data = Buffer.from(response.data.data, 'base64url');

    // Save to file system
    const filePath = await this.saveFile(messageId, attachmentId, data);

    // Schedule cleanup (simplified - use Bull queue in production)
    setTimeout(() => this.deleteFile(filePath), 24 * 60 * 60 * 1000);

    return filePath;
  }

  private async saveFile(
    messageId: string,
    attachmentId: string,
    data: Buffer
  ): Promise<string> {
    const dir = join(this.storagePath, messageId);
    await mkdir(dir, { recursive: true });

    const filePath = join(dir, attachmentId);
    const writeStream = createWriteStream(filePath);

    return new Promise((resolve, reject) => {
      writeStream.write(data);
      writeStream.end();
      writeStream.on('finish', () => resolve(filePath));
      writeStream.on('error', reject);
    });
  }

  private async deleteFile(filePath: string) {
    try {
      const { unlink } = await import('fs/promises');
      await unlink(filePath);
    } catch (error) {
      console.error('Failed to delete file:', error);
    }
  }
}
```

## Frontend Setup (Optional - 30 min)

```bash
# Navigate to frontend directory
cd ../../../frontend

# Initialize Next.js
npx create-next-app@latest . --typescript --tailwind --app --no-src-dir

# Install dependencies
npm install --save \
  @tanstack/react-query \
  axios \
  date-fns

# Create basic search page
# File: app/gmail-search/page.tsx
```

## Testing Your Setup (15 min)

```bash
# 1. Start backend
cd backend/services/gmail-service
npm run start:dev

# 2. Test OAuth flow
# Visit: http://localhost:8080/api/v1/auth/google
# Complete OAuth consent
# Should redirect to frontend with session

# 3. Test email search
curl -X POST http://localhost:8080/api/v1/emails/search \
  -H 'Content-Type: application/json' \
  -H 'Cookie: session=...' \
  -d '{
    "startDate": "2025-01-01",
    "endDate": "2025-01-31"
  }'

# 4. Check database
docker exec -it <postgres-container> psql -U postgres -d gmail_service_dev
\dt  # List tables
SELECT * FROM users;
SELECT * FROM user_tokens;
```

## Next Steps

### Implement Missing Features
1. ✅ OAuth authentication - Done
2. ✅ Email search - Done
3. ✅ Attachment download - Done
4. ⏭️ Rate limiting (Redis + rate-limiter-flexible)
5. ⏭️ Token encryption (crypto module)
6. ⏭️ File cleanup job (Bull queue)
7. ⏭️ Error handling & logging
8. ⏭️ Frontend UI components
9. ⏭️ E2E tests

### Production Readiness Checklist
- [ ] Environment variables secured (use secrets manager)
- [ ] HTTPS/TLS configured
- [ ] Rate limiting implemented
- [ ] Token encryption at rest
- [ ] File cleanup Bull queue
- [ ] Audit logging
- [ ] Monitoring & alerts (Prometheus/Grafana)
- [ ] Error tracking (Sentry)
- [ ] API documentation (Swagger UI)
- [ ] E2E tests passing
- [ ] Security audit completed
- [ ] Load testing completed

## Common Issues & Solutions

### Issue: OAuth redirect fails
**Solution**: Check `GOOGLE_CALLBACK_URL` matches exactly what's configured in Google Console

### Issue: Gmail API quota exceeded
**Solution**: Implement rate limiting with Redis token bucket algorithm

### Issue: Tokens not persisting
**Solution**: Verify DATABASE_URL and that Prisma migrations ran successfully

### Issue: Files not being deleted after 24 hours
**Solution**: Implement Bull queue for reliable job scheduling (simplified setTimeout won't work in production)

### Issue: Large file downloads timeout
**Solution**: Use streaming instead of loading entire file into memory

## Resources

- **Specification**: `specs/004-gmail-email-search/spec.md`
- **Research**: `specs/004-gmail-email-search/research.md`
- **Data Model**: `specs/004-gmail-email-search/data-model.md`
- **API Contract**: `specs/004-gmail-email-search/contracts/gmail-api.yaml`
- **Gmail API Docs**: https://developers.google.com/gmail/api/guides
- **NestJS Docs**: https://docs.nestjs.com
- **Prisma Docs**: https://www.prisma.io/docs

## Support

For questions or issues during implementation:
1. Check the specification and research documents
2. Review Gmail API documentation
3. Consult ProActive People development team
4. Create a GitHub issue with `004-gmail-email-search` label

---

**Quickstart Status**: Ready for development
**Estimated Time to Working Prototype**: 2-3 hours
**Next Command**: `/speckit.tasks` (after implementation planning complete)
