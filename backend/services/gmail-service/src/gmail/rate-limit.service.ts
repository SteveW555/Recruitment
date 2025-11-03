import { Injectable, Logger } from '@nestjs/common';
import { Redis } from 'ioredis';
import { InjectRedis } from '@nestjs-modules/ioredis';

/**
 * Rate Limiting Service with Exponential Backoff
 * Implements FR-013: Gmail API rate limit handling
 *
 * Gmail API Quotas:
 * - 250 quota units per user per second
 * - 1 billion quota units per day
 * - Most operations cost 5-10 units
 *
 * Exponential Backoff Strategy:
 * - Attempt 1: Immediate (0s delay)
 * - Attempt 2: 1s delay
 * - Attempt 3: 2s delay
 * - Attempt 4: 4s delay
 * - After 3 failed attempts: Display user message
 */
@Injectable()
export class RateLimitService {
  private readonly logger = new Logger(RateLimitService.name);

  // Rate limit configuration
  private readonly MAX_REQUESTS_PER_SECOND = 250;
  private readonly RATE_LIMIT_WINDOW_MS = 1000; // 1 second
  private readonly MAX_RETRY_ATTEMPTS = 3;
  private readonly BASE_DELAY_MS = 1000; // 1 second base delay

  constructor(@InjectRedis() private readonly redis: Redis) {}

  /**
   * Check if user has exceeded rate limit
   * @param userId - User ID
   * @throws Error if rate limit exceeded
   */
  async checkRateLimit(userId: string): Promise<void> {
    const key = `rate_limit:${userId}`;
    const now = Date.now();
    const windowStart = now - this.RATE_LIMIT_WINDOW_MS;

    try {
      // Remove old entries outside the time window
      await this.redis.zremrangebyscore(key, 0, windowStart);

      // Count requests in current window
      const requestCount = await this.redis.zcard(key);

      if (requestCount >= this.MAX_REQUESTS_PER_SECOND) {
        this.logger.warn(`Rate limit exceeded for user ${userId}`);

        // Log rate limit event
        await this.logRateLimitEvent(userId, requestCount);

        throw new Error(
          'Gmail API rate limit exceeded. Please try again in a moment.',
        );
      }

      // Add current request to the window
      await this.redis.zadd(key, now, `${now}-${Math.random()}`);

      // Set expiry on key (cleanup)
      await this.redis.expire(key, 2); // 2 seconds TTL
    } catch (error) {
      if (error.message.includes('rate limit')) {
        throw error;
      }

      this.logger.error(
        `Failed to check rate limit for user ${userId}: ${error.message}`,
      );
      // Don't throw - allow request to proceed if Redis fails
    }
  }

  /**
   * Handle rate limit error with exponential backoff retry
   * Implements FR-013 retry logic: 1s, 2s, 4s delays
   * @param userId - User ID
   * @param operation - Operation to retry
   * @returns Operation result
   */
  async handleRateLimitWithRetry<T>(
    userId: string,
    operation: () => Promise<T>,
  ): Promise<T> {
    let lastError: Error;

    for (let attempt = 1; attempt <= this.MAX_RETRY_ATTEMPTS; attempt++) {
      try {
        // Calculate exponential backoff delay
        // Attempt 1: 0ms, Attempt 2: 1000ms, Attempt 3: 2000ms, Attempt 4: 4000ms
        const delayMs =
          attempt === 1 ? 0 : this.BASE_DELAY_MS * Math.pow(2, attempt - 2);

        if (delayMs > 0) {
          this.logger.log(
            `Rate limit retry attempt ${attempt}/${this.MAX_RETRY_ATTEMPTS} ` +
              `for user ${userId}, waiting ${delayMs}ms`,
          );

          await this.delay(delayMs);
        }

        // Attempt the operation
        const result = await operation();

        // Success - log recovery if this was a retry
        if (attempt > 1) {
          this.logger.log(
            `Rate limit recovered on attempt ${attempt} for user ${userId}`,
          );
        }

        return result;
      } catch (error) {
        lastError = error;

        // If not a rate limit error, throw immediately
        if (!this.isRateLimitError(error)) {
          throw error;
        }

        // Log retry attempt
        this.logger.warn(
          `Rate limit hit on attempt ${attempt}/${this.MAX_RETRY_ATTEMPTS} for user ${userId}`,
        );

        // If this was the last attempt, break and throw
        if (attempt === this.MAX_RETRY_ATTEMPTS) {
          break;
        }
      }
    }

    // All retries failed - log and throw user-friendly error
    await this.logRateLimitFailure(userId, this.MAX_RETRY_ATTEMPTS);

    throw new Error(
      'Gmail API rate limit exceeded. We attempted to retry your request ' +
        `${this.MAX_RETRY_ATTEMPTS} times with exponential backoff (1s, 2s, 4s delays), ` +
        'but the rate limit persists. Please wait a few moments and try again. ' +
        'All rate limit events have been logged for monitoring.',
    );
  }

