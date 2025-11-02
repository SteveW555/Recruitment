---
name: ui
description: Expert frontend UI specialist with comprehensive knowledge of all interface elements, components, and styling in the EasyGeo3B project. This skill should be used when working with any UI elements, modifying styles, finding interface components, debugging UI issues, or implementing new frontend features. Specializes in vanilla JavaScript, Bootstrap 5, Google Maps integration, Chart.js visualizations, Three.js 3D graphics, and selective React components. (project, gitignored)
---

# Frontend UI Expert Skill

Expert in all aspects of frontend development for the ProActive People Recruitment System, with comprehensive knowledge of all UI elements, components, pages, and technical patterns.

## Purpose

Provide specialized expertise for all frontend development tasks including:
- Understanding and navigating the current UI codebase
- Implementing new UI features and components
- Debugging UI issues and performance problems
- Refactoring and improving component architecture
- Integrating UI libraries and design systems
- Implementing responsive layouts and accessibility features

## When to Use This Skill

Use this skill proactively when:
- Working with any React components or pages
- Modifying styles, layouts, or visual elements
- Debugging frontend issues (rendering, state, API integration)
- Implementing new UI features or components
- Questions about component structure or UI patterns
- Improving frontend architecture or performance
- Integrating new UI libraries or tools
- Accessibility or responsive design tasks

## Current Frontend Architecture

### Technology Stack

**Core Framework:**
- React 18.2.0 (no TypeScript - plain JSX)
- Vite 5.0.8 (build tool with fast HMR)
- React 18 features enabled

**Styling:**
- Tailwind CSS 3.4.0
- @tailwindcss/typography for markdown prose
- Custom utility patterns
- No CSS modules, styled-components, or CSS-in-JS

**UI Libraries:**
- Lucide React 0.292.0 (icons only)
- react-markdown 9.0.1 + remark-gfm 4.0.0
- NO component library (no shadcn, MUI, Radix, etc.)

**State Management:**
- React hooks only (useState, useRef, useEffect)
- No Redux, Zustand, or other state management libraries

**API Integration:**
- Native Fetch API (no Axios)
- Vite proxy for backend communication
- No React Query, SWR, or data fetching libraries

### File Structure

```
frontend/
├── index.html          # Entry point
├── index.jsx           # React root (10 lines)
├── dashboard.jsx       # ENTIRE APP (756 lines) ⚠️
├── index.css           # Tailwind imports + global styles
├── package.json
├── vite.config.js      # Vite + proxy config
├── tailwind.config.js
├── postcss.config.js
└── public/
    └── elephant-logo-black.svg
```

**Critical Note**: The entire application is in ONE file (`dashboard.jsx` - 756 lines). All components are inline, no component decomposition exists.

### Application Pages

**Page Navigation**: State-based (no React Router)

1. **Dashboard** (`activePage === 'dashboard'`)
   - AI Chat Interface with markdown rendering
   - Workflow Categories Sidebar (4 categories)
   - Connected Sources Panel (5 data sources)
   - System Console Panel

2. **Analytics** (`activePage === 'analytics'`)
   - Metrics Overview (4 cards)
   - Workflow Usage Charts (static progress bars)
   - Data Source Usage (static progress bars)
   - ROI Metrics Display

### Key UI Components

All components are inline in [dashboard.jsx](frontend/dashboard.jsx). Key sections:

**Header** (lines 303-339)
- Logo and branding
- Navigation buttons (Dashboard, Analytics, Account, Support)
- Notifications bell
- Menu button

**Connected Sources Panel** (lines 344-374)
- 5 data source cards (Supabase, Salesforce, Mailchimp, Bullhorn, SQL)
- Grid layout with icons and status
- "Add New Source" button

**Workflows Sidebar** (lines 379-438)
- 4 expandable categories: Lookup, Problem Solve, Report, Automation
- Role-based query examples (5 roles: Managing Director, Sales, Recruiter, Admin, HR)
- 3-4 example queries per category
- "Add custom query" and "Add Workflow" buttons

