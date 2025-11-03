import { Injectable, Logger } from '@nestjs/common';
import { InjectRedis } from '@nestjs-modules/ioredis';
import Redis from 'ioredis';
import { EmailPreview } from './email-preview.service';

/**
 * Preview Cache Service
 * Caches email preview data in Redis for performance
 * Implements caching layer for FR-018: Email Preview
 */
@Injectable()
export class PreviewCacheService {
  private readonly logger = new Logger(PreviewCacheService.name);
  private readonly CACHE_PREFIX = 'email_preview:';
  private readonly THREAD_CACHE_PREFIX = 'thread_preview:';
  private readonly CACHE_TTL = 15 * 60; // 15 minutes in seconds

  constructor(@InjectRedis() private readonly redis: Redis) {}

  /**
   * Get cached email preview
   * @param userId - User ID
   * @param emailId - Email ID
   * @returns Cached preview or null
   */
  async getEmailPreview(
    userId: string,
    emailId: string,
  ): Promise<EmailPreview | null> {
    try {
      const key = this.getEmailCacheKey(userId, emailId);
      const cached = await this.redis.get(key);

      if (!cached) {
        return null;
      }

      const preview = JSON.parse(cached) as EmailPreview;

      // Convert date strings back to Date objects
      preview.date = new Date(preview.date);

      this.logger.debug(`Cache hit for email preview ${emailId}`);
      return preview;
    } catch (error) {
      this.logger.error(`Failed to get cached preview: ${error.message}`);
      return null;
    }
  }

  /**
   * Cache email preview
   * @param userId - User ID
   * @param emailId - Email ID
   * @param preview - Email preview data
   * @param ttl - Time to live in seconds (optional)
   */
  async setEmailPreview(
    userId: string,
    emailId: string,
    preview: EmailPreview,
    ttl: number = this.CACHE_TTL,
  ): Promise<void> {
    try {
      const key = this.getEmailCacheKey(userId, emailId);
      const serialized = JSON.stringify(preview);

      await this.redis.setex(key, ttl, serialized);

      this.logger.debug(`Cached email preview ${emailId} for ${ttl}s`);
    } catch (error) {
      this.logger.error(`Failed to cache preview: ${error.message}`);
    }
  }

  /**
   * Get cached thread preview
   * @param userId - User ID
   * @param threadId - Thread ID
   * @returns Cached thread preview or null
   */
  async getThreadPreview(
    userId: string,
    threadId: string,
  ): Promise<EmailPreview[] | null> {
    try {
      const key = this.getThreadCacheKey(userId, threadId);
      const cached = await this.redis.get(key);

      if (!cached) {
        return null;
      }

      const previews = JSON.parse(cached) as EmailPreview[];

      // Convert date strings back to Date objects
      for (const preview of previews) {
        preview.date = new Date(preview.date);
      }

      this.logger.debug(`Cache hit for thread preview ${threadId}`);
      return previews;
    } catch (error) {
      this.logger.error(`Failed to get cached thread preview: ${error.message}`);
      return null;
    }
  }

  /**
   * Cache thread preview
   * @param userId - User ID
   * @param threadId - Thread ID
   * @param previews - Array of email previews
   * @param ttl - Time to live in seconds (optional)
   */
  async setThreadPreview(
    userId: string,
    threadId: string,
    previews: EmailPreview[],
    ttl: number = this.CACHE_TTL,
  ): Promise<void> {
    try {
      const key = this.getThreadCacheKey(userId, threadId);
      const serialized = JSON.stringify(previews);

      await this.redis.setex(key, ttl, serialized);

      this.logger.debug(`Cached thread preview ${threadId} for ${ttl}s`);
    } catch (error) {
      this.logger.error(`Failed to cache thread preview: ${error.message}`);
    }
  }

  /**
   * Invalidate email preview cache
   * @param userId - User ID
   * @param emailId - Email ID
   */
  async invalidateEmailPreview(
    userId: string,
    emailId: string,
  ): Promise<void> {
    try {
      const key = this.getEmailCacheKey(userId, emailId);
      await this.redis.del(key);

      this.logger.debug(`Invalidated cache for email ${emailId}`);
    } catch (error) {
      this.logger.error(`Failed to invalidate email cache: ${error.message}`);
    }
  }

