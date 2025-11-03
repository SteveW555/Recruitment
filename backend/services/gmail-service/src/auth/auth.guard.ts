import {
  Injectable,
  CanActivate,
  ExecutionContext,
  UnauthorizedException,
} from '@nestjs/common';
import { Observable } from 'rxjs';

/**
 * Authentication guard for protecting routes
 * Verifies user session exists and is valid
 */
@Injectable()
export class AuthGuard implements CanActivate {
  canActivate(
    context: ExecutionContext,
  ): boolean | Promise<boolean> | Observable<boolean> {
    const request = context.switchToHttp().getRequest();
    const session = request.session as any;

    // Check if user is authenticated
    if (!session || !session.userId) {
      throw new UnauthorizedException('Authentication required. Please log in with your Gmail account.');
    }

    // Session exists and has userId
    return true;
  }
}