**AI Chat Interface** (lines 442-568)
- Role selector dropdown (5 roles)
- Message list (user messages left-aligned blue, AI messages right-aligned gray)
- Markdown rendering for AI responses
- Metadata display (graph analysis, SQL queries)
- Copy-to-clipboard for SQL
- Input field with attachment button
- Send button with loading state
- Enter key support

**System Console Panel** (lines 571-604)
- Terminal-style logging
- Log levels: INFO, SUCCESS, WARN, ERROR
- Color-coded messages
- Timestamps
- Clear button
- Auto-scroll

**Analytics Components** (lines 610-752)
- 4 metric cards with percentage changes
- Static progress bars (no actual chart library)
- Hard-coded data (no API integration)

### State Management

Current state variables in dashboard.jsx:

```javascript
const [activePage, setActivePage] = useState('dashboard')
const [messages, setMessages] = useState([...])
const [inputMessage, setInputMessage] = useState('')
const [expandedCategory, setExpandedCategory] = useState(null)
const [selectedRole, setSelectedRole] = useState('Recruiter')
const [isSending, setIsSending] = useState(false)
const [consoleLogs, setConsoleLogs] = useState([...])
```

Refs for auto-scrolling:
```javascript
const messagesEndRef = useRef(null)
const consoleEndRef = useRef(null)
```

### API Integration

**Backend Communication:**
- Single endpoint: `POST /api/chat`
- Proxied through Vite to `http://localhost:3002`
- Request payload: `{ message, sessionId, useHistory, agent }`
- Response format: `{ response, metadata, graph_analysis }`

**Error Handling:**
- Try-catch blocks
- Error state in messages array
- Console logging
- User-facing error messages

### Styling Patterns

**Common Tailwind Classes:**
- Layout: `flex`, `grid`, `gap-4`, `space-y-4`, `max-w-7xl`
- Colors: `bg-blue-500`, `text-gray-600`, `border-gray-200`
- Spacing: `p-4`, `px-6`, `py-3`, `m-4`
- Effects: `rounded-lg`, `shadow-lg`, `hover:bg-blue-600`, `transition-colors`
- Gradients: `bg-gradient-to-br from-gray-100 to-gray-200`

**Color Palette:**
- Primary: Blue (`bg-blue-500`, `text-blue-600`)
- Success: Green (`bg-green-400`, `text-green-600`)
- Warning: Yellow (`bg-yellow-100`, `text-yellow-600`)
- Error: Red (`bg-red-50`, `text-red-600`)
- Info: Gray (`bg-gray-100`, `text-gray-600`)
- Purple: Automation category
- Cyan: Salesforce branding

### Icons Used (Lucide React)

16 unique icons throughout the app:
- Search, Bell, ChevronDown, Send, Paperclip
- Calendar, ChevronRight, Plus, Mail
- FolderOpen, Briefcase, FileSpreadsheet, Monitor
- Lightbulb, TrendingUp, Zap, Menu

### Role-Based Workflows

5 user roles with custom workflow examples:

1. **Managing Director**
2. **Sales** (Business Development, Telesales)
3. **Recruiter**
4. **Admin and Resources** (Admin, Resources, Tech Support)
5. **HR** (Compliance, Wellbeing)

Each role has 4 categories × 3-4 examples = 12-16 workflow queries

### Special Features

**Query Classification** (frontend, lines 120-157):
- Client-side regex-based classification
- 6 categories: general-chat, information-retrieval, problem-solving, automation, report-generation, industry-knowledge
- Pre-classification before sending to backend

**Markdown Rendering**:
- `react-markdown` with `remark-gfm`
- GitHub Flavored Markdown support
- Prose styling via `@tailwindcss/typography`

**Metadata Display**:
- Graph analysis rendering
- SQL query display with copy-to-clipboard
- Visualization recommendations

