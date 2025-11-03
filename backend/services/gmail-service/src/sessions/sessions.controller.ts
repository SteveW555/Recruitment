import { Controller, Get, Req, UseGuards } from '@nestjs/common';
import { Request } from 'express';
import { SessionsService } from './sessions.service';
import { AuthGuard } from '../auth/auth.guard';

/**
 * Session management controller
 */
@Controller('sessions')
export class SessionsController {
  constructor(private readonly sessionsService: SessionsService) {}

  /**
   * Get current session information
   * GET /api/v1/sessions/current
   */
  @Get('current')
  @UseGuards(AuthGuard)
  async getCurrentSession(@Req() req: Request) {
    const sessionData = req.session as any;

    return this.sessionsService.getSessionInfo(sessionData);
  }
}