  /**
   * Check if error is a rate limit error
   */
  private isRateLimitError(error: any): boolean {
    const errorMessage = error.message?.toLowerCase() || '';
    const errorCode = error.code;

    return (
      errorMessage.includes('rate limit') ||
      errorMessage.includes('quota exceeded') ||
      errorMessage.includes('too many requests') ||
      errorCode === 429 ||
      errorCode === 'RATE_LIMIT_EXCEEDED'
    );
  }

  /**
   * Delay execution for specified milliseconds
   */
  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * Log rate limit event for monitoring
   * Implements FR-013: Log all rate limit events
   */
  private async logRateLimitEvent(
    userId: string,
    requestCount: number,
  ): Promise<void> {
    const event = {
      timestamp: new Date().toISOString(),
      userId,
      event: 'rate_limit_exceeded',
      requestCount,
      windowMs: this.RATE_LIMIT_WINDOW_MS,
    };

    try {
      // Store in Redis list for monitoring
      await this.redis.lpush('rate_limit_events', JSON.stringify(event));

      // Keep only last 1000 events
      await this.redis.ltrim('rate_limit_events', 0, 999);

      this.logger.warn(
        `Rate limit event logged: ${JSON.stringify(event)}`,
      );
    } catch (error) {
      this.logger.error(`Failed to log rate limit event: ${error.message}`);
    }
  }

  /**
   * Log rate limit retry failure
   */
  private async logRateLimitFailure(
    userId: string,
    attempts: number,
  ): Promise<void> {
    const event = {
      timestamp: new Date().toISOString(),
      userId,
      event: 'rate_limit_retry_failed',
      attempts,
      message: 'All retry attempts exhausted',
    };

    try {
      await this.redis.lpush('rate_limit_failures', JSON.stringify(event));
      await this.redis.ltrim('rate_limit_failures', 0, 999);

      this.logger.error(
        `Rate limit retry failed: ${JSON.stringify(event)}`,
      );
    } catch (error) {
      this.logger.error(
        `Failed to log rate limit failure: ${error.message}`,
      );
    }
  }

  /**
   * Get rate limit statistics for user
   * @param userId - User ID
   * @returns Rate limit stats
   */
  async getRateLimitStats(userId: string): Promise<{
    currentRequests: number;
    maxRequests: number;
    windowMs: number;
    availableRequests: number;
    percentUsed: number;
  }> {
    const key = `rate_limit:${userId}`;
    const now = Date.now();
    const windowStart = now - this.RATE_LIMIT_WINDOW_MS;

    try {
      // Remove old entries
      await this.redis.zremrangebyscore(key, 0, windowStart);

      // Count current requests
      const currentRequests = await this.redis.zcard(key);

      const availableRequests = Math.max(
        0,
        this.MAX_REQUESTS_PER_SECOND - currentRequests,
      );

      const percentUsed =
        (currentRequests / this.MAX_REQUESTS_PER_SECOND) * 100;

      return {
        currentRequests,
        maxRequests: this.MAX_REQUESTS_PER_SECOND,
        windowMs: this.RATE_LIMIT_WINDOW_MS,
        availableRequests,
        percentUsed: Math.round(percentUsed * 100) / 100,
      };
    } catch (error) {
      this.logger.error(
        `Failed to get rate limit stats for user ${userId}: ${error.message}`,
      );

      return {
        currentRequests: 0,
        maxRequests: this.MAX_REQUESTS_PER_SECOND,
        windowMs: this.RATE_LIMIT_WINDOW_MS,
        availableRequests: this.MAX_REQUESTS_PER_SECOND,
        percentUsed: 0,
      };
    }
  }

  /**
   * Reset rate limit for user (admin function)
   * @param userId - User ID
   */
  async resetRateLimit(userId: string): Promise<void> {
    const key = `rate_limit:${userId}`;

    try {
      await this.redis.del(key);
      this.logger.log(`Rate limit reset for user ${userId}`);
    } catch (error) {
      this.logger.error(
        `Failed to reset rate limit for user ${userId}: ${error.message}`,
      );
    }
  }
}
