import { Module } from '@nestjs/common';
import { GdprController } from './gdpr.controller';
import { GdprService } from './gdpr.service';
import { PrismaModule } from '../prisma/prisma.module';

/**
 * GDPR Compliance Module
 *
 * Provides GDPR compliance features:
 * - Article 15: Right to Access (data export)
 * - Article 17: Right to Erasure (account deletion)
 * - Article 20: Right to Data Portability (portable export)
 *
 * All endpoints require session authentication via SessionGuard.
 * Rate limiting is applied to prevent abuse.
 *
 * @see SECURITY.md - GDPR Compliance section
 */
@Module({
  imports: [PrismaModule],
  controllers: [GdprController],
  providers: [GdprService],
  exports: [GdprService], // Export for use in other modules if needed
})
export class GdprModule {}
