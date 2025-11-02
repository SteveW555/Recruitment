# Frontend Improvement Roadmap

Systematic guide for refactoring and improving the ProActive People frontend from a 756-line monolithic component to a modern, scalable architecture.

## Overview

**Current State**: Single-file React app (dashboard.jsx - 756 lines)
**Target State**: Modular component architecture with modern tooling
**Timeline**: 4 weeks for core improvements, 8 weeks for complete transformation

---

## Phase 1: Foundation (Weeks 1-2)

### Week 1: Component Extraction & Routing

#### Day 1-2: Component Extraction Setup

**Goal**: Create component directory structure

```bash
# Create directory structure
mkdir -p frontend/src/{components,pages,hooks,utils,stores,api,schemas}
mkdir -p frontend/src/components/{layout,chat,workflows,analytics,common}
```

**Directory structure**:
```
frontend/src/
├── components/          # Reusable UI components
│   ├── layout/         # Header, Sidebar, Console
│   ├── chat/           # Chat interface components
│   ├── workflows/      # Workflow categories
│   ├── analytics/      # Analytics components
│   └── common/         # Buttons, Cards, Inputs
├── pages/              # Page-level components
│   ├── Dashboard.jsx
│   └── Analytics.jsx
├── hooks/              # Custom React hooks
│   ├── useChat.js
│   └── useConsole.js
├── utils/              # Utility functions
│   ├── queryClassifier.js
│   └── api.js
├── stores/             # State management (Zustand)
├── api/                # API client functions
└── schemas/            # Validation schemas (Zod)
```

#### Day 3-4: Extract Common Components

**Extract Button Component**:
```javascript
// frontend/src/components/common/Button.jsx
export const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  icon: Icon,
  disabled,
  onClick,
  type = 'button',
  className = '',
  ...props
}) => {
  const baseStyles = 'rounded-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed'

  const variants = {
    primary: 'bg-blue-500 text-white hover:bg-blue-600',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300',
    ghost: 'bg-transparent text-gray-600 hover:bg-gray-100',
    danger: 'bg-red-500 text-white hover:bg-red-600'
  }

  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-6 py-2',
    lg: 'px-8 py-3 text-lg'
  }

  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
      {...props}
    >
      {Icon && <Icon className="w-4 h-4" />}
      {children}
    </button>
  )
}

// Usage
import { Button } from '../components/common/Button'
import { Send } from 'lucide-react'

<Button variant="primary" icon={Send} onClick={handleSend}>
  Send Message
</Button>
```

**Extract Card Component**:
```javascript
// frontend/src/components/common/Card.jsx
export const Card = ({ children, className = '', ...props }) => (
  <div
    className={`bg-white rounded-lg shadow-lg ${className}`}
    {...props}
  >
    {children}
  </div>
)

export const CardHeader = ({ children, className = '' }) => (
  <div className={`p-6 border-b border-gray-200 ${className}`}>
    {children}
  </div>
)

export const CardBody = ({ children, className = '' }) => (
  <div className={`p-6 ${className}`}>
    {children}
  </div>
)

export const CardFooter = ({ children, className = '' }) => (
  <div className={`p-6 border-t border-gray-200 ${className}`}>
    {children}
  </div>
)

// Usage
import { Card, CardHeader, CardBody } from '../components/common/Card'

<Card>
  <CardHeader>
    <h3 className="text-lg font-semibold">Title</h3>
  </CardHeader>
  <CardBody>
    Content here
  </CardBody>
</Card>
```

**Extract Select Component**:
```javascript
// frontend/src/components/common/Select.jsx
export const Select = ({
  value,
  onChange,
  options,
  label,
  className = '',
  ...props
}) => (
  <div className={className}>
    {label && (
      <label className="block text-sm font-medium text-gray-700 mb-2">
        {label}
      </label>
    )}
    <select
      value={value}
      onChange={onChange}
      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
      {...props}
    >
      {options.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  </div>
)

// Usage
<Select
  label="Select Role"
  value={selectedRole}
  onChange={(e) => setSelectedRole(e.target.value)}
  options={[
    { value: 'Managing Director', label: 'Managing Director' },
    { value: 'Sales', label: 'Sales' },
    { value: 'Recruiter', label: 'Recruiter' }
  ]}
/>
```

#### Day 5: Extract Chat Components

