import { Injectable, UnauthorizedException } from '@nestjs/common';
import { google } from 'googleapis';
import { TokenService } from './token.service';
import { UserRepository } from './user.repository';

/**
 * OAuth service for managing Google OAuth 2.0 flow and token operations
 */
@Injectable()
export class OAuthService {
  constructor(
    private readonly tokenService: TokenService,
    private readonly userRepository: UserRepository,
  ) {}

  /**
   * Handle OAuth callback and create/update user
   */
  async handleOAuthCallback(profile: any, tokens: any) {
    const gmailAddress = profile.emails[0].value;
    const email = profile.emails[0].value;
    const name = profile.displayName;

    // Find or create user
    let user = await this.userRepository.findByGmailAddress(gmailAddress);

    if (!user) {
      user = await this.userRepository.create({
        email,
        name,
        gmailAddress,
      });
    } else {
      await this.userRepository.updateLastLogin(user.id);
    }

    // Encrypt and store tokens
    const encryptedAccessToken = this.tokenService.encryptToken(
      tokens.access_token,
    );
    const encryptedRefreshToken = this.tokenService.encryptToken(
      tokens.refresh_token,
    );

    const tokenExpiry = new Date(Date.now() + tokens.expiry_date);

    await this.userRepository.upsertToken({
      userId: user.id,
      accessToken: encryptedAccessToken,
      refreshToken: encryptedRefreshToken,
      tokenExpiry,
      scopes: tokens.scope?.split(' ') || [],
    });

    return user;
  }

  /**
   * Get decrypted access token for user
   */
  async getAccessToken(userId: string): Promise<string> {
    const tokenRecord = await this.userRepository.getUserToken(userId);

    if (!tokenRecord) {
      throw new UnauthorizedException('No valid token found');
    }

    // Check if token needs refresh (within 5 minutes of expiry)
    const fiveMinutesFromNow = new Date(Date.now() + 5 * 60 * 1000);
    if (tokenRecord.tokenExpiry < fiveMinutesFromNow) {
      return this.refreshAccessToken(userId);
    }

    return this.tokenService.decryptToken(tokenRecord.accessToken);
  }

  /**
   * Refresh access token using refresh token
   */
  async refreshAccessToken(userId: string): Promise<string> {
    const tokenRecord = await this.userRepository.getUserToken(userId);

    if (!tokenRecord) {
      throw new UnauthorizedException('No token to refresh');
    }

    const refreshToken = this.tokenService.decryptToken(
      tokenRecord.refreshToken,
    );

    // Create OAuth2 client
    const oauth2Client = new google.auth.OAuth2(
      process.env.GOOGLE_CLIENT_ID,
      process.env.GOOGLE_CLIENT_SECRET,
      process.env.GOOGLE_CALLBACK_URL,
    );

    oauth2Client.setCredentials({ refresh_token: refreshToken });

    try {
      // Refresh the token
      const { credentials } = await oauth2Client.refreshAccessToken();

      // Store new access token
      const encryptedAccessToken = this.tokenService.encryptToken(
        credentials.access_token,
      );

      const tokenExpiry = new Date(credentials.expiry_date);

      await this.userRepository.upsertToken({
        userId,
        accessToken: encryptedAccessToken,
        refreshToken: tokenRecord.refreshToken, // Keep existing refresh token
        tokenExpiry,
        scopes: tokenRecord.scopes,
      });

      return credentials.access_token;
    } catch (error) {
      console.error('Token refresh failed:', error);
      throw new UnauthorizedException('Token refresh failed. Please re-authenticate.');
    }
  }

  /**
   * Revoke user tokens (logout)
   */
  async revokeTokens(userId: string): Promise<void> {
    const tokenRecord = await this.userRepository.getUserToken(userId);

    if (tokenRecord) {
      try {
        const accessToken = this.tokenService.decryptToken(
          tokenRecord.accessToken,
        );

        // Revoke token with Google
        const oauth2Client = new google.auth.OAuth2();
        await oauth2Client.revokeToken(accessToken);
      } catch (error) {
        console.error('Token revocation failed:', error);
        // Continue anyway to delete from database
      }
    }

    await this.userRepository.deleteUserTokens(userId);
  }
}
