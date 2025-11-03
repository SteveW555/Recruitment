import { Module } from '@nestjs/common';
import { PassportModule } from '@nestjs/passport';
import { ConfigModule } from '@nestjs/config';
import { ScheduleModule } from '@nestjs/schedule';

// Controllers
import { OAuthController } from './oauth.controller';

// Services
import { OAuthService } from './oauth.service';
import { TokenService } from './token.service';
import { TokenRefreshService } from './token-refresh.service';
import { UserRepository } from './user.repository';

// Strategies
import { GoogleStrategy } from './google.strategy';

// Guards
import { AuthGuard } from './auth.guard';

// Audit
import { AuditService } from '../audit/audit.service';

/**
 * Authentication module
 * Handles OAuth 2.0, token management, and session authentication
 */
@Module({
  imports: [
    PassportModule.register({ defaultStrategy: 'google' }),
    ConfigModule,
    ScheduleModule.forRoot(), // For token refresh cron jobs
  ],
  controllers: [OAuthController],
  providers: [
    // Services
    OAuthService,
    TokenService,
    TokenRefreshService,
    UserRepository,
    AuditService,

    // Strategies
    GoogleStrategy,

    // Guards
    AuthGuard,
  ],
  exports: [
    OAuthService,
    TokenService,
    TokenRefreshService,
    UserRepository,
    AuthGuard,
    AuditService,
  ],
})
export class AuthModule {}
