import { Injectable } from '@nestjs/common';
import { Cron, CronExpression } from '@nestjs/schedule';
import { createClient } from 'redis';
import { OAuthService } from './oauth.service';
import { UserRepository } from './user.repository';
import { TokenService } from './token.service';

/**
 * Token refresh service with Redis caching
 * Automatically refreshes tokens before expiry
 */
@Injectable()
export class TokenRefreshService {
  private redisClient: any;

  constructor(
    private readonly oauthService: OAuthService,
    private readonly userRepository: UserRepository,
    private readonly tokenService: TokenService,
  ) {
    this.initializeRedis();
  }

  private async initializeRedis() {
    this.redisClient = createClient({
      host: process.env.REDIS_HOST || 'localhost',
      port: parseInt(process.env.REDIS_PORT) || 6379,
      password: process.env.REDIS_PASSWORD,
    });

    this.redisClient.on('error', (err) => {
      console.error('Redis client error:', err);
    });

    await this.redisClient.connect();
  }

  /**
   * Get cached access token or fetch fresh one
   * @param userId - User ID
   * @returns Decrypted access token
   */
  async getCachedToken(userId: string): Promise<string> {
    const cacheKey = `token:${userId}`;

    try {
      // Check Redis cache
      const cachedToken = await this.redisClient.get(cacheKey);

      if (cachedToken) {
        return this.tokenService.decryptToken(cachedToken);
      }

      // Cache miss - get from database
      const tokenRecord = await this.userRepository.getUserToken(userId);

      if (!tokenRecord) {
        throw new Error('No token found for user');
      }

      // Check if needs refresh
      const fiveMinutesFromNow = new Date(Date.now() + 5 * 60 * 1000);
      if (tokenRecord.tokenExpiry < fiveMinutesFromNow) {
        // Refresh token
        const freshToken = await this.oauthService.refreshAccessToken(userId);

        // Cache the encrypted token
        const encryptedToken = this.tokenService.encryptToken(freshToken);
        const ttl = Math.floor(
          (tokenRecord.tokenExpiry.getTime() - Date.now() - 5 * 60 * 1000) / 1000,
        );

        await this.redisClient.setEx(cacheKey, ttl, encryptedToken);

        return freshToken;
      }

      // Cache the token
      const ttl = Math.floor(
        (tokenRecord.tokenExpiry.getTime() - Date.now() - 5 * 60 * 1000) / 1000,
      );

      await this.redisClient.setEx(cacheKey, ttl, tokenRecord.accessToken);

      return this.tokenService.decryptToken(tokenRecord.accessToken);
    } catch (error) {
      console.error('Token cache error:', error);
      // Fallback to direct OAuth service
      return this.oauthService.getAccessToken(userId);
    }
  }

  /**
   * Invalidate cached token
   * @param userId - User ID
   */
  async invalidateCache(userId: string): Promise<void> {
    const cacheKey = `token:${userId}`;
    await this.redisClient.del(cacheKey);
  }

  /**
   * Cron job: Refresh tokens expiring within 5 minutes
   * Runs every minute
   */
  @Cron(CronExpression.EVERY_MINUTE)
  async handleTokenRefresh() {
    console.log('Running token refresh check...');

    try {
      const expiringTokens = await this.userRepository.getExpiringTokens(5);

      for (const tokenRecord of expiringTokens) {
        try {
          console.log(
            `Refreshing token for user: ${this.tokenService.maskToken(tokenRecord.userId)}`,
          );

          await this.oauthService.refreshAccessToken(tokenRecord.userId);

          // Invalidate cache to force re-fetch
          await this.invalidateCache(tokenRecord.userId);
        } catch (error) {
          console.error(
            `Failed to refresh token for user ${tokenRecord.userId}:`,
            error,
          );
        }
      }

      console.log(`Token refresh complete. Refreshed ${expiringTokens.length} tokens.`);
    } catch (error) {
      console.error('Token refresh cron job error:', error);
    }
  }

  async onModuleDestroy() {
    if (this.redisClient) {
      await this.redisClient.quit();
    }
  }
}
