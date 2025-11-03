/**
 * Gmail API Client
 * Frontend service for interacting with Gmail Email Search backend
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api/v1';

class GmailApiClient {
  constructor() {
    this.baseUrl = `${API_BASE_URL}/gmail`;
    this.advancedUrl = `${API_BASE_URL}/gmail/advanced`;
    this.attachmentsUrl = `${API_BASE_URL}/attachments`;
  }

  /**
   * Generic fetch wrapper with error handling
   */
  async request(url, options = {}) {
    const defaultOptions = {
      credentials: 'include', // Include cookies for session auth
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, { ...defaultOptions, ...options });

      if (!response.ok) {
        const error = await response.json().catch(() => ({
          message: `HTTP ${response.status}: ${response.statusText}`,
        }));
        throw new Error(error.message || 'Request failed');
      }

      return await response.json();
    } catch (error) {
      console.error(`API Request failed: ${url}`, error);
      throw error;
    }
  }

  // =============================================================================
  // Email Search (US1)
  // =============================================================================

  /**
   * Search emails with filters
   * @param {Object} params - Search parameters
   * @returns {Promise<Object>} Search results
   */
  async searchEmails(params = {}) {
    const queryString = new URLSearchParams(
      Object.entries(params).filter(([_, v]) => v != null)
    ).toString();

    const url = `${this.baseUrl}/search?${queryString}`;
    return await this.request(url);
  }

  /**
   * Search CV emails
   * @param {Object} params - Search parameters
   * @returns {Promise<Object>} CV email results
   */
  async searchCVEmails(params = {}) {
    const queryString = new URLSearchParams(
      Object.entries(params).filter(([_, v]) => v != null)
    ).toString();

    const url = `${this.baseUrl}/search/cv?${queryString}`;
    return await this.request(url);
  }

  /**
   * Get single email by ID
   * @param {string} emailId - Email ID
   * @returns {Promise<Object>} Email data
   */
  async getEmail(emailId) {
    const url = `${this.baseUrl}/emails/${emailId}`;
    return await this.request(url);
  }

  /**
   * Get email count
   * @param {Object} params - Date range parameters
   * @returns {Promise<Object>} Email count
   */
  async getEmailCount(params = {}) {
    const queryString = new URLSearchParams(
      Object.entries(params).filter(([_, v]) => v != null)
    ).toString();

    const url = `${this.baseUrl}/count?${queryString}`;
    return await this.request(url);
  }

  // =============================================================================
  // Email Preview (US4)
  // =============================================================================

  /**
   * Get email preview with full content
   * @param {string} emailId - Email ID
   * @param {boolean} sanitize - Sanitize HTML (default: true)
   * @returns {Promise<Object>} Email preview
   */
  async getEmailPreview(emailId, sanitize = true) {
    const url = `${this.baseUrl}/emails/${emailId}/preview?sanitize=${sanitize}`;
    return await this.request(url);
  }

  /**
   * Get thread preview
   * @param {string} threadId - Thread ID
   * @param {boolean} sanitize - Sanitize HTML (default: true)
   * @returns {Promise<Object>} Thread preview
   */
  async getThreadPreview(threadId, sanitize = true) {
    const url = `${this.baseUrl}/threads/${threadId}/preview?sanitize=${sanitize}`;
    return await this.request(url);
  }

  /**
   * Get email as plain text
   * @param {string} emailId - Email ID
   * @returns {Promise<Object>} Plain text email
   */
  async getEmailText(emailId) {
    const url = `${this.baseUrl}/emails/${emailId}/text`;
    return await this.request(url);
  }

  // =============================================================================
  // Advanced Filtering (US3)
  // =============================================================================

  /**
   * Advanced search with complex filters
   * @param {Object} filters - Advanced filter options
   * @param {Object} pagination - Pagination options
   * @returns {Promise<Object>} Search results
   */
  async advancedSearch(filters, pagination = {}) {
    const url = `${this.advancedUrl}/search`;
    const body = { ...filters, ...pagination };
    return await this.request(url, {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  /**
   * Search by domain
   * @param {string} domain - Domain to filter
   * @param {Object} params - Additional parameters
   * @returns {Promise<Object>} Search results
   */
  async searchByDomain(domain, params = {}) {
    const queryString = new URLSearchParams({
      domain,
      ...Object.entries(params).reduce((acc, [k, v]) => {
        if (v != null) acc[k] = v;
        return acc;
      }, {}),
    }).toString();

    const url = `${this.advancedUrl}/search/domain?${queryString}`;
    return await this.request(url);
  }

  /**
   * Search by keywords
   * @param {string[]} keywords - Keywords to search
   * @param {boolean} matchAll - Match all keywords
   * @param {Object} params - Additional parameters
   * @returns {Promise<Object>} Search results
   */
  async searchByKeywords(keywords, matchAll = false, params = {}) {
    const url = `${this.advancedUrl}/search/keywords`;
    const body = { keywords, matchAll, ...params };
    return await this.request(url, {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  /**
   * Search recruitment emails
   * @param {Object} params - Date range parameters
   * @returns {Promise<Object>} Recruitment emails
   */
  async searchRecruitmentEmails(params = {}) {
    const queryString = new URLSearchParams(
      Object.entries(params).filter(([_, v]) => v != null)
    ).toString();

    const url = `${this.advancedUrl}/search/recruitment?${queryString}`;
    return await this.request(url);
  }

  // =============================================================================
  // Saved Searches (US3)
  // =============================================================================

  /**
   * Get all saved searches
   * @returns {Promise<Object>} Saved searches
   */
  async getSavedSearches() {
    const url = `${this.advancedUrl}/saved`;
    return await this.request(url);
  }

  /**
   * Create saved search
   * @param {Object} data - Saved search data
   * @returns {Promise<Object>} Created saved search
   */
  async createSavedSearch(data) {
    const url = `${this.advancedUrl}/saved`;
    return await this.request(url, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * Get single saved search
   * @param {string} searchId - Saved search ID
   * @returns {Promise<Object>} Saved search
   */
  async getSavedSearch(searchId) {
    const url = `${this.advancedUrl}/saved/${searchId}`;
    return await this.request(url);
  }

  /**
   * Update saved search
   * @param {string} searchId - Saved search ID
   * @param {Object} data - Updated data
   * @returns {Promise<Object>} Updated saved search
   */
  async updateSavedSearch(searchId, data) {
    const url = `${this.advancedUrl}/saved/${searchId}`;
    return await this.request(url, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  /**
   * Delete saved search
   * @param {string} searchId - Saved search ID
   * @returns {Promise<Object>} Success message
   */
  async deleteSavedSearch(searchId) {
    const url = `${this.advancedUrl}/saved/${searchId}`;
    return await this.request(url, {
      method: 'DELETE',
    });
  }

  /**
   * Execute saved search
   * @param {string} searchId - Saved search ID
   * @param {Object} pagination - Pagination options
   * @returns {Promise<Object>} Search results
   */
  async executeSavedSearch(searchId, pagination = {}) {
    const queryString = new URLSearchParams(
      Object.entries(pagination).filter(([_, v]) => v != null)
    ).toString();

    const url = `${this.advancedUrl}/saved/${searchId}/execute?${queryString}`;
    return await this.request(url);
  }

  /**
   * Get saved search statistics
   * @returns {Promise<Object>} Statistics
   */
  async getSavedSearchStats() {
    const url = `${this.advancedUrl}/saved-stats`;
    return await this.request(url);
  }

  // =============================================================================
  // Filter Suggestions (US3)
  // =============================================================================

  /**
   * Get filter suggestions
   * @returns {Promise<Object>} Filter suggestions
   */
  async getFilterSuggestions() {
    const url = `${this.advancedUrl}/suggestions`;
    return await this.request(url);
  }

  /**
   * Get domain suggestions
   * @returns {Promise<Object>} Domain suggestions
   */
  async getDomainSuggestions() {
    const url = `${this.advancedUrl}/suggestions/domains`;
    return await this.request(url);
  }

  /**
   * Get date range suggestions
   * @returns {Promise<Object>} Date range suggestions
   */
  async getDateRangeSuggestions() {
    const url = `${this.advancedUrl}/suggestions/date-ranges`;
    return await this.request(url);
  }

  /**
   * Get file type suggestions
   * @returns {Promise<Object>} File type suggestions
   */
  async getFileTypeSuggestions() {
    const url = `${this.advancedUrl}/suggestions/file-types`;
    return await this.request(url);
  }

  // =============================================================================
  // Attachments (US2)
  // =============================================================================

  /**
   * Download single attachment
   * @param {string} emailId - Email ID
   * @param {string} attachmentId - Attachment ID
   * @param {string} filename - Filename
   * @returns {Promise<Object>} Download data
   */
  async downloadAttachment(emailId, attachmentId, filename) {
    const url = `${this.attachmentsUrl}/download`;
    return await this.request(url, {
      method: 'POST',
      body: JSON.stringify({ emailId, attachmentId, filename }),
    });
  }

  /**
   * Download all email attachments
   * @param {string} emailId - Email ID
   * @param {Array} attachments - Array of attachment objects
   * @returns {Promise<Object>} Download data
   */
  async downloadEmailAttachments(emailId, attachments) {
    const url = `${this.attachmentsUrl}/download-email`;
    return await this.request(url, {
      method: 'POST',
      body: JSON.stringify({ emailId, attachments }),
    });
  }

  /**
   * Get downloaded file
   * @param {string} downloadId - Download ID
   * @returns {Promise<Blob>} File blob
   */
  async getDownloadedFile(downloadId) {
    const url = `${this.attachmentsUrl}/downloads/${downloadId}`;
    const response = await fetch(url, { credentials: 'include' });

    if (!response.ok) {
      throw new Error('Failed to download file');
    }

    return await response.blob();
  }

  /**
   * List user's downloads
   * @returns {Promise<Object>} Downloads list
   */
  async listDownloads() {
    const url = `${this.attachmentsUrl}/downloads`;
    return await this.request(url);
  }

  /**
   * Delete download
   * @param {string} downloadId - Download ID
   * @returns {Promise<Object>} Success message
   */
  async deleteDownload(downloadId) {
    const url = `${this.attachmentsUrl}/downloads/${downloadId}`;
    return await this.request(url, {
      method: 'DELETE',
    });
  }

  /**
   * Bulk download as ZIP
   * @param {string[]} downloadIds - Array of download IDs
   * @returns {Promise<Blob>} ZIP file blob
   */
  async bulkDownload(downloadIds) {
    const url = `${this.attachmentsUrl}/bulk-download`;
    const response = await fetch(url, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ downloadIds }),
    });

    if (!response.ok) {
      throw new Error('Failed to create bulk download');
    }

    return await response.blob();
  }

  /**
   * Get download statistics
   * @returns {Promise<Object>} Statistics
   */
  async getDownloadStats() {
    const url = `${this.attachmentsUrl}/stats`;
    return await this.request(url);
  }

  // =============================================================================
  // Cache Management
  // =============================================================================

  /**
   * Get cache statistics
   * @returns {Promise<Object>} Cache statistics
   */
  async getCacheStats() {
    const url = `${this.baseUrl}/cache-stats`;
    return await this.request(url);
  }

  /**
   * Invalidate cache
   * @returns {Promise<Object>} Success message
   */
  async invalidateCache() {
    const url = `${this.baseUrl}/cache/invalidate`;
    return await this.request(url);
  }

  /**
   * Get preview cache statistics
   * @returns {Promise<Object>} Preview cache statistics
   */
  async getPreviewCacheStats() {
    const url = `${this.baseUrl}/preview-cache/stats`;
    return await this.request(url);
  }

  /**
   * Invalidate email preview cache
   * @param {string} emailId - Email ID
   * @returns {Promise<Object>} Success message
   */
  async invalidateEmailPreview(emailId) {
    const url = `${this.baseUrl}/preview-cache/invalidate/${emailId}`;
    return await this.request(url);
  }

  /**
   * Invalidate all preview caches
   * @returns {Promise<Object>} Success message
   */
  async invalidateAllPreviews() {
    const url = `${this.baseUrl}/preview-cache/invalidate-all`;
    return await this.request(url);
  }

  // =============================================================================
  // Rate Limiting
  // =============================================================================

  /**
   * Get rate limit status
   * @returns {Promise<Object>} Rate limit status
   */
  async getRateLimitStatus() {
    const url = `${this.baseUrl}/rate-limit`;
    return await this.request(url);
  }

  // =============================================================================
  // Health Check
  // =============================================================================

  /**
   * Health check
   * @returns {Promise<Object>} Health status
   */
  async healthCheck() {
    const url = `${this.baseUrl}/health`;
    return await this.request(url);
  }
}

// Export singleton instance
export const gmailApi = new GmailApiClient();
export default gmailApi;
