# Feature Specification: Gmail Email Search & CV Extraction

**Feature Branch**: `004-gmail-email-search`
**Created**: 2025-11-03
**Status**: Draft
**Input**: User description: "email analysis - we need a system to be able to search through all emails in a given gmail acoount in a given date range, and ultimately to open and read attached documents such as CVs"

## Clarifications

### Session 2025-11-03

- Q: Downloaded CV File Lifecycle - What is the retention policy for downloaded CV attachments stored on the server? → A: Files automatically deleted after 24 hours
- Q: Multi-User Access Model - Can multiple recruiters share access to a single Gmail account, or does each recruiter connect their own? → A: Each recruiter connects their own personal Gmail account
- Q: CV Attachment Identification - How does the system distinguish CV attachments from other document attachments? → A: All PDF/DOC/DOCX attachments are treated as potential CVs

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Search Emails by Date Range (Priority: P1)

Recruiters need to search through their Gmail inbox to find emails within a specific date range. This is the foundation for all email analysis activities, allowing users to narrow down their search scope before looking for specific candidates or CVs.

**Why this priority**: Core functionality that must work before any other feature can be useful. Without date-based search, users would be overwhelmed by the volume of emails.

**Independent Test**: Can be fully tested by connecting a Gmail account, specifying a date range (e.g., "last 30 days"), and verifying that only emails within that range are returned. Delivers immediate value by helping users locate relevant email conversations.

**Acceptance Scenarios**:

1. **Given** a recruiter has connected their Gmail account, **When** they specify a date range of "Jan 1, 2025 to Jan 31, 2025", **Then** only emails received or sent within that date range are displayed
2. **Given** a recruiter searches with an invalid date range (end date before start date), **When** they submit the search, **Then** a clear error message is displayed prompting them to correct the date range
3. **Given** a recruiter searches a date range with no emails, **When** the search completes, **Then** a message indicates "No emails found in this date range" with helpful suggestions
4. **Given** a recruiter has thousands of emails in a date range, **When** they perform the search, **Then** results are displayed within 5 seconds with pagination or lazy loading for large result sets

---

### User Story 2 - View and Extract CV Attachments (Priority: P2)

Recruiters need to identify emails containing CV attachments and be able to view or download those CVs directly from the search results. This is the primary value proposition - quickly accessing candidate CVs that were received via email.

**Why this priority**: This is the main business value. Without attachment extraction, the feature only provides basic email search which Gmail already offers. This differentiates the solution by focusing on recruitment needs.

**Independent Test**: Can be tested by searching emails that contain CV attachments (PDF, DOC, DOCX files), verifying that attachments are clearly indicated in results, and confirming that clicking an attachment opens or downloads it. Delivers value by eliminating manual email browsing.

**Acceptance Scenarios**:

1. **Given** search results contain emails with attachments, **When** a recruiter views the results, **Then** emails with attachments are clearly indicated with an attachment icon and count
2. **Given** a recruiter clicks on a CV attachment (PDF or DOC format), **When** the action completes, **Then** the CV is either displayed in a preview pane or downloaded to their device
3. **Given** an email contains multiple attachments including a CV, **When** the recruiter views the email, **Then** all attachments are listed with clear filenames and file types
4. **Given** a recruiter wants to extract all CVs from search results, **When** they select multiple emails with CV attachments, **Then** they can bulk download all CV files in a single action
5. **Given** an attachment fails to download (network error, file corruption), **When** the error occurs, **Then** a clear error message is displayed with retry options

---

### User Story 3 - Advanced Email Filtering (Priority: P3)

Recruiters need to refine their email search beyond date ranges by filtering on sender email address, subject line keywords, and email body content. This helps them quickly locate specific candidate emails or job application threads.

**Why this priority**: Enhances the core search functionality but is not essential for MVP. Users can still find CVs with just date range search, but filtering makes the process more efficient.

**Independent Test**: Can be tested by applying various filters (sender contains "@example.com", subject contains "Application", body contains "Java Developer") and verifying results match all criteria. Delivers value by reducing manual scanning of search results.

**Acceptance Scenarios**:

1. **Given** a recruiter wants to find emails from a specific candidate, **When** they filter by sender email address "candidate@example.com", **Then** only emails from that sender within the date range are displayed
2. **Given** a recruiter wants to find job application emails, **When** they filter by subject containing "Application" or "Resume", **Then** only emails matching those subject keywords are displayed
3. **Given** a recruiter wants to combine filters, **When** they specify date range AND sender AND subject keywords, **Then** only emails matching ALL criteria are displayed
4. **Given** a recruiter's filters return no results, **When** the search completes, **Then** a message suggests relaxing some filter criteria