  /**
   * Invalidate thread preview cache
   * @param userId - User ID
   * @param threadId - Thread ID
   */
  async invalidateThreadPreview(
    userId: string,
    threadId: string,
  ): Promise<void> {
    try {
      const key = this.getThreadCacheKey(userId, threadId);
      await this.redis.del(key);

      this.logger.debug(`Invalidated cache for thread ${threadId}`);
    } catch (error) {
      this.logger.error(`Failed to invalidate thread cache: ${error.message}`);
    }
  }

  /**
   * Invalidate all preview caches for user
   * @param userId - User ID
   */
  async invalidateUserPreviews(userId: string): Promise<void> {
    try {
      const emailPattern = this.getEmailCacheKey(userId, '*');
      const threadPattern = this.getThreadCacheKey(userId, '*');

      // Delete email preview caches
      const emailKeys = await this.redis.keys(emailPattern);
      if (emailKeys.length > 0) {
        await this.redis.del(...emailKeys);
      }

      // Delete thread preview caches
      const threadKeys = await this.redis.keys(threadPattern);
      if (threadKeys.length > 0) {
        await this.redis.del(...threadKeys);
      }

      this.logger.log(
        `Invalidated ${emailKeys.length + threadKeys.length} preview caches for user ${userId}`,
      );
    } catch (error) {
      this.logger.error(
        `Failed to invalidate user preview caches: ${error.message}`,
      );
    }
  }

  /**
   * Get cache statistics
   * @param userId - User ID
   * @returns Cache statistics
   */
  async getCacheStats(userId: string): Promise<{
    emailCaches: number;
    threadCaches: number;
    totalSize: number;
  }> {
    try {
      const emailPattern = this.getEmailCacheKey(userId, '*');
      const threadPattern = this.getThreadCacheKey(userId, '*');

      const emailKeys = await this.redis.keys(emailPattern);
      const threadKeys = await this.redis.keys(threadPattern);

      // Calculate total size
      let totalSize = 0;
      for (const key of [...emailKeys, ...threadKeys]) {
        const value = await this.redis.get(key);
        if (value) {
          totalSize += Buffer.byteLength(value, 'utf8');
        }
      }

      return {
        emailCaches: emailKeys.length,
        threadCaches: threadKeys.length,
        totalSize,
      };
    } catch (error) {
      this.logger.error(`Failed to get cache stats: ${error.message}`);
      return {
        emailCaches: 0,
        threadCaches: 0,
        totalSize: 0,
      };
    }
  }

  /**
   * Generate email cache key
   */
  private getEmailCacheKey(userId: string, emailId: string): string {
    return `${this.CACHE_PREFIX}${userId}:${emailId}`;
  }

  /**
   * Generate thread cache key
   */
  private getThreadCacheKey(userId: string, threadId: string): string {
    return `${this.THREAD_CACHE_PREFIX}${userId}:${threadId}`;
  }

  /**
   * Warm up cache with multiple previews
   * Useful for preloading previews for search results
   * @param userId - User ID
   * @param previews - Array of email previews to cache
   */
  async warmUpCache(
    userId: string,
    previews: EmailPreview[],
  ): Promise<void> {
    try {
      const pipeline = this.redis.pipeline();

      for (const preview of previews) {
        const key = this.getEmailCacheKey(userId, preview.id);
        const serialized = JSON.stringify(preview);
        pipeline.setex(key, this.CACHE_TTL, serialized);
      }

      await pipeline.exec();

      this.logger.debug(`Warmed up cache with ${previews.length} previews`);
    } catch (error) {
      this.logger.error(`Failed to warm up cache: ${error.message}`);
    }
  }

  /**
   * Check if preview is cached
   * @param userId - User ID
   * @param emailId - Email ID
   * @returns True if cached
   */
  async isCached(userId: string, emailId: string): Promise<boolean> {
    try {
      const key = this.getEmailCacheKey(userId, emailId);
      const exists = await this.redis.exists(key);
      return exists === 1;
    } catch (error) {
      this.logger.error(`Failed to check cache: ${error.message}`);
      return false;
    }
  }

  /**
   * Get cache TTL for email
   * @param userId - User ID
   * @param emailId - Email ID
   * @returns Remaining TTL in seconds, or -1 if not cached
   */
  async getCacheTtl(userId: string, emailId: string): Promise<number> {
    try {
      const key = this.getEmailCacheKey(userId, emailId);
      return await this.redis.ttl(key);
    } catch (error) {
      this.logger.error(`Failed to get cache TTL: ${error.message}`);
      return -1;
    }
  }
}
