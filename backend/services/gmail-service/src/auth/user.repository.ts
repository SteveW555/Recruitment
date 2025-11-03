import { Injectable } from '@nestjs/common';
import { PrismaClient } from '@prisma/client';

/**
 * User repository for database operations
 * Handles CRUD operations for User and UserToken entities
 */
@Injectable()
export class UserRepository {
  private prisma: PrismaClient;

  constructor() {
    this.prisma = new PrismaClient();
  }

  async onModuleDestroy() {
    await this.prisma.$disconnect();
  }

  /**
   * Find user by Gmail address
   */
  async findByGmailAddress(gmailAddress: string) {
    return this.prisma.user.findUnique({
      where: { gmailAddress },
      include: { tokens: true },
    });
  }

  /**
   * Find user by ID
   */
  async findById(id: string) {
    return this.prisma.user.findUnique({
      where: { id },
      include: { tokens: true },
    });
  }

  /**
   * Create new user
   */
  async create(data: {
    email: string;
    name?: string;
    gmailAddress: string;
  }) {
    return this.prisma.user.create({
      data: {
        ...data,
        lastLoginAt: new Date(),
      },
    });
  }

  /**
   * Update user's last login timestamp
   */
  async updateLastLogin(userId: string) {
    return this.prisma.user.update({
      where: { id: userId },
      data: { lastLoginAt: new Date() },
    });
  }

  /**
   * Store or update user tokens
   */
  async upsertToken(data: {
    userId: string;
    accessToken: string;
    refreshToken: string;
    tokenExpiry: Date;
    scopes: string[];
  }) {
    // Delete existing tokens for this user
    await this.prisma.userToken.deleteMany({
      where: { userId: data.userId },
    });

    // Create new token
    return this.prisma.userToken.create({
      data,
    });
  }

  /**
   * Get user's active token
   */
  async getUserToken(userId: string) {
    return this.prisma.userToken.findFirst({
      where: {
        userId,
        tokenExpiry: { gt: new Date() },
      },
      orderBy: { createdAt: 'desc' },
    });
  }

  /**
   * Get tokens expiring soon (within specified minutes)
   */
  async getExpiringTokens(withinMinutes: number = 5) {
    const expiryThreshold = new Date(Date.now() + withinMinutes * 60 * 1000);

    return this.prisma.userToken.findMany({
      where: {
        tokenExpiry: {
          lte: expiryThreshold,
          gt: new Date(),
        },
      },
      include: { user: true },
    });
  }

  /**
   * Delete user tokens (logout)
   */
  async deleteUserTokens(userId: string) {
    return this.prisma.userToken.deleteMany({
      where: { userId },
    });
  }
}