---

### User Story 4 - Email Preview and Metadata Display (Priority: P4)

Recruiters need to quickly scan through email content without opening each email individually. Displaying email metadata (sender, recipient, date, subject) and a preview of the email body helps them identify relevant emails faster.

**Why this priority**: Nice-to-have feature that improves user experience but is not critical for core functionality. Users can still click into emails to read them.

**Independent Test**: Can be tested by viewing search results and verifying that each email displays sender, subject, date, and a snippet of the body text. Delivers value by speeding up email triage.

**Acceptance Scenarios**:

1. **Given** search results contain emails, **When** a recruiter views the results list, **Then** each email displays sender name/email, subject line, date received, and first 2-3 lines of body text
2. **Given** a recruiter clicks on an email in the results, **When** the email opens, **Then** the full email body is displayed along with all metadata and attachments
3. **Given** an email contains HTML formatting or images, **When** displayed in preview, **Then** the content is rendered appropriately without breaking the layout

---

### Edge Cases

- **Large Volume**: What happens when a date range contains 10,000+ emails? System should paginate results, display a count, and maintain performance (results within 10 seconds for any query).

- **Attachment Size Limits**: What happens when a CV attachment is 50MB+ (unusually large file)? System should warn users about large files before download and set a reasonable size limit (e.g., 25MB per file).

- **Unsupported File Formats**: How does the system handle non-standard CV formats (e.g., .pages, .odt, .rtf)? System should indicate unsupported formats and suggest common formats (PDF, DOC, DOCX).

- **Gmail API Rate Limits**: What happens when Gmail API rate limits are exceeded during a large search? System should gracefully handle rate limiting with appropriate retry logic and user messaging.

- **Access Revoked**: What happens when a user revokes Gmail access permissions mid-session? System should detect revoked access and prompt user to re-authenticate.

- **Attachments Without Proper Extensions**: How does the system identify document attachments when the filename doesn't include standard extensions (e.g., "resume" without .pdf)? System should use MIME type detection (application/pdf, application/msword, application/vnd.openxmlformats-officedocument.wordprocessingml.document) to identify all PDF/DOC/DOCX files regardless of filename extension.

- **Email Threading**: How does the system handle email threads where multiple emails contain the same CV attachment? System should indicate duplicate attachments and allow users to view the attachment from any email in the thread.

- **International Characters**: What happens when email subjects or attachment filenames contain non-English characters (Chinese, Arabic, emoji)? System should properly display Unicode characters without corruption.

- **Expired Downloaded Files**: What happens when a user tries to access a previously downloaded CV after 24 hours? System should detect the expired file, remove it from temporary storage, and allow the user to re-download from Gmail if needed.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST authenticate each recruiter individually with their own personal Gmail account using OAuth 2.0 authorization (no shared account access)
- **FR-002**: System MUST allow users to specify a date range with start date and end date for email search
- **FR-003**: System MUST retrieve all emails within the specified date range from the connected Gmail account
- **FR-004**: System MUST display search results showing email sender, subject, date, and attachment indicator
- **FR-005**: System MUST identify emails containing attachments and treat all PDF, DOC, and DOCX attachments as potential CVs
- **FR-006**: System MUST support viewing and downloading all PDF, DOC, and DOCX attachments (treating all such files as potential CVs)
- **FR-007**: System MUST allow users to filter search results by sender email address
- **FR-008**: System MUST allow users to filter search results by subject line keywords
- **FR-009**: System MUST allow users to filter search results by email body content keywords
- **FR-010**: System MUST handle pagination for large result sets (more than 100 emails)
- **FR-011**: System MUST display attachment metadata including filename, file type, and file size
- **FR-012**: System MUST allow users to select multiple emails and bulk download all attachments
- **FR-013**: System MUST handle Gmail API rate limits gracefully with appropriate retry logic
- **FR-014**: System MUST persist Gmail access tokens securely and refresh them when expired
- **FR-015**: System MUST validate date range inputs and display clear error messages for invalid ranges
- **FR-016**: System MUST handle network errors during email retrieval with appropriate user messaging and retry options
- **FR-017**: System MUST detect and handle attachment files that exceed 25MB, displaying a warning message to users before allowing download of larger files
- **FR-018**: System MUST allow users to preview email body content without downloading attachments
- **FR-019**: System MUST indicate when attachments cannot be previewed or downloaded due to format or access restrictions
- **FR-020**: System MUST automatically delete downloaded CV attachments from temporary storage after 24 hours to minimize data retention and comply with GDPR principles

### Key Entities

- **Email Message**: Represents an email in the Gmail account with attributes including unique message ID, sender email address, recipient email addresses, subject line, date received/sent, body content (plain text and HTML), and list of attachments.