Follow the patterns in [component-patterns.md](./component-patterns.md) to extract:
- `ChatInterface.jsx`
- `ChatHeader.jsx`
- `MessageList.jsx`
- `Message.jsx`
- `ChatInput.jsx`
- `MessageMetadata.jsx`

**Checklist**:
- [ ] Create component files
- [ ] Move inline JSX to components
- [ ] Pass props from parent
- [ ] Test each component independently
- [ ] Verify no broken functionality

#### Day 6-7: Add React Router

**Install dependencies**:
```bash
npm install react-router-dom
```

**Create router configuration**:
```javascript
// frontend/src/App.jsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from './components/layout/Layout'
import { Dashboard } from './pages/Dashboard'
import { Analytics } from './pages/Analytics'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
```

**Create Layout component**:
```javascript
// frontend/src/components/layout/Layout.jsx
import { Outlet } from 'react-router-dom'
import { Header } from './Header'
import { Console } from './Console'

export const Layout = () => (
  <div className="flex flex-col h-screen">
    <Header />
    <main className="flex-1 overflow-hidden">
      <Outlet />
    </main>
    <Console />
  </div>
)
```

**Update Header navigation**:
```javascript
// frontend/src/components/layout/Header.jsx
import { Link, useLocation } from 'react-router-dom'

export const Header = () => {
  const location = useLocation()

  const navItems = [
    { path: '/dashboard', label: 'Dashboard' },
    { path: '/analytics', label: 'Analytics' }
  ]

  return (
    <header className="bg-white shadow-sm">
      <nav className="flex gap-4">
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`px-4 py-2 rounded-lg ${
              location.pathname === item.path
                ? 'bg-blue-500 text-white'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            {item.label}
          </Link>
        ))}
      </nav>
    </header>
  )
}
```

**Checklist**:
- [ ] Install react-router-dom
- [ ] Create App.jsx with router
- [ ] Create Layout component
- [ ] Extract Header component
- [ ] Update navigation to use Link
- [ ] Test all routes work
- [ ] Remove state-based navigation

---

### Week 2: State Management & API Layer

#### Day 1-3: Add Zustand State Management

**Install dependencies**:
```bash
npm install zustand
```

**Create chat store**:
```javascript
// frontend/src/stores/chatStore.js
import { create } from 'zustand'
import { devtools } from 'zustand/middleware'

export const useChatStore = create(
  devtools(
    (set, get) => ({
      // State
      messages: [],
      inputMessage: '',
      selectedRole: 'Recruiter',
      isSending: false,

      // Actions
      setInputMessage: (message) => set({ inputMessage: message }),

      setSelectedRole: (role) => set({ selectedRole: role }),

      addMessage: (message) =>
        set((state) => ({
          messages: [
            ...state.messages,
            {
              ...message,
              timestamp: new Date().toLocaleTimeString()
            }
          ]
        })),

      sendMessage: async () => {
        const { inputMessage, selectedRole } = get()
        if (!inputMessage.trim()) return

        // Add user message
        set({ isSending: true })
        get().addMessage({
          role: 'user',
          text: inputMessage
        })
        set({ inputMessage: '' })

        try {
          const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              message: inputMessage,
              sessionId: 'elephant-session-1',
              useHistory: true
            })
          })

          const data = await response.json()

          get().addMessage({
            role: 'assistant',
            text: data.response,
            metadata: data.metadata
          })
        } catch (error) {
          get().addMessage({
            role: 'assistant',
            text: `Error: ${error.message}`,
            isError: true
          })
        } finally {
          set({ isSending: false })
        }
      },

      clearMessages: () => set({ messages: [] })
    }),
    { name: 'chat-store' }
  )
)
```

**Create console store**:
```javascript
// frontend/src/stores/consoleStore.js
import { create } from 'zustand'

export const useConsoleStore = create((set) => ({
  logs: [],

  addLog: (level, message) =>
    set((state) => ({
      logs: [
        ...state.logs,
        {
          level,
          message,
          timestamp: new Date().toLocaleTimeString()
        }
      ]
    })),

  clearLogs: () => set({ logs: [] })
}))
```

**Update components to use stores**:
```javascript
// Before (dashboard.jsx)
const [messages, setMessages] = useState([])
const [inputMessage, setInputMessage] = useState('')

// After (Dashboard.jsx)
import { useChatStore } from '../stores/chatStore'

