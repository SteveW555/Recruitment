import { Injectable, Logger, NotFoundException, BadRequestException } from '@nestjs/common';
import { PrismaClient } from '@prisma/client';
import { AdvancedSearchDto } from './advanced-filter.service';

export interface CreateSavedSearchDto {
  name: string;
  description?: string;
  filters: AdvancedSearchDto;
}

export interface UpdateSavedSearchDto {
  name?: string;
  description?: string;
  filters?: AdvancedSearchDto;
}

/**
 * Saved Search Service
 * Manages user's saved search filters for quick access
 * Implements US3: Advanced Filtering - Saved Searches
 */
@Injectable()
export class SavedSearchService {
  private readonly logger = new Logger(SavedSearchService.name);
  private readonly prisma: PrismaClient;
  private readonly MAX_SAVED_SEARCHES = 50;

  constructor() {
    this.prisma = new PrismaClient();
  }

  /**
   * Create a saved search
   * @param userId - User ID
   * @param data - Saved search data
   * @returns Created saved search
   */
  async createSavedSearch(userId: string, data: CreateSavedSearchDto) {
    // Check limit
    const count = await this.prisma.savedSearch.count({
      where: { userId },
    });

    if (count >= this.MAX_SAVED_SEARCHES) {
      throw new BadRequestException(
        `Maximum ${this.MAX_SAVED_SEARCHES} saved searches allowed`,
      );
    }

    // Check for duplicate name
    const existing = await this.prisma.savedSearch.findFirst({
      where: {
        userId,
        name: data.name,
      },
    });

    if (existing) {
      throw new BadRequestException(`Saved search with name "${data.name}" already exists`);
    }

    try {
      const savedSearch = await this.prisma.savedSearch.create({
        data: {
          userId,
          name: data.name,
          description: data.description,
          filters: data.filters as any, // Prisma Json type
        },
      });

      this.logger.log(`Created saved search ${savedSearch.id} for user ${userId}`);

      return savedSearch;
    } catch (error) {
      this.logger.error(`Failed to create saved search: ${error.message}`);
      throw error;
    }
  }

  /**
   * Get all saved searches for user
   * @param userId - User ID
   * @returns List of saved searches
   */
  async getUserSavedSearches(userId: string) {
    try {
      const searches = await this.prisma.savedSearch.findMany({
        where: { userId },
        orderBy: [
          { lastUsedAt: 'desc' }, // Most recently used first
          { createdAt: 'desc' },
        ],
      });

      return searches;
    } catch (error) {
      this.logger.error(`Failed to get saved searches for user ${userId}: ${error.message}`);
      return [];
    }
  }

  /**
   * Get single saved search
   * @param userId - User ID
   * @param searchId - Saved search ID
   * @returns Saved search or null
   */
  async getSavedSearch(userId: string, searchId: string) {
    try {
      const savedSearch = await this.prisma.savedSearch.findFirst({
        where: {
          id: searchId,
          userId,
        },
      });

      return savedSearch;
    } catch (error) {
      this.logger.error(`Failed to get saved search ${searchId}: ${error.message}`);
      return null;
    }
  }

  /**
   * Update saved search
   * @param userId - User ID
   * @param searchId - Saved search ID
   * @param data - Update data
   * @returns Updated saved search
   */
  async updateSavedSearch(
    userId: string,
    searchId: string,
    data: UpdateSavedSearchDto,
  ) {
    const existing = await this.getSavedSearch(userId, searchId);

    if (!existing) {
      throw new NotFoundException('Saved search not found');
    }

    // Check for duplicate name if name is being updated
    if (data.name && data.name !== existing.name) {
      const duplicate = await this.prisma.savedSearch.findFirst({
        where: {
          userId,
          name: data.name,
          id: { not: searchId },
        },
      });

      if (duplicate) {
        throw new BadRequestException(`Saved search with name "${data.name}" already exists`);
      }
    }

    try {
      const updated = await this.prisma.savedSearch.update({
        where: { id: searchId },
        data: {
          name: data.name,
          description: data.description,
          filters: data.filters as any,
        },
      });

      this.logger.log(`Updated saved search ${searchId} for user ${userId}`);

      return updated;
    } catch (error) {
      this.logger.error(`Failed to update saved search ${searchId}: ${error.message}`);
      throw error;
    }
  }