**Auto-scroll**:
- Messages and console auto-scroll on new content
- `scrollIntoView({ behavior: 'smooth' })`

## How to Use This Skill

### 1. Understanding the Codebase

To understand the current UI implementation, refer to:
- **[references/ui-catalog.md](references/ui-catalog.md)** - Complete catalog of all UI elements (comprehensive 880-line reference)
- **[references/component-patterns.md](references/component-patterns.md)** - Common patterns and code examples
- **[references/improvement-roadmap.md](references/improvement-roadmap.md)** - Step-by-step refactoring guide

### 2. Finding UI Elements

**Main file**: [dashboard.jsx](frontend/dashboard.jsx) (756 lines)

**Quick navigation by line numbers:**
- Header: 303-339
- Connected Sources: 344-374
- Workflows Sidebar: 379-438
- Chat Interface: 442-568
- Console Panel: 571-604
- Analytics: 610-752
- Query Classification: 120-157

### 3. Implementing New Features

When adding new UI features:

1. **Read the current implementation** in dashboard.jsx
2. **Check references** for patterns and best practices
3. **Consider component extraction** (see improvement-roadmap.md)
4. **Use Tailwind CSS** for styling (match existing patterns)
5. **Add to appropriate section** or create new state-based page
6. **Update state management** if needed (useState hooks)
7. **Test with backend** using `/api/chat` endpoint

### 4. Common Tasks

#### Adding a New Page
```javascript
// Add state
const [activePage, setActivePage] = useState('dashboard')

// Add navigation button in header
<button onClick={() => setActivePage('newpage')}>New Page</button>

// Add conditional rendering
{activePage === 'newpage' && (
  <div className="p-6">
    {/* New page content */}
  </div>
)}
```

#### Adding a New Component (inline)
```javascript
// Extract inline component pattern
const MyComponent = ({ prop1, prop2 }) => (
  <div className="bg-white rounded-lg shadow-lg p-4">
    {/* Component content */}
  </div>
)
```

#### Adding API Call
```javascript
const fetchData = async () => {
  try {
    const response = await fetch('/api/endpoint', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data })
    })
    const result = await response.json()
    // Handle result
  } catch (error) {
    console.error('Error:', error)
    // Handle error
  }
}
```

#### Using Lucide Icons
```javascript
import { IconName } from 'lucide-react'

<IconName className="w-5 h-5 text-blue-500" />
```

### 5. Refactoring and Improvement

For refactoring the monolithic dashboard.jsx, follow the structured roadmap in [references/improvement-roadmap.md](references/improvement-roadmap.md).

**Priority order:**
1. Component extraction (Week 1)
2. Add React Router (Week 1)
3. Add state management - Zustand (Week 2)
4. Add TanStack Query (Week 2)
5. Add component library - shadcn/ui (Week 3)
6. TypeScript migration (Week 4)
7. Testing infrastructure (Week 4)

### 6. Debugging UI Issues

**Common issues and solutions:**

**State not updating:**
- Check useState setter calls
- Verify re-render triggers
- Check for stale closures

**API calls failing:**
- Check Vite proxy config in vite.config.js
- Verify backend is running on port 3002
- Check network tab in DevTools

**Styling issues:**
- Verify Tailwind classes are valid
- Check tailwind.config.js content paths
- Run `npm run dev` to rebuild

**Auto-scroll not working:**
- Check messagesEndRef/consoleEndRef
- Verify useEffect dependencies
- Check scrollIntoView browser support

### 7. Performance Optimization

**Current limitations:**
- No code splitting
- No React.memo optimization
- No virtual scrolling
- All data loaded upfront

**Quick optimizations:**
- Add React.memo for expensive components
- Implement lazy loading for pages
- Add useMemo for computed values
- Add useCallback for event handlers

### 8. Accessibility Improvements

**Current issues:**
- Missing aria-labels on icon buttons
- No keyboard navigation indicators
- Limited screen reader support

