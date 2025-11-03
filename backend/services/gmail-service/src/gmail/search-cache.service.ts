import { Injectable, Logger } from '@nestjs/common';
import { Redis } from 'ioredis';
import { InjectRedis } from '@nestjs-modules/ioredis';
import { SearchEmailsResult } from './gmail.service';
import * as crypto from 'crypto';

/**
 * Search Results Caching Service
 * Implements Redis caching for email search results
 * Cache TTL: 5 minutes (300 seconds)
 * Cache invalidation: On new emails received (future enhancement)
 */
@Injectable()
export class SearchCacheService {
  private readonly logger = new Logger(SearchCacheService.name);

  // Cache configuration
  private readonly CACHE_TTL_SECONDS = 300; // 5 minutes
  private readonly CACHE_KEY_PREFIX = 'search_cache:';
  private readonly MAX_CACHE_SIZE_BYTES = 1024 * 1024; // 1MB max per cache entry

  constructor(@InjectRedis() private readonly redis: Redis) {}

  /**
   * Get cached search results
   * @param userId - User ID
   * @param queryString - Gmail query string
   * @returns Cached results or null if not found
   */
  async getCachedSearch(
    userId: string,
    queryString: string,
  ): Promise<SearchEmailsResult | null> {
    const cacheKey = this.generateCacheKey(userId, queryString);

    try {
      const cachedData = await this.redis.get(cacheKey);

      if (!cachedData) {
        this.logger.debug(`Cache miss for key: ${cacheKey}`);
        return null;
      }

      // Parse cached data
      const result: SearchEmailsResult = JSON.parse(cachedData);

      this.logger.debug(
        `Cache hit for key: ${cacheKey}, ${result.emails.length} emails`,
      );

      // Update cache stats
      await this.incrementCacheHit(userId);

      return result;
    } catch (error) {
      this.logger.error(
        `Failed to get cached search for user ${userId}: ${error.message}`,
      );
      return null;
    }
  }

  /**
   * Cache search results
   * @param userId - User ID
   * @param queryString - Gmail query string
   * @param results - Search results to cache
   */
  async cacheSearch(
    userId: string,
    queryString: string,
    results: SearchEmailsResult,
  ): Promise<void> {
    const cacheKey = this.generateCacheKey(userId, queryString);

    try {
      // Don't cache if results have pagination token (only cache first page)
      if (results.nextPageToken) {
        this.logger.debug(
          `Skipping cache for paginated results: ${cacheKey}`,
        );
        return;
      }

      // Serialize results
      const serialized = JSON.stringify(results);

      // Check size limit
      const sizeBytes = Buffer.byteLength(serialized, 'utf8');
      if (sizeBytes > this.MAX_CACHE_SIZE_BYTES) {
        this.logger.warn(
          `Search results too large to cache: ${sizeBytes} bytes (max ${this.MAX_CACHE_SIZE_BYTES})`,
        );
        return;
      }

      // Store in Redis with TTL
      await this.redis.setex(cacheKey, this.CACHE_TTL_SECONDS, serialized);

      this.logger.debug(
        `Cached search results: ${cacheKey}, ${results.emails.length} emails, ` +
          `${sizeBytes} bytes, TTL ${this.CACHE_TTL_SECONDS}s`,
      );

      // Update cache stats
      await this.incrementCacheWrite(userId);
    } catch (error) {
      this.logger.error(
        `Failed to cache search results for user ${userId}: ${error.message}`,
      );
      // Don't throw - caching failures shouldn't break the search
    }
  }

  /**
   * Invalidate cached searches for user
   * Call this when new emails are received or user performs actions
   * @param userId - User ID
   */
  async invalidateUserCache(userId: string): Promise<void> {
    try {
      // Find all cache keys for this user
      const pattern = `${this.CACHE_KEY_PREFIX}${userId}:*`;
      const keys = await this.redis.keys(pattern);

      if (keys.length === 0) {
        this.logger.debug(`No cache entries to invalidate for user ${userId}`);
        return;
      }

      // Delete all matching keys
      await this.redis.del(...keys);

      this.logger.log(
        `Invalidated ${keys.length} cache entries for user ${userId}`,
      );
    } catch (error) {
      this.logger.error(
        `Failed to invalidate cache for user ${userId}: ${error.message}`,
      );
    }
  }

  /**
   * Invalidate specific search cache
   * @param userId - User ID
   * @param queryString - Gmail query string
   */
  async invalidateSearch(userId: string, queryString: string): Promise<void> {
    const cacheKey = this.generateCacheKey(userId, queryString);

    try {
      await this.redis.del(cacheKey);
      this.logger.debug(`Invalidated cache entry: ${cacheKey}`);
    } catch (error) {
      this.logger.error(
        `Failed to invalidate search cache: ${error.message}`,
      );
    }
  }

