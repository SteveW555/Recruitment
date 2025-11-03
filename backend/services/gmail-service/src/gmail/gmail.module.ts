import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';

// Controllers
import { GmailController } from './gmail.controller';
import { AdvancedSearchController } from './advanced-search.controller';

// Services
import { GmailService } from './gmail.service';
import { GmailClientService } from './gmail-client.service';
import { GmailAuthHelper } from './gmail-auth.helper';
import { QueryBuilderService } from './query-builder.service';
import { EmailTransformer } from './email.transformer';
import { RateLimitService } from './rate-limit.service';
import { SearchCacheService } from './search-cache.service';

// Advanced filtering services
import { AdvancedFilterService } from './advanced-filter.service';
import { SavedSearchService } from './saved-search.service';
import { FilterSuggestionService } from './filter-suggestion.service';

// Email preview services
import { EmailPreviewService } from './email-preview.service';
import { HtmlSanitizerService } from './html-sanitizer.service';
import { PreviewCacheService } from './preview-cache.service';

// Shared services from AuthModule
import { TokenRefreshService } from '../auth/token-refresh.service';
import { UserRepository } from '../auth/user.repository';
import { OAuthService } from '../auth/oauth.service';
import { AuditService } from '../audit/audit.service';
import { AuthModule } from '../auth/auth.module';

/**
 * Gmail Module
 * Handles Gmail API integration and email search functionality
 *
 * Features:
 * - Email search with date range and filters
 * - Advanced filtering with domain, keyword, and file type filters (US3)
 * - Saved searches with usage tracking (US3)
 * - Intelligent filter suggestions (US3)
 * - Email preview with HTML sanitization and caching (US4/FR-018)
 * - Thread conversation preview
 * - Gmail API client wrapper with automatic token management
 * - Rate limiting with exponential backoff (FR-013)
 * - Search results caching with Redis
 * - Email transformation to internal model
 * - CV email detection
 */
@Module({
  imports: [
    ConfigModule,
    AuthModule, // Import AuthModule to get shared services
  ],
  controllers: [
    GmailController,
    AdvancedSearchController,
  ],
  providers: [
    // Core Gmail services
    GmailService,
    GmailClientService,
    GmailAuthHelper,
    QueryBuilderService,
    EmailTransformer,
    RateLimitService,
    SearchCacheService,

    // Advanced filtering services (US3)
    AdvancedFilterService,
    SavedSearchService,
    FilterSuggestionService,

    // Email preview services (US4)
    EmailPreviewService,
    HtmlSanitizerService,
    PreviewCacheService,
  ],
  exports: [
    // Export services for use in other modules (e.g., AttachmentsModule)
    GmailService,
    GmailClientService,
    GmailAuthHelper,
    QueryBuilderService,
    EmailTransformer,
    RateLimitService,
    SearchCacheService,

    // Export advanced filtering services
    AdvancedFilterService,
    SavedSearchService,
    FilterSuggestionService,

    // Export email preview services
    EmailPreviewService,
    HtmlSanitizerService,
    PreviewCacheService,
  ],
})
export class GmailModule {}