function Dashboard() {
  const { messages, inputMessage, setInputMessage, sendMessage } = useChatStore()

  return <ChatInterface />
}
```

**Checklist**:
- [ ] Install Zustand
- [ ] Create chatStore.js
- [ ] Create consoleStore.js
- [ ] Update components to use stores
- [ ] Test state updates work
- [ ] Remove useState from components

#### Day 4-5: Add TanStack Query (React Query)

**Install dependencies**:
```bash
npm install @tanstack/react-query
```

**Setup query client**:
```javascript
// frontend/src/main.jsx or index.jsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000 // 5 minutes
    }
  }
})

root.render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  </React.StrictMode>
)
```

**Create API layer**:
```javascript
// frontend/src/api/chatApi.js
export const chatApi = {
  sendMessage: async ({ message, sessionId, agent }) => {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        sessionId,
        useHistory: true,
        agent
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  }
}
```

**Create custom hooks**:
```javascript
// frontend/src/hooks/useChat.js
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { chatApi } from '../api/chatApi'

export const useSendMessage = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: chatApi.sendMessage,
    onSuccess: () => {
      queryClient.invalidateQueries(['chatHistory'])
    }
  })
}
```

**Usage in component**:
```javascript
import { useSendMessage } from '../hooks/useChat'

function ChatInterface() {
  const sendMessage = useSendMessage()

  const handleSend = () => {
    sendMessage.mutate(
      { message: inputMessage, sessionId: 'session-1' },
      {
        onSuccess: (data) => {
          // Handle success
        },
        onError: (error) => {
          // Handle error
        }
      }
    )
  }

  return (
    <button onClick={handleSend} disabled={sendMessage.isPending}>
      {sendMessage.isPending ? 'Sending...' : 'Send'}
    </button>
  )
}
```

**Checklist**:
- [ ] Install @tanstack/react-query
- [ ] Setup QueryClientProvider
- [ ] Create api/chatApi.js
- [ ] Create hooks/useChat.js
- [ ] Update components to use mutation
- [ ] Test API calls work
- [ ] Add error handling

---

## Phase 2: Enhanced UI (Weeks 3-4)

### Week 3: Component Library & Styling

#### Day 1-2: Add shadcn/ui

**Install shadcn/ui**:
```bash
npx shadcn-ui@latest init
```

**Install specific components**:
```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add input
npx shadcn-ui@latest add select
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add toast
npx shadcn-ui@latest add dropdown-menu
```

**Replace custom components**:
```javascript
// Before
import { Button } from './components/common/Button'

// After
import { Button } from './components/ui/button'

<Button variant="default" size="lg">
  Click Me
</Button>
```

**Checklist**:
- [ ] Install shadcn/ui
- [ ] Add required components
- [ ] Replace custom Button with shadcn Button
- [ ] Replace custom Card with shadcn Card
- [ ] Update all component imports
- [ ] Test styling consistency

#### Day 3-4: Add Chart Library (Recharts)

**Install dependencies**:
```bash
npm install recharts
```

**Create chart components**:
```javascript
// frontend/src/components/analytics/WorkflowChart.jsx
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export const WorkflowChart = ({ data }) => (
  <ResponsiveContainer width="100%" height={300}>
    <BarChart data={data}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="name" />
      <YAxis />
      <Tooltip />
      <Bar dataKey="count" fill="#3b82f6" />
    </BarChart>
  </ResponsiveContainer>
)

// Usage
<WorkflowChart
  data={[
    { name: 'Lookup', count: 245 },
    { name: 'Problem Solve', count: 189 },
    { name: 'Report', count: 156 }
  ]}
/>
```

**Update Analytics page**:
```javascript
// frontend/src/pages/Analytics.jsx
import { WorkflowChart } from '../components/analytics/WorkflowChart'

export const Analytics = () => {
  // Fetch real data instead of static
  const { data: workflowData } = useQuery({
    queryKey: ['analytics', 'workflows'],
    queryFn: () => fetch('/api/analytics/workflows').then(res => res.json())
  })

  return (
    <div>
      <WorkflowChart data={workflowData} />
    </div>
  )
}
```

**Checklist**:
- [ ] Install Recharts
- [ ] Create WorkflowChart component
- [ ] Create DataSourceChart component
- [ ] Update Analytics page
- [ ] Remove static progress bars
- [ ] Fetch real data from API

#### Day 5-7: Accessibility Improvements

**Add ARIA labels**:
```javascript
// Before
<button onClick={handleClick}>
  <Bell className="w-5 h-5" />
