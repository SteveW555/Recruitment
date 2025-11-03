import { Module, Global } from '@nestjs/common';
import { AuditLogService } from './audit-log.service';
import { PrismaModule } from '../prisma/prisma.module';

/**
 * Common Module (Global)
 *
 * Provides shared services used across the application:
 * - AuditLogService: Structured audit logging for security and compliance
 *
 * This module is marked as @Global so its exports are available
 * everywhere without explicit imports.
 */
@Global()
@Module({
  imports: [PrismaModule],
  providers: [AuditLogService],
  exports: [AuditLogService],
})
export class CommonModule {}