  /**
   * Get cache statistics for user
   * @param userId - User ID
   * @returns Cache statistics
   */
  async getCacheStats(userId: string): Promise<{
    hits: number;
    writes: number;
    hitRate: number;
    cachedSearches: number;
  }> {
    try {
      const hitsKey = `cache_stats:${userId}:hits`;
      const writesKey = `cache_stats:${userId}:writes`;

      const [hits, writes, cachedSearches] = await Promise.all([
        this.redis.get(hitsKey).then((v) => parseInt(v || '0', 10)),
        this.redis.get(writesKey).then((v) => parseInt(v || '0', 10)),
        this.getCachedSearchCount(userId),
      ]);

      const totalRequests = hits + writes;
      const hitRate = totalRequests > 0 ? (hits / totalRequests) * 100 : 0;

      return {
        hits,
        writes,
        hitRate: Math.round(hitRate * 100) / 100,
        cachedSearches,
      };
    } catch (error) {
      this.logger.error(
        `Failed to get cache stats for user ${userId}: ${error.message}`,
      );

      return {
        hits: 0,
        writes: 0,
        hitRate: 0,
        cachedSearches: 0,
      };
    }
  }

  /**
   * Get count of cached searches for user
   */
  private async getCachedSearchCount(userId: string): Promise<number> {
    try {
      const pattern = `${this.CACHE_KEY_PREFIX}${userId}:*`;
      const keys = await this.redis.keys(pattern);
      return keys.length;
    } catch (error) {
      this.logger.error(`Failed to count cached searches: ${error.message}`);
      return 0;
    }
  }

  /**
   * Generate cache key from user ID and query string
   * Uses MD5 hash of query to create consistent, short keys
   */
  private generateCacheKey(userId: string, queryString: string): string {
    const queryHash = crypto
      .createHash('md5')
      .update(queryString)
      .digest('hex');

    return `${this.CACHE_KEY_PREFIX}${userId}:${queryHash}`;
  }

  /**
   * Increment cache hit counter
   */
  private async incrementCacheHit(userId: string): Promise<void> {
    const key = `cache_stats:${userId}:hits`;

    try {
      await this.redis.incr(key);

      // Set expiry on stats key (24 hours)
      await this.redis.expire(key, 86400);
    } catch (error) {
      this.logger.error(`Failed to increment cache hit: ${error.message}`);
    }
  }

  /**
   * Increment cache write counter
   */
  private async incrementCacheWrite(userId: string): Promise<void> {
    const key = `cache_stats:${userId}:writes`;

    try {
      await this.redis.incr(key);

      // Set expiry on stats key (24 hours)
      await this.redis.expire(key, 86400);
    } catch (error) {
      this.logger.error(`Failed to increment cache write: ${error.message}`);
    }
  }

  /**
   * Warm up cache for common searches (optional optimization)
   * @param userId - User ID
   * @param commonQueries - Array of common query strings
   */
  async warmUpCache(userId: string, commonQueries: string[]): Promise<void> {
    this.logger.log(
      `Warming up cache for user ${userId} with ${commonQueries.length} queries`,
    );

    for (const query of commonQueries) {
      const cacheKey = this.generateCacheKey(userId, query);

      // Check if already cached
      const exists = await this.redis.exists(cacheKey);

      if (!exists) {
        this.logger.debug(`Cache warm-up needed for query: ${query}`);
        // The actual search would be triggered by the application layer
      }
    }
  }

  /**
   * Clear all cache entries (admin function)
   */
  async clearAllCache(): Promise<void> {
    try {
      const pattern = `${this.CACHE_KEY_PREFIX}*`;
      const keys = await this.redis.keys(pattern);

      if (keys.length === 0) {
        this.logger.log('No cache entries to clear');
        return;
      }

      await this.redis.del(...keys);

      this.logger.log(`Cleared ${keys.length} cache entries`);
    } catch (error) {
      this.logger.error(`Failed to clear all cache: ${error.message}`);
    }
  }

  /**
   * Get cache memory usage statistics
   */
  async getCacheMemoryUsage(): Promise<{
    totalKeys: number;
    estimatedMemoryBytes: number;
    estimatedMemoryMB: number;
  }> {
    try {
      const pattern = `${this.CACHE_KEY_PREFIX}*`;
      const keys = await this.redis.keys(pattern);

      let totalMemory = 0;

      // Sample first 100 keys to estimate memory
      const sampleKeys = keys.slice(0, 100);

      for (const key of sampleKeys) {
        const value = await this.redis.get(key);
        if (value) {
          totalMemory += Buffer.byteLength(value, 'utf8');
        }
      }

      // Estimate total memory based on sample
      const avgMemoryPerKey = sampleKeys.length > 0 ? totalMemory / sampleKeys.length : 0;
      const estimatedTotal = Math.round(avgMemoryPerKey * keys.length);

      return {
        totalKeys: keys.length,
        estimatedMemoryBytes: estimatedTotal,
        estimatedMemoryMB: Math.round((estimatedTotal / (1024 * 1024)) * 100) / 100,
      };
    } catch (error) {
      this.logger.error(
        `Failed to get cache memory usage: ${error.message}`,
      );

      return {
        totalKeys: 0,
        estimatedMemoryBytes: 0,
        estimatedMemoryMB: 0,
      };
    }
  }
}