</button>

// After
<button
  onClick={handleClick}
  aria-label="View notifications"
  aria-describedby="notification-count"
>
  <Bell className="w-5 h-5" />
  <span id="notification-count" className="sr-only">
    {notificationCount} unread notifications
  </span>
</button>
```

**Add keyboard shortcuts**:
```javascript
// frontend/src/hooks/useKeyboardShortcuts.js
import { useEffect } from 'react'

export const useKeyboardShortcuts = (shortcuts) => {
  useEffect(() => {
    const handleKeyPress = (e) => {
      const key = e.key.toLowerCase()
      const modifiers = {
        ctrl: e.ctrlKey,
        shift: e.shiftKey,
        alt: e.altKey
      }

      shortcuts.forEach((shortcut) => {
        const match =
          shortcut.key === key &&
          shortcut.ctrl === modifiers.ctrl &&
          (shortcut.shift === undefined || shortcut.shift === modifiers.shift)

        if (match) {
          e.preventDefault()
          shortcut.action()
        }
      })
    }

    window.addEventListener('keydown', handleKeyPress)
    return () => window.removeEventListener('keydown', handleKeyPress)
  }, [shortcuts])
}

// Usage
useKeyboardShortcuts([
  { key: '/', ctrl: true, action: () => focusChatInput() },
  { key: 'k', ctrl: true, action: () => openCommandPalette() },
  { key: 'escape', action: () => closeModal() }
])
```

**Checklist**:
- [ ] Add aria-labels to all icon buttons
- [ ] Implement keyboard shortcuts
- [ ] Add focus management
- [ ] Test with screen reader
- [ ] Check color contrast ratios
- [ ] Add skip-to-content link

---

### Week 4: TypeScript & Testing

#### Day 1-3: TypeScript Migration

**Install TypeScript**:
```bash
npm install --save-dev typescript @types/react @types/react-dom
```

**Create tsconfig.json**:
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

**Rename files**:
```bash
# Rename .jsx to .tsx, .js to .ts
mv frontend/src/App.jsx frontend/src/App.tsx
mv frontend/src/components/chat/ChatInterface.jsx frontend/src/components/chat/ChatInterface.tsx
# ... repeat for all files
```

**Add type definitions**:
```typescript
// frontend/src/types/chat.ts
export interface Message {
  role: 'user' | 'assistant'
  text: string
  timestamp: string
  metadata?: MessageMetadata
  isError?: boolean
}

export interface MessageMetadata {
  graph_analysis?: {
    sql_query: string
    visualization_recommendations: string[]
  }
}

export interface ChatState {
  messages: Message[]
  inputMessage: string
  selectedRole: string
  isSending: boolean
}

// Usage in store
import { Message, ChatState } from '../types/chat'

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  inputMessage: '',
  // ...
}))
```

**Checklist**:
- [ ] Install TypeScript
- [ ] Create tsconfig.json
- [ ] Rename files to .tsx/.ts
- [ ] Add type definitions
- [ ] Fix type errors
- [ ] Update imports

#### Day 4-5: Add Testing Infrastructure

**Install testing dependencies**:
```bash
npm install --save-dev vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
```

**Configure Vitest**:
```javascript
// vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts'
  }
})
```

**Create test setup**:
```typescript
// frontend/src/test/setup.ts
import { expect, afterEach } from 'vitest'
import { cleanup } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'

afterEach(() => {
  cleanup()
})
```

**Write component tests**:
```typescript
// frontend/src/components/common/Button.test.tsx
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Button } from './Button'

describe('Button', () => {
  it('renders with children', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  it('handles click events', async () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>Click me</Button>)

    await userEvent.click(screen.getByText('Click me'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Click me</Button>)
    expect(screen.getByText('Click me')).toBeDisabled()
  })
})
```

**Update package.json**:
```json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage"
  }
}
```

**Checklist**:
- [ ] Install Vitest and testing libraries
- [ ] Configure Vitest
- [ ] Create test setup file
- [ ] Write tests for common components
- [ ] Write tests for chat components
- [ ] Achieve >80% code coverage
- [ ] Add test script to CI/CD

---

## Phase 3: Advanced Features (Weeks 5-8)

### Week 5: Real-time Features

#### Add WebSocket Support

**Install dependencies**:
```bash
npm install socket.io-client
```

**Create WebSocket hook**:
```typescript
// frontend/src/hooks/useWebSocket.ts
import { useEffect, useRef } from 'react'
import { io, Socket } from 'socket.io-client'

