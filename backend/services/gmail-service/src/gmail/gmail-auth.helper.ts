import {
  Injectable,
  UnauthorizedException,
  Logger,
} from '@nestjs/common';
import { GaxiosError } from 'gaxios';
import { UserRepository } from '../auth/user.repository';
import { OAuthService } from '../auth/oauth.service';

/**
 * Gmail API Authentication Helper
 * Handles authentication validation and error recovery
 */
@Injectable()
export class GmailAuthHelper {
  private readonly logger = new Logger(GmailAuthHelper.name);

  constructor(
    private readonly userRepository: UserRepository,
    private readonly oauthService: OAuthService,
  ) {}

  /**
   * Validate that user has valid Gmail authentication
   * @param userId - User ID
   * @throws UnauthorizedException if authentication is invalid
   */
  async validateGmailAuth(userId: string): Promise<void> {
    const user = await this.userRepository.findById(userId);

    if (!user) {
      throw new UnauthorizedException('User not found');
    }

    if (!user.gmailAddress) {
      throw new UnauthorizedException('No Gmail account linked');
    }

    const token = await this.userRepository.getUserToken(userId);

    if (!token) {
      throw new UnauthorizedException(
        'No authentication token found. Please re-authenticate.',
      );
    }

    // Check if token is expired
    if (token.tokenExpiry < new Date()) {
      this.logger.warn(`Token expired for user ${userId}, attempting refresh`);

      try {
        await this.oauthService.refreshAccessToken(userId);
      } catch (error) {
        this.logger.error(
          `Failed to refresh token for user ${userId}: ${error.message}`,
        );
        throw new UnauthorizedException(
          'Authentication expired. Please re-authenticate.',
        );
      }
    }

    // Verify required scopes
    const requiredScopes = [
      'https://www.googleapis.com/auth/gmail.readonly',
    ];

    const hasRequiredScopes = requiredScopes.every((scope) =>
      token.scopes.includes(scope),
    );

    if (!hasRequiredScopes) {
      throw new UnauthorizedException(
        'Insufficient permissions. Please re-authenticate with required scopes.',
      );
    }
  }

  /**
   * Handle Gmail API errors and provide user-friendly messages
   * @param error - Error from Gmail API
   * @param userId - User ID
   * @returns User-friendly error message
   */
  handleGmailApiError(error: any, userId: string): never {
    this.logger.error(
      `Gmail API error for user ${userId}: ${error.message}`,
      error.stack,
    );

    if (this.isGaxiosError(error)) {
      const gaxiosError = error as GaxiosError;
      const status = gaxiosError.response?.status;

      switch (status) {
        case 401:
          throw new UnauthorizedException(
            'Authentication failed. Please re-authenticate with Gmail.',
          );

        case 403:
          if (
            gaxiosError.response?.data?.error?.message?.includes(
              'Rate Limit Exceeded',
            )
          ) {
            throw new Error(
              'Gmail API rate limit exceeded. Please try again in a few moments.',
            );
          }
          throw new UnauthorizedException(
            'Insufficient permissions to access Gmail. Please re-authenticate.',
          );

        case 404:
          throw new Error('Email or resource not found.');

        case 429:
          throw new Error(
            'Too many requests. Please slow down and try again in a moment.',
          );

        case 500:
        case 502:
        case 503:
          throw new Error(
            'Gmail service is temporarily unavailable. Please try again later.',
          );

        default:
          throw new Error(
            `Gmail API error: ${gaxiosError.response?.data?.error?.message || error.message}`,
          );
      }
    }

    // Network errors
    if (error.code === 'ENOTFOUND' || error.code === 'ECONNREFUSED') {
      throw new Error(
        'Unable to connect to Gmail. Please check your internet connection.',
      );
    }

    if (error.code === 'ETIMEDOUT') {
      throw new Error(
        'Connection to Gmail timed out. Please check your connection and try again.',
      );
    }

    // Generic error
    throw new Error(
      `An error occurred while accessing Gmail: ${error.message}`,
    );
  }

  /**
   * Check if error is a GaxiosError
   */
  private isGaxiosError(error: any): error is GaxiosError {
    return error.response !== undefined && error.config !== undefined;
  }

  /**
   * Check if user needs to re-authenticate
   * @param userId - User ID
   * @returns True if re-authentication is required
   */
  async needsReAuthentication(userId: string): Promise<boolean> {
    try {
      await this.validateGmailAuth(userId);
      return false;
    } catch (error) {
      if (error instanceof UnauthorizedException) {
        return true;
      }
      return false;
    }
  }

  /**
   * Get authentication status for user
   * @param userId - User ID
   * @returns Authentication status object
   */
  async getAuthStatus(userId: string): Promise<{
    authenticated: boolean;
    gmailAddress?: string;
    scopes?: string[];
    tokenExpiry?: Date;
    needsReauth: boolean;
  }> {
    try {
      const user = await this.userRepository.findById(userId);

      if (!user || !user.gmailAddress) {
        return { authenticated: false, needsReauth: true };
      }

      const token = await this.userRepository.getUserToken(userId);

      if (!token) {
        return {
          authenticated: false,
          gmailAddress: user.gmailAddress,
          needsReauth: true,
        };
      }

      const isExpired = token.tokenExpiry < new Date();
      const needsReauth = await this.needsReAuthentication(userId);

      return {
        authenticated: !isExpired && !needsReauth,
        gmailAddress: user.gmailAddress,
        scopes: token.scopes,
        tokenExpiry: token.tokenExpiry,
        needsReauth,
      };
    } catch (error) {
      this.logger.error(
        `Failed to get auth status for user ${userId}: ${error.message}`,
      );
      return { authenticated: false, needsReauth: true };
    }
  }
}
