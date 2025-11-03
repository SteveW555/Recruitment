import { Module, MiddlewareConsumer, NestModule } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { BullModule } from '@nestjs/bull';
import { RedisModule } from '@nestjs-modules/ioredis';

// Feature modules
import { AuthModule } from './auth/auth.module';
import { SessionsModule } from './sessions/sessions.module';
import { GmailModule } from './gmail/gmail.module';
import { AttachmentsModule } from './attachments/attachments.module';
import { GdprModule } from './gdpr/gdpr.module';
import { HealthModule } from './health/health.module';
import { CommonModule } from './common/common.module';

// Middleware
import { CsrfMiddleware } from './middleware/csrf.middleware';

@Module({
  imports: [
    // Configuration
    ConfigModule.forRoot({
      isGlobal: true,
      envFilePath: '.env',
    }),

    // Redis (for caching, rate limiting, token refresh)
    RedisModule.forRoot({
      type: 'single',
      url: `redis://${process.env.REDIS_HOST || 'localhost'}:${process.env.REDIS_PORT || '6379'}`,
    }),

    // Bull Queue (for file cleanup jobs)
    BullModule.forRoot({
      redis: {
        host: process.env.BULL_REDIS_HOST || 'localhost',
        port: parseInt(process.env.BULL_REDIS_PORT) || 6379,
      },
    }),

    // Feature modules
    CommonModule, // Global module for shared services (AuditLogService)
    AuthModule,
    SessionsModule,
    GmailModule,
    AttachmentsModule,
    GdprModule,
    HealthModule,
  ],
  controllers: [],
  providers: [],
})
export class AppModule implements NestModule {
  configure(consumer: MiddlewareConsumer) {
    // Apply CSRF protection to all routes except OAuth callback
    consumer
      .apply(CsrfMiddleware)
      .exclude('auth/google', 'auth/google/callback')
      .forRoutes('*');
  }
}