export const useWebSocket = (url: string) => {
  const socketRef = useRef<Socket | null>(null)

  useEffect(() => {
    socketRef.current = io(url)

    socketRef.current.on('connect', () => {
      console.log('Connected to WebSocket')
    })

    socketRef.current.on('disconnect', () => {
      console.log('Disconnected from WebSocket')
    })

    return () => {
      socketRef.current?.disconnect()
    }
  }, [url])

  return socketRef.current
}

// Usage
const socket = useWebSocket('http://localhost:3002')

useEffect(() => {
  socket?.on('notification', (data) => {
    addNotification(data)
  })
}, [socket])
```

### Week 6: Advanced Data Visualization

#### Add Interactive Charts

**Install dependencies**:
```bash
npm install @tremor/react
```

**Create dashboard with Tremor**:
```typescript
// frontend/src/pages/Dashboard.tsx
import { Card, Title, BarChart } from '@tremor/react'

export const Dashboard = () => (
  <Card>
    <Title>Workflow Usage</Title>
    <BarChart
      data={workflowData}
      index="name"
      categories={["count"]}
      colors={["blue"]}
      valueFormatter={(number) => `${number} queries`}
    />
  </Card>
)
```

### Week 7-8: Mobile App (React Native)

**Create React Native app**:
```bash
npx react-native init ProActiveMobile
```

**Share business logic**:
```typescript
// shared/src/stores/chatStore.ts
// Same Zustand store works in React Native!
```

---

## Quick Reference Checklists

### Component Extraction Checklist
- [ ] Identify component boundaries
- [ ] Create component file
- [ ] Define props interface (TypeScript)
- [ ] Extract JSX to component
- [ ] Import and use in parent
- [ ] Test component works
- [ ] Add tests

### New Feature Checklist
- [ ] Create component
- [ ] Add to router (if page)
- [ ] Create Zustand store (if needed)
- [ ] Add API functions
- [ ] Create TanStack Query hooks
- [ ] Add Zod validation schema
- [ ] Write tests
- [ ] Update documentation

### Performance Optimization Checklist
- [ ] Add React.memo to expensive components
- [ ] Use useMemo for calculations
- [ ] Use useCallback for event handlers
- [ ] Implement code splitting (React.lazy)
- [ ] Add virtual scrolling for long lists
- [ ] Optimize images
- [ ] Add service worker (PWA)

### Accessibility Checklist
- [ ] Add aria-labels
- [ ] Implement keyboard navigation
- [ ] Add focus management
- [ ] Check color contrast
- [ ] Test with screen reader
- [ ] Add skip-to-content link
- [ ] Support keyboard shortcuts

---

## Migration Scripts

### Component Extractor Script

```bash
# Usage: node .claude/skills/ui/scripts/extract-component.js <name> <start> <end>
node .claude/skills/ui/scripts/extract-component.js ChatInterface 442 568
```

This creates `frontend/src/components/chat/ChatInterface.jsx` with the extracted code.

---

## Troubleshooting

### Common Issues

**State not syncing after Zustand migration:**
- Ensure you're using the store setter functions
- Check devtools to see state changes
- Verify no stale useState hooks remain

**Router navigation not working:**
- Check that all links use `<Link to="/path">` not `<a href>`
- Verify routes are defined correctly
- Check for trailing slashes in paths

**TypeScript errors after migration:**
- Install missing @types packages
- Add type definitions for external libraries
- Use `// @ts-ignore` temporarily for complex types
- Gradually strict typing, start with `strict: false`

**Tests failing after refactor:**
- Update component imports
- Mock Zustand stores in tests
- Wrap components in Router for tests with navigation
- Update test selectors after HTML changes

---

## Success Metrics

Track these metrics to measure improvement:

- **Bundle size**: Should decrease with code splitting
- **Lighthouse score**: Aim for 90+ across all metrics
- **Code coverage**: Target >80% for critical paths
- **Component count**: ~30-40 reusable components
- **Lines per file**: Average <200 lines
- **Build time**: Should be <10s for dev, <60s for prod
- **Hot reload time**: <2s after code changes

---

This roadmap provides a clear path from the current monolithic 756-line dashboard.jsx to a modern, scalable frontend architecture.
