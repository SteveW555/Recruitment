import { Injectable, UnauthorizedException } from '@nestjs/common';
import { UserRepository } from '../auth/user.repository';

/**
 * Session service for session management and validation
 */
@Injectable()
export class SessionsService {
  constructor(private readonly userRepository: UserRepository) {}

  /**
   * Validate session and return user
   */
  async validateSession(userId: string) {
    if (!userId) {
      throw new UnauthorizedException('No active session');
    }

    const user = await this.userRepository.findById(userId);

    if (!user) {
      throw new UnauthorizedException('User not found');
    }

    // Check if user has valid token
    const token = await this.userRepository.getUserToken(userId);

    if (!token || token.tokenExpiry < new Date()) {
      throw new UnauthorizedException('Session expired. Please re-authenticate.');
    }

    return {
      id: user.id,
      email: user.email,
      name: user.name,
      gmailAddress: user.gmailAddress,
      lastLoginAt: user.lastLoginAt,
    };
  }

  /**
   * Get session information
   */
  async getSessionInfo(sessionData: any) {
    if (!sessionData?.userId) {
      return {
        authenticated: false,
        user: null,
      };
    }

    try {
      const user = await this.validateSession(sessionData.userId);

      return {
        authenticated: true,
        user,
        createdAt: sessionData.createdAt,
        lastActivity: new Date(),
      };
    } catch (error) {
      return {
        authenticated: false,
        user: null,
        error: error.message,
      };
    }
  }
}
