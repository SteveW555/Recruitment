# Gmail Email Search Frontend

React-based frontend for the Gmail Email Search & CV Extraction service.

## Features

- **Email Search (US1)**: Search emails by date range, sender, subject, and attachments
- **Email Preview (US4)**: Full email content with sanitized HTML rendering
- **Attachment Downloads (US2)**: Individual and bulk download capabilities
- **CV Detection**: Automatic identification of CV-related emails
- **Responsive Design**: Works on desktop, tablet, and mobile

## Components

### Core Components

1. **GmailApp** - Main application component
2. **EmailSearch** - Search form with filters
3. **EmailList** - Results display with CV highlighting
4. **EmailPreview** - Full email content with attachments

### API Client

- **gmail-api-client.js** - Comprehensive API service
  - Email search and filtering
  - Email preview and content
  - Attachment management
  - Cache management

## Quick Start

### 1. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```
VITE_API_BASE_URL=http://localhost:8080/api/v1
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Run Development Server

```bash
npm run dev
```

Or use the Gmail-specific entry point:
```bash
npm run dev -- gmail-index.jsx
```

### 4. Build for Production

```bash
npm run build
```

## Usage

### Basic Email Search

1. Enter date range (optional)
2. Add sender email filter (optional)
3. Enter subject keywords (optional)
4. Check "Has Attachments" for CV emails
5. Click "Search Emails"

### Viewing Email Content

1. Click any email in the results list
2. View full content in the preview pane
3. Toggle between HTML and plain text view
4. Download attachments individually or in bulk

### CV Email Detection

- Emails containing CVs are automatically tagged with a green "CV" badge
- Filter by attachments to find CV emails quickly

## API Integration

The frontend connects to the backend Gmail service at:
- **Base URL**: `http://localhost:8080/api/v1/gmail`
- **Advanced Search**: `http://localhost:8080/api/v1/gmail/advanced`
- **Attachments**: `http://localhost:8080/api/v1/attachments`

### Authentication

The app uses session-based authentication with cookies. Users must:
1. Authenticate via OAuth 2.0 (Google)
2. Session cookies are automatically included in requests

## Component Architecture

```
src/
├── components/
│   ├── GmailApp.jsx          # Main application
│   ├── EmailSearch.jsx       # Search form
│   ├── EmailList.jsx         # Results list
│   └── EmailPreview.jsx      # Email preview
├── lib/
│   └── gmail-api-client.js   # API service
└── types/                     # TypeScript types (future)
```

## Styling

- **Framework**: Tailwind CSS
- **Icons**: Lucide React
- **Theme**: Professional blue and gray palette
- **Responsive**: Mobile-first design

## Performance Optimizations

1. **Caching**: Preview caching reduces API calls
2. **Lazy Loading**: Email content loaded on demand
3. **Pagination**: Results pagination for large searches
4. **Debouncing**: Search input debouncing (future enhancement)

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Security Features

1. **HTML Sanitization**: All email HTML is sanitized server-side
2. **XSS Protection**: Content Security Policy headers
3. **Session Security**: HTTP-only cookies
4. **CSRF Protection**: CSRF tokens on all mutations

## Development

### Adding New Features

1. Create component in `src/components/`
2. Add API methods to `gmail-api-client.js`
3. Import and use in `GmailApp.jsx`
4. Test with backend service

### Code Style

- Use functional components with hooks
- Follow React best practices
- Keep components under 300 lines
- Extract reusable logic to custom hooks

## Troubleshooting

### Backend Connection Failed

```
Error: Failed to fetch
```

**Solution**: Ensure backend is running on port 8080 and CORS is enabled.

### Authentication Error

```
Error: Unauthorized
```

**Solution**: User needs to authenticate via OAuth. Redirect to `/auth/google`.

### Preview Not Loading

```
Error: Failed to load email preview
```

**Solution**: Check that Gmail API credentials are valid and user has granted permissions.

## Future Enhancements

- [ ] Advanced filtering UI (US3)
- [ ] Saved searches management
- [ ] Filter suggestions
- [ ] Keyboard shortcuts
- [ ] Dark mode
- [ ] Email threading view
- [ ] Search history
- [ ] Export results to CSV

## Support

For issues or questions:
- Backend API: `D:\Recruitment\backend\services\gmail-service\`
- Frontend: `D:\Recruitment\frontend\`
- Documentation: `docs_root/specs/004-gmail-email-search/`