**Recommended fixes:**
- Add aria-label to all icon-only buttons
- Implement focus management
- Add keyboard shortcuts
- Use semantic HTML
- Test with screen readers

## Bundled Resources

### References Directory

**[references/ui-catalog.md](references/ui-catalog.md)**
Complete 880-line catalog of all UI elements, components, dependencies, and architecture. Use this when you need comprehensive information about:
- All components and their line numbers
- Complete dependency list
- Technology stack details
- Gap analysis and missing features

**[references/component-patterns.md](references/component-patterns.md)**
Common UI patterns and code examples for:
- Component extraction templates
- State management patterns
- API integration examples
- Styling patterns
- Form handling
- Error handling

**[references/improvement-roadmap.md](references/improvement-roadmap.md)**
Step-by-step guide for refactoring and improving the frontend:
- Week-by-week implementation plan
- Component extraction strategy
- Library integration guides
- Migration paths (TypeScript, testing)
- Architecture improvements

### Scripts Directory

**[scripts/extract-component.js](scripts/extract-component.js)**
Node.js script to automatically extract inline components from dashboard.jsx into separate files.

Usage:
```bash
node .claude/skills/ui/scripts/extract-component.js <component-name> <start-line> <end-line>
```

### Assets Directory

**[assets/component-templates/](assets/component-templates/)**
Reusable component templates matching project patterns:
- Button.jsx
- Card.jsx
- Select.jsx
- Modal.jsx
- Input.jsx

## Development Commands

```bash
# Start development server
cd frontend
npm start        # or npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

**Dev server**: http://localhost:3000
**Backend proxy**: http://localhost:3002 (configured in vite.config.js)

## Key Constraints

**What's NOT available:**
- ❌ TypeScript (all files are .jsx)
- ❌ React Router (state-based navigation only)
- ❌ Component library (no shadcn, MUI, etc.)
- ❌ State management library (useState only)
- ❌ Form library (manual form handling)
- ❌ Chart library (static progress bars only)
- ❌ Testing infrastructure (no tests)
- ❌ Mobile app (no React Native)

**What IS available:**
- ✅ React 18 with hooks
- ✅ Vite for fast development
- ✅ Tailwind CSS for styling
- ✅ Lucide icons
- ✅ Markdown rendering
- ✅ Fetch API for backend calls

## Best Practices

1. **Match existing patterns** - Keep consistency with current codebase
2. **Use Tailwind utilities** - Avoid custom CSS unless necessary
3. **Follow inline component pattern** - Until refactoring is complete
4. **Add console logging** - Use the console panel for debugging
5. **Handle errors gracefully** - Show user-friendly messages
6. **Update state immutably** - Use spread operators for arrays/objects
7. **Test with backend** - Ensure API integration works
8. **Consider accessibility** - Add aria-labels and keyboard support

## Critical Notes

⚠️ **The entire app is in one 756-line file** - Component extraction is the highest priority improvement.

⚠️ **No TypeScript** - Be careful with prop types and API contracts.

⚠️ **No formal routing** - Use state-based navigation pattern.

⚠️ **Limited testing** - Manual testing is required for all changes.

⚠️ **Static analytics** - Charts are fake progress bars with hard-coded data.

## Getting Help

When encountering issues:
1. Read [references/ui-catalog.md](references/ui-catalog.md) for comprehensive details
2. Check [references/component-patterns.md](references/component-patterns.md) for code examples
3. Review [dashboard.jsx](frontend/dashboard.jsx) source code with line numbers above
4. Check browser console and network tab
5. Verify backend is running and accessible
6. Test API endpoints with curl or Postman

## Future Improvements

See [references/improvement-roadmap.md](references/improvement-roadmap.md) for detailed implementation plan.

**Phase 1** (Weeks 1-2): Component extraction, routing, state management
**Phase 2** (Weeks 3-4): Component library, TypeScript, testing
**Phase 3** (Weeks 5-8): Advanced features, mobile app, design system