- **Attachment**: Represents a file attached to an email with attributes including filename, file type/MIME type, file size in bytes, content/download URL, and download timestamp for automatic cleanup after 24 hours. All PDF, DOC, and DOCX attachments are treated as potential CVs. Related to the parent Email Message.

- **Search Query**: Represents the user's search criteria including date range (start date, end date), sender filter (email address or domain), subject filter (keywords), body filter (keywords), and pagination settings (page number, results per page).

- **Search Result Set**: Collection of Email Messages matching the Search Query, including total count, current page, and metadata about the search (query execution time, whether results were truncated).

- **User Session**: Represents an individual recruiter's authenticated connection to their personal Gmail account, including OAuth tokens (access token, refresh token), token expiration times, recruiter identifier, and associated Gmail account identifier. Each recruiter maintains their own independent session.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete Gmail account connection and authorization in under 1 minute
- **SC-002**: Email search results for any date range are returned and displayed within 5 seconds
- **SC-003**: Users can identify and access a CV attachment within 3 clicks from the search interface
- **SC-004**: System successfully handles searches across 10,000+ emails without performance degradation
- **SC-005**: 95% of CV attachments in common formats (PDF, DOC, DOCX) are successfully extractable and viewable
- **SC-006**: Users can filter search results to reduce result count by at least 70% when applying sender or subject filters
- **SC-007**: System maintains stable performance under Gmail API rate limits, completing searches even when limits are encountered (with appropriate delays)
- **SC-008**: Zero user data is exposed due to authentication or authorization failures
- **SC-009**: Users can successfully complete bulk download of 50+ CV attachments in under 30 seconds

## Assumptions

- Each recruiter has their own personal Gmail account (no shared team accounts)
- Gmail account users have enabled IMAP access or granted appropriate API permissions
- All PDF, DOC, and DOCX attachments in recruitment emails are treated as potential CVs (no filename-based filtering required)
- Users have stable internet connection during email search and download operations
- Gmail API quota limits are sufficient for expected usage patterns (typically 250 quota units per user per second for Gmail API)
- Users understand that only emails accessible via their Gmail account will be searchable (no access to emails in other accounts or deleted emails beyond Gmail's retention period)
- CV attachments are typically under 10MB in size, with occasional larger files up to 25MB
- Users have modern web browsers supporting OAuth 2.0 and secure token storage

## Dependencies

- **Gmail API Access**: Requires active Google Cloud project with Gmail API enabled and OAuth 2.0 credentials configured
- **OAuth 2.0 Infrastructure**: Requires secure token storage and refresh mechanism
- **File Storage**: Requires temporary storage for downloaded attachments before presenting to user
- **Existing Authentication System**: May need to integrate with ProActive People's existing user authentication if this feature is part of the main platform

## Scope

### In Scope

- Gmail account authentication and authorization
- Email search by date range
- Email filtering by sender, subject, and body keywords
- Attachment detection and metadata display
- Attachment download and preview for common CV formats (PDF, DOC, DOCX)
- Bulk attachment download
- Handling of Gmail API rate limits and errors
- Pagination for large result sets

### Out of Scope

- Email composition or sending capabilities
- Email deletion or modification
- Support for email providers other than Gmail (Outlook, Yahoo, etc.)
- Advanced CV parsing or content extraction (text recognition, skill extraction)
- Integration with ATS (Bullhorn) for automatic candidate creation
- Automated CV categorization or candidate matching
- Email labeling or organization features
- Calendar integration or meeting scheduling
- Real-time email monitoring or notifications
- Blocking downloads of attachments larger than 25MB (warnings will be shown, but download is still permitted)

## Security & Privacy Considerations

- **OAuth 2.0 Security**: All Gmail access must use OAuth 2.0 with secure token storage. Each recruiter authenticates individually with their own Gmail account to ensure clear audit trails and comply with Google's OAuth policies. Never store user passwords.
- **Token Encryption**: Access tokens and refresh tokens must be encrypted at rest
- **Minimal Scope Request**: Only request Gmail API scopes necessary for email reading and attachment access
- **User Consent**: Clearly inform users what data will be accessed and why before requesting Gmail authorization
- **Data Retention**: Downloaded CV attachments are automatically deleted from temporary storage after 24 hours to minimize data retention and comply with GDPR data minimization principles. Users retain the right to immediate deletion upon request.
- **Audit Logging**: Log all Gmail API access and attachment downloads for security audit purposes
- **Session Management**: Implement secure session handling with automatic timeout for inactive users
- **Error Handling**: Never expose sensitive error details (API keys, tokens, internal paths) to users
