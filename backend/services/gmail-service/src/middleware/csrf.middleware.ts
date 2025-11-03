import { Injectable, NestMiddleware, ForbiddenException } from '@nestjs/common';
import { Request, Response, NextFunction } from 'express';
import * as crypto from 'crypto';

/**
 * CSRF protection middleware
 * Implements CSRF token validation for state-changing operations
 */
@Injectable()
export class CsrfMiddleware implements NestMiddleware {
  private readonly tokenLength = 32;

  use(req: Request, res: Response, next: NextFunction) {
    const session = req.session as any;

    // Skip CSRF check for safe methods
    if (['GET', 'HEAD', 'OPTIONS'].includes(req.method)) {
      // Generate CSRF token if not exists
      if (!session.csrfToken) {
        session.csrfToken = this.generateToken();
      }

      // Add CSRF token to response headers
      res.setHeader('X-CSRF-Token', session.csrfToken);

      return next();
    }

    // Validate CSRF token for state-changing methods
    const clientToken = req.headers['x-csrf-token'] as string;
    const sessionToken = session.csrfToken;

    if (!clientToken || !sessionToken) {
      throw new ForbiddenException('CSRF token missing');
    }

    if (!this.compareTokens(clientToken, sessionToken)) {
      throw new ForbiddenException('Invalid CSRF token');
    }

    next();
  }

  private generateToken(): string {
    return crypto.randomBytes(this.tokenLength).toString('hex');
  }

  private compareTokens(token1: string, token2: string): boolean {
    if (token1.length !== token2.length) {
      return false;
    }

    // Constant-time comparison to prevent timing attacks
    return crypto.timingSafeEqual(
      Buffer.from(token1),
      Buffer.from(token2),
    );
  }
}
