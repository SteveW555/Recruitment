import {
  Controller,
  Get,
  Post,
  Req,
  Res,
  UseGuards,
  HttpStatus,
} from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';
import { Request, Response } from 'express';
import { OAuthService } from './oauth.service';
import { AuditService } from '../audit/audit.service';

/**
 * OAuth authentication controller
 * Handles Google OAuth 2.0 flow endpoints
 */
@Controller('auth')
export class OAuthController {
  constructor(
    private readonly oauthService: OAuthService,
    private readonly auditService: AuditService,
  ) {}

  /**
   * Initiate OAuth 2.0 flow
   * GET /api/v1/auth/google
   */
  @Get('google')
  @UseGuards(AuthGuard('google'))
  async googleAuth() {
    // Guard redirects to Google OAuth consent screen
  }

  /**
   * OAuth 2.0 callback handler
   * GET /api/v1/auth/google/callback
   */
  @Get('google/callback')
  @UseGuards(AuthGuard('google'))
  async googleAuthCallback(@Req() req: Request, @Res() res: Response) {
    try {
      const { accessToken, refreshToken, profile } = req.user as any;

      // Create or update user and store tokens
      const user = await this.oauthService.handleOAuthCallback(profile, {
        access_token: accessToken,
        refresh_token: refreshToken,
        expiry_date: Date.now() + 3600 * 1000, // 1 hour default
        scope: 'gmail.readonly userinfo.email userinfo.profile',
      });

      if (!user) {
        throw new Error('Failed to create or retrieve user');
      }

      // Store user in session
      (req.session as any).userId = user.id;
      (req.session as any).gmailAddress = user.gmailAddress;

      // Log successful authentication
      await this.auditService.log({
        userId: user.id,
        action: 'oauth_completed',
        resourceType: 'user',
        resourceId: user.id,
        metadata: {
          gmailAddress: user.gmailAddress,
          scopes: ['gmail.readonly', 'userinfo.email', 'userinfo.profile'],
        },
        ipAddress: req.ip,
        userAgent: req.headers['user-agent'] || 'unknown',
      });

      // Redirect to frontend
      const frontendUrl = process.env.FRONTEND_URL || 'http://localhost:3000';
      res.redirect(`${frontendUrl}/gmail-search`);
    } catch (error) {
      console.error('OAuth callback error:', error);

      await this.auditService.log({
        userId: null,
        action: 'oauth_failed',
        resourceType: 'user',
        resourceId: null,
        metadata: { error: error.message },
        ipAddress: req.ip,
        userAgent: req.headers['user-agent'] || 'unknown',
      });

      res.redirect(`${process.env.FRONTEND_URL}/auth/error`);
    }
  }

  /**
   * Logout user
   * POST /api/v1/auth/logout
   */
  @Post('logout')
  async logout(@Req() req: Request, @Res() res: Response) {
    const userId = (req.session as any)?.userId;

    if (userId) {
      // Revoke OAuth tokens
      await this.oauthService.revokeTokens(userId);

      // Log logout
      await this.auditService.log({
        userId,
        action: 'oauth_revoked',
        resourceType: 'user',
        resourceId: userId,
        metadata: {},
        ipAddress: req.ip,
        userAgent: req.headers['user-agent'] || 'unknown',
      });
    }

    // Destroy session
    req.session.destroy((err) => {
      if (err) {
        console.error('Session destruction error:', err);
      }
    });

    res.status(HttpStatus.NO_CONTENT).send();
  }

  /**
   * Check authentication status
   * GET /api/v1/auth/status
   */
  @Get('status')
  async authStatus(@Req() req: Request) {
    const userId = (req.session as any)?.userId;

    if (!userId) {
      return {
        authenticated: false,
        user: null,
        tokenExpiry: null,
      };
    }

    // Get user info (simplified - should use UserRepository)
    const session = req.session as any;

    return {
      authenticated: true,
      user: {
        id: userId,
        gmailAddress: session.gmailAddress,
      },
      tokenExpiry: null, // Would fetch from database in production
    };
  }
}