  /**
   * Delete saved search
   * @param userId - User ID
   * @param searchId - Saved search ID
   */
  async deleteSavedSearch(userId: string, searchId: string): Promise<void> {
    const existing = await this.getSavedSearch(userId, searchId);

    if (!existing) {
      throw new NotFoundException('Saved search not found');
    }

    try {
      await this.prisma.savedSearch.delete({
        where: { id: searchId },
      });

      this.logger.log(`Deleted saved search ${searchId} for user ${userId}`);
    } catch (error) {
      this.logger.error(`Failed to delete saved search ${searchId}: ${error.message}`);
      throw error;
    }
  }

  /**
   * Record usage of saved search
   * Updates useCount and lastUsedAt
   * @param userId - User ID
   * @param searchId - Saved search ID
   */
  async recordUsage(userId: string, searchId: string): Promise<void> {
    const existing = await this.getSavedSearch(userId, searchId);

    if (!existing) {
      return; // Silently fail if search doesn't exist
    }

    try {
      await this.prisma.savedSearch.update({
        where: { id: searchId },
        data: {
          useCount: { increment: 1 },
          lastUsedAt: new Date(),
        },
      });

      this.logger.debug(`Recorded usage for saved search ${searchId}`);
    } catch (error) {
      this.logger.error(`Failed to record usage for saved search ${searchId}: ${error.message}`);
    }
  }

  /**
   * Get most frequently used saved searches
   * @param userId - User ID
   * @param limit - Number of results (default 5)
   * @returns Top saved searches by use count
   */
  async getMostUsed(userId: string, limit: number = 5) {
    try {
      const searches = await this.prisma.savedSearch.findMany({
        where: { userId },
        orderBy: { useCount: 'desc' },
        take: limit,
      });

      return searches;
    } catch (error) {
      this.logger.error(`Failed to get most used searches: ${error.message}`);
      return [];
    }
  }

  /**
   * Get recently used saved searches
   * @param userId - User ID
   * @param limit - Number of results (default 5)
   * @returns Recently used searches
   */
  async getRecentlyUsed(userId: string, limit: number = 5) {
    try {
      const searches = await this.prisma.savedSearch.findMany({
        where: {
          userId,
          lastUsedAt: { not: null },
        },
        orderBy: { lastUsedAt: 'desc' },
        take: limit,
      });

      return searches;
    } catch (error) {
      this.logger.error(`Failed to get recently used searches: ${error.message}`);
      return [];
    }
  }

  /**
   * Get saved search statistics
   * @param userId - User ID
   * @returns Statistics
   */
  async getStats(userId: string): Promise<{
    totalSaved: number;
    totalUsage: number;
    averageUsage: number;
    mostUsedSearch: any;
  }> {
    try {
      const searches = await this.getUserSavedSearches(userId);

      const totalSaved = searches.length;
      const totalUsage = searches.reduce((sum, s) => sum + s.useCount, 0);
      const averageUsage = totalSaved > 0 ? totalUsage / totalSaved : 0;

      const mostUsed = searches.length > 0
        ? searches.reduce((max, s) => s.useCount > max.useCount ? s : max)
        : null;

      return {
        totalSaved,
        totalUsage,
        averageUsage: Math.round(averageUsage * 100) / 100,
        mostUsedSearch: mostUsed,
      };
    } catch (error) {
      this.logger.error(`Failed to get saved search stats: ${error.message}`);

      return {
        totalSaved: 0,
        totalUsage: 0,
        averageUsage: 0,
        mostUsedSearch: null,
      };
    }
  }

  /**
   * Close Prisma connection
   */
  async onModuleDestroy() {
    await this.prisma.$disconnect();
  }
}
