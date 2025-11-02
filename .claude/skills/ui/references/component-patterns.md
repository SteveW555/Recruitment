# Component Patterns & Code Examples

Practical code examples and patterns for the ProActive People frontend.

## Table of Contents

1. [Component Extraction Patterns](#component-extraction-patterns)
2. [State Management Patterns](#state-management-patterns)
3. [API Integration Patterns](#api-integration-patterns)
4. [Styling Patterns](#styling-patterns)
5. [Form Handling Patterns](#form-handling-patterns)
6. [Error Handling Patterns](#error-handling-patterns)
7. [Performance Optimization Patterns](#performance-optimization-patterns)
8. [Accessibility Patterns](#accessibility-patterns)

---

## Component Extraction Patterns

### Current: Inline Component in dashboard.jsx

```javascript
// Current monolithic pattern (lines 442-568)
<div className="flex-1 bg-white rounded-lg shadow-lg overflow-hidden flex flex-col">
  <div className="bg-gradient-to-r from-blue-500 to-blue-600 p-4 text-white flex items-center justify-between">
    <h2 className="text-lg font-semibold">AI Chat Assistant</h2>
    <select
      value={selectedRole}
      onChange={(e) => setSelectedRole(e.target.value)}
      className="bg-white/20 backdrop-blur-sm text-white rounded-lg px-3 py-1.5 text-sm"
    >
      <option>Managing Director</option>
      <option>Sales</option>
      <option>Recruiter</option>
      <option>Admin and Resources</option>
      <option>HR</option>
    </select>
  </div>
  {/* 100+ more lines... */}
</div>
```

### Recommended: Extracted Component

```javascript
// frontend/src/components/chat/ChatInterface.jsx
import React from 'react'
import { Send, Paperclip } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

export const ChatInterface = ({
  messages,
  inputMessage,
  selectedRole,
  isSending,
  onSendMessage,
  onInputChange,
  onRoleChange,
  messagesEndRef
}) => {
  return (
    <div className="flex-1 bg-white rounded-lg shadow-lg overflow-hidden flex flex-col">
      <ChatHeader
        selectedRole={selectedRole}
        onRoleChange={onRoleChange}
      />
      <MessageList
        messages={messages}
        messagesEndRef={messagesEndRef}
      />
      <ChatInput
        inputMessage={inputMessage}
        isSending={isSending}
        onInputChange={onInputChange}
        onSendMessage={onSendMessage}
      />
    </div>
  )
}

// frontend/src/components/chat/ChatHeader.jsx
export const ChatHeader = ({ selectedRole, onRoleChange }) => (
  <div className="bg-gradient-to-r from-blue-500 to-blue-600 p-4 text-white flex items-center justify-between">
    <h2 className="text-lg font-semibold">AI Chat Assistant</h2>
    <RoleSelector value={selectedRole} onChange={onRoleChange} />
  </div>
)

// frontend/src/components/chat/MessageList.jsx
export const MessageList = ({ messages, messagesEndRef }) => (
  <div className="flex-1 overflow-y-auto p-6 space-y-4">
    {messages.map((msg, idx) => (
      <Message key={idx} message={msg} />
    ))}
    <div ref={messagesEndRef} />
  </div>
)

// frontend/src/components/chat/Message.jsx
export const Message = ({ message }) => {
  const isUser = message.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-start' : 'justify-end'}`}>
      <div className={`max-w-3xl rounded-lg p-4 ${
        isUser ? 'bg-blue-100 text-blue-900' : 'bg-gray-100 text-gray-900'
      }`}>
        {message.role === 'assistant' ? (
          <ReactMarkdown remarkPlugins={[remarkGfm]} className="prose prose-sm max-w-none">
            {message.text}
          </ReactMarkdown>
        ) : (
          <p>{message.text}</p>
        )}
        {message.metadata && <MessageMetadata metadata={message.metadata} />}
        <span className="text-xs text-gray-500 mt-2 block">{message.timestamp}</span>
      </div>
    </div>
  )
}

// frontend/src/components/chat/ChatInput.jsx
export const ChatInput = ({ inputMessage, isSending, onInputChange, onSendMessage }) => {
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      onSendMessage()
    }
  }

  return (
    <div className="border-t border-gray-200 p-4">
      <div className="flex items-center gap-2">
        <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
          <Paperclip className="w-5 h-5" />
        </button>
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => onInputChange(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          disabled={isSending}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={onSendMessage}
          disabled={isSending || !inputMessage.trim()}
          className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2"
        >
          <Send className="w-4 h-4" />
          {isSending ? 'Sending...' : 'Send'}
        </button>
      </div>
    </div>
  )
}
```

### Usage in Dashboard

```javascript
// frontend/src/pages/Dashboard.jsx or dashboard.jsx (refactored)
import { ChatInterface } from './components/chat/ChatInterface'

function Dashboard() {
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [selectedRole, setSelectedRole] = useState('Recruiter')
  const [isSending, setIsSending] = useState(false)
  const messagesEndRef = useRef(null)

  const handleSendMessage = async () => {
    // ... existing send logic ...
  }

  return (
    <div className="flex flex-col h-screen">
      <ChatInterface
        messages={messages}
        inputMessage={inputMessage}
        selectedRole={selectedRole}
        isSending={isSending}
        onSendMessage={handleSendMessage}
        onInputChange={setInputMessage}
        onRoleChange={setSelectedRole}
        messagesEndRef={messagesEndRef}
      />
    </div>
  )
}
```

---

## State Management Patterns

### Current: useState in One File

```javascript
// Current approach in dashboard.jsx
const [activePage, setActivePage] = useState('dashboard')
const [messages, setMessages] = useState([])
const [consoleLogs, setConsoleLogs] = useState([])
// ... 7 state variables scattered throughout
```

### Recommended: Zustand Store

```javascript
// frontend/src/stores/chatStore.js
import { create } from 'zustand'

export const useChatStore = create((set, get) => ({
  // State
  messages: [],
  inputMessage: '',
  selectedRole: 'Recruiter',
  isSending: false,

  // Actions
  setInputMessage: (message) => set({ inputMessage: message }),
  setSelectedRole: (role) => set({ selectedRole: role }),

  addMessage: (message) => set((state) => ({
    messages: [...state.messages, {
      ...message,
      timestamp: new Date().toLocaleTimeString()
    }]
  })),

  sendMessage: async (backendUrl) => {
    const { inputMessage, selectedRole, messages } = get()
    if (!inputMessage.trim()) return

    // Add user message
    const userMessage = {
      role: 'user',
      text: inputMessage
    }
    set((state) => ({
      messages: [...state.messages, userMessage],
      inputMessage: '',
      isSending: true
    }))

    try {
      const response = await fetch(`${backendUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: inputMessage,
          sessionId: 'elephant-session-1',
          useHistory: true
        })
      })

      const data = await response.json()

      set((state) => ({
        messages: [...state.messages, {
          role: 'assistant',
          text: data.response,
          metadata: data.metadata
        }],
        isSending: false
      }))
    } catch (error) {
      set((state) => ({
        messages: [...state.messages, {
          role: 'assistant',
          text: `Error: ${error.message}`,
          isError: true
        }],
        isSending: false
      }))
    }
  },

  clearMessages: () => set({ messages: [] })
}))

// Usage in component
import { useChatStore } from '../stores/chatStore'

function ChatInterface() {
  const {
    messages,
    inputMessage,
    selectedRole,
    isSending,
    setInputMessage,
    setSelectedRole,
    sendMessage
  } = useChatStore()

  return (
    <div>
      {/* Use state and actions */}
      <input
        value={inputMessage}
        onChange={(e) => setInputMessage(e.target.value)}
      />
      <button onClick={() => sendMessage('/api')}>Send</button>
    </div>
  )
}
```

### Alternative: Context + useReducer (No Dependencies)

```javascript
// frontend/src/context/ChatContext.jsx
import React, { createContext, useContext, useReducer } from 'react'

const ChatContext = createContext()

const initialState = {
  messages: [],
  inputMessage: '',
  selectedRole: 'Recruiter',
  isSending: false
}

function chatReducer(state, action) {
  switch (action.type) {
    case 'SET_INPUT':
      return { ...state, inputMessage: action.payload }
    case 'SET_ROLE':
      return { ...state, selectedRole: action.payload }
    case 'ADD_MESSAGE':
      return { ...state, messages: [...state.messages, action.payload] }
    case 'SET_SENDING':
      return { ...state, isSending: action.payload }
    case 'CLEAR_MESSAGES':
      return { ...state, messages: [] }
    default:
      return state
  }
}

export function ChatProvider({ children }) {
  const [state, dispatch] = useReducer(chatReducer, initialState)

  const setInputMessage = (message) => {
    dispatch({ type: 'SET_INPUT', payload: message })
  }

  const addMessage = (message) => {
    dispatch({ type: 'ADD_MESSAGE', payload: message })
  }

  const value = {
    ...state,
    setInputMessage,
    addMessage,
    dispatch
  }

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>
}

export const useChat = () => {
  const context = useContext(ChatContext)
  if (!context) {
    throw new Error('useChat must be used within ChatProvider')
  }
  return context
}

// Usage
import { ChatProvider, useChat } from './context/ChatContext'

function App() {
  return (
    <ChatProvider>
      <Dashboard />
    </ChatProvider>
  )
}

function Dashboard() {
  const { messages, inputMessage, setInputMessage, addMessage } = useChat()
  // Use state and actions
}
```

---

## API Integration Patterns

### Current: Fetch in Component

```javascript
// Current approach (lines 188-258 in dashboard.jsx)
const handleSendMessage = async () => {
  if (isSending || !inputMessage.trim()) return

  const userMessage = {
    role: 'user',
    text: inputMessage,
    timestamp: new Date().toLocaleTimeString()
  }

  setMessages([...messages, userMessage])
  setInputMessage('')
  setIsSending(true)

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: inputMessage,
        sessionId: 'elephant-session-1',
        useHistory: true,
        agent: agentType
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()

    const assistantMessage = {
      role: 'assistant',
      text: data.response,
      timestamp: new Date().toLocaleTimeString(),
      metadata: data.metadata
    }

    setMessages(prev => [...prev, assistantMessage])
  } catch (error) {
    const errorMessage = {
      role: 'assistant',
      text: `Error: ${error.message}`,
      timestamp: new Date().toLocaleTimeString(),
      isError: true
    }
    setMessages(prev => [...prev, errorMessage])
  } finally {
    setIsSending(false)
  }
}
```

### Recommended: TanStack Query (React Query)

```javascript
// frontend/src/api/chatApi.js
export const sendChatMessage = async ({ message, sessionId, agent }) => {
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

// frontend/src/hooks/useChat.js
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { sendChatMessage } from '../api/chatApi'

export const useSendMessage = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: sendChatMessage,
    onSuccess: (data) => {
      // Optionally update cache or trigger refetches
      queryClient.invalidateQueries(['chatHistory'])
    },
    onError: (error) => {
      console.error('Chat error:', error)
    }
  })
}

// Usage in component
import { useSendMessage } from '../hooks/useChat'

function ChatInterface() {
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')

  const sendMessage = useSendMessage()

  const handleSend = () => {
    if (!inputMessage.trim()) return

    const userMsg = {
      role: 'user',
      text: inputMessage,
      timestamp: new Date().toLocaleTimeString()
    }
    setMessages(prev => [...prev, userMsg])
    setInputMessage('')

    sendMessage.mutate(
      {
        message: inputMessage,
        sessionId: 'elephant-session-1',
        agent: 'general'
      },
      {
        onSuccess: (data) => {
          setMessages(prev => [...prev, {
            role: 'assistant',
            text: data.response,
            timestamp: new Date().toLocaleTimeString(),
            metadata: data.metadata
          }])
        },
        onError: (error) => {
          setMessages(prev => [...prev, {
            role: 'assistant',
            text: `Error: ${error.message}`,
            timestamp: new Date().toLocaleTimeString(),
            isError: true
          }])
        }
      }
    )
  }

  return (
    <div>
      {/* UI */}
      <button
        onClick={handleSend}
        disabled={sendMessage.isPending}
      >
        {sendMessage.isPending ? 'Sending...' : 'Send'}
      </button>
    </div>
  )
}
```

### Alternative: Custom Fetch Hook (No Dependencies)

```javascript
// frontend/src/hooks/useFetch.js
import { useState, useCallback } from 'react'

export const useFetch = () => {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchData = useCallback(async (url, options = {}) => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch(url, {
        headers: { 'Content-Type': 'application/json' },
        ...options
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setIsLoading(false)
      return { data, error: null }
    } catch (err) {
      setError(err.message)
      setIsLoading(false)
      return { data: null, error: err.message }
    }
  }, [])

  return { fetchData, isLoading, error }
}

// Usage
import { useFetch } from './hooks/useFetch'

function ChatInterface() {
  const { fetchData, isLoading, error } = useFetch()

  const handleSend = async () => {
    const { data, error } = await fetchData('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ message: inputMessage })
    })

    if (error) {
      console.error('Error:', error)
      return
    }

    // Handle successful response
    console.log('Response:', data)
  }

  return (
    <button onClick={handleSend} disabled={isLoading}>
      {isLoading ? 'Loading...' : 'Send'}
    </button>
  )
}
```

---

## Styling Patterns

### Tailwind Utility Classes

```javascript
// Layout
<div className="flex items-center justify-between gap-4">
<div className="grid grid-cols-3 gap-6">
<div className="max-w-7xl mx-auto px-4">

// Spacing
<div className="p-6">        // padding all sides
<div className="px-4 py-2">  // padding horizontal/vertical
<div className="space-y-4">  // space between children

// Colors
<div className="bg-blue-500 text-white">
<div className="bg-gradient-to-r from-blue-500 to-blue-600">
<div className="border-gray-200 border">

// Effects
<div className="rounded-lg shadow-lg">
<div className="hover:bg-blue-600 transition-colors">
<div className="backdrop-blur-sm bg-white/20">

// Responsive
<div className="hidden md:block">           // show on medium+
<div className="w-full md:w-1/2 lg:w-1/3">  // responsive widths
```

### Component Style Patterns

```javascript
// Card Pattern
<div className="bg-white rounded-lg shadow-lg p-6">
  <h3 className="text-lg font-semibold text-gray-900">Title</h3>
  <p className="text-gray-600 mt-2">Content</p>
</div>

// Button Pattern
<button className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 transition-all flex items-center gap-2">
  <Icon className="w-4 h-4" />
  Button Text
</button>

// Input Pattern
<input
  type="text"
  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
  placeholder="Placeholder text"
/>

// Badge Pattern
<span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
  Active
</span>

// Progress Bar Pattern
<div className="w-full bg-gray-200 rounded-full h-2">
  <div className="bg-blue-500 h-2 rounded-full" style={{ width: '75%' }} />
</div>
```

### Color System

```javascript
// Define in tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        success: '#10b981',
        warning: '#f59e0b',
        error: '#ef4444',
      }
    }
  }
}

// Usage
<div className="bg-primary-500 text-white">
<div className="text-success">Success message</div>
```

---

## Form Handling Patterns

### Current: Manual Form State

```javascript
// Current approach
const [inputMessage, setInputMessage] = useState('')
const [selectedRole, setSelectedRole] = useState('Recruiter')

<input
  value={inputMessage}
  onChange={(e) => setInputMessage(e.target.value)}
/>
```

### Recommended: React Hook Form + Zod

```javascript
// frontend/src/schemas/chatSchema.js
import { z } from 'zod'

export const chatMessageSchema = z.object({
  message: z.string().min(1, 'Message is required').max(1000, 'Message too long'),
  role: z.enum(['Managing Director', 'Sales', 'Recruiter', 'Admin and Resources', 'HR']),
  sessionId: z.string().optional()
})

// Usage in component
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { chatMessageSchema } from '../schemas/chatSchema'

function ChatForm({ onSubmit }) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset
  } = useForm({
    resolver: zodResolver(chatMessageSchema),
    defaultValues: {
      message: '',
      role: 'Recruiter'
    }
  })

  const onSubmitForm = async (data) => {
    await onSubmit(data)
    reset()
  }

  return (
    <form onSubmit={handleSubmit(onSubmitForm)} className="space-y-4">
      <div>
        <input
          {...register('message')}
          placeholder="Type your message..."
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        />
        {errors.message && (
          <p className="text-red-500 text-sm mt-1">{errors.message.message}</p>
        )}
      </div>

      <select {...register('role')} className="px-4 py-2 border rounded-lg">
        <option>Managing Director</option>
        <option>Sales</option>
        <option>Recruiter</option>
        <option>Admin and Resources</option>
        <option>HR</option>
      </select>

      <button
        type="submit"
        disabled={isSubmitting}
        className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
      >
        {isSubmitting ? 'Sending...' : 'Send'}
      </button>
    </form>
  )
}
```

### Alternative: Controlled Form (No Dependencies)

```javascript
// Custom form validation
function ChatForm({ onSubmit }) {
  const [formData, setFormData] = useState({
    message: '',
    role: 'Recruiter'
  })
  const [errors, setErrors] = useState({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  const validate = () => {
    const newErrors = {}

    if (!formData.message.trim()) {
      newErrors.message = 'Message is required'
    } else if (formData.message.length > 1000) {
      newErrors.message = 'Message is too long'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!validate()) return

    setIsSubmitting(true)
    try {
      await onSubmit(formData)
      setFormData({ message: '', role: 'Recruiter' })
      setErrors({})
    } catch (error) {
      setErrors({ submit: error.message })
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={formData.message}
        onChange={(e) => handleChange('message', e.target.value)}
        className={errors.message ? 'border-red-500' : ''}
      />
      {errors.message && <p className="text-red-500">{errors.message}</p>}

      <select
        value={formData.role}
        onChange={(e) => handleChange('role', e.target.value)}
      >
        <option>Recruiter</option>
        {/* ... */}
      </select>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Sending...' : 'Send'}
      </button>
    </form>
  )
}
```

---

## Error Handling Patterns

### Current Error Handling

```javascript
// Error in messages array
try {
  const response = await fetch('/api/chat', { /* ... */ })
  const data = await response.json()
  setMessages(prev => [...prev, { role: 'assistant', text: data.response }])
} catch (error) {
  setMessages(prev => [...prev, {
    role: 'assistant',
    text: `Error: ${error.message}`,
    isError: true
  }])
}

// Rendering errors
{message.isError && (
  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
    <p className="text-red-600">{message.text}</p>
  </div>
)}
```

### Recommended: Error Boundary + Toast System

```javascript
// frontend/src/components/ErrorBoundary.jsx
import React from 'react'

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100">
          <div className="bg-white p-8 rounded-lg shadow-lg max-w-md">
            <h2 className="text-2xl font-bold text-red-600 mb-4">Something went wrong</h2>
            <p className="text-gray-600 mb-4">{this.state.error?.message}</p>
            <button
              onClick={() => window.location.reload()}
              className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
            >
              Reload Page
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

// Usage
import { ErrorBoundary } from './components/ErrorBoundary'

function App() {
  return (
    <ErrorBoundary>
      <Dashboard />
    </ErrorBoundary>
  )
}

// Toast notification system
// frontend/src/components/Toast.jsx
import { useState, useEffect } from 'react'
import { X } from 'lucide-react'

export const Toast = ({ message, type = 'info', onClose, duration = 5000 }) => {
  useEffect(() => {
    const timer = setTimeout(onClose, duration)
    return () => clearTimeout(timer)
  }, [duration, onClose])

  const colors = {
    success: 'bg-green-500',
    error: 'bg-red-500',
    warning: 'bg-yellow-500',
    info: 'bg-blue-500'
  }

  return (
    <div className={`${colors[type]} text-white px-6 py-4 rounded-lg shadow-lg flex items-center justify-between gap-4`}>
      <p>{message}</p>
      <button onClick={onClose} className="hover:bg-white/20 rounded p-1">
        <X className="w-4 h-4" />
      </button>
    </div>
  )
}

// Toast container
export const ToastContainer = ({ toasts, removeToast }) => (
  <div className="fixed top-4 right-4 space-y-2 z-50">
    {toasts.map((toast) => (
      <Toast
        key={toast.id}
        {...toast}
        onClose={() => removeToast(toast.id)}
      />
    ))}
  </div>
)

// Usage with custom hook
// frontend/src/hooks/useToast.js
import { useState, useCallback } from 'react'

export const useToast = () => {
  const [toasts, setToasts] = useState([])

  const addToast = useCallback((message, type = 'info') => {
    const id = Date.now()
    setToasts(prev => [...prev, { id, message, type }])
  }, [])

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  return { toasts, addToast, removeToast }
}

// In component
import { useToast } from '../hooks/useToast'
import { ToastContainer } from '../components/Toast'

function Dashboard() {
  const { toasts, addToast, removeToast } = useToast()

  const handleError = (error) => {
    addToast(error.message, 'error')
  }

  const handleSuccess = (message) => {
    addToast(message, 'success')
  }

  return (
    <>
      <ToastContainer toasts={toasts} removeToast={removeToast} />
      {/* Rest of component */}
    </>
  )
}
```

---

## Performance Optimization Patterns

### React.memo for Expensive Components

```javascript
// Without optimization
export const WorkflowCategory = ({ category, examples, isExpanded, onToggle }) => {
  console.log('WorkflowCategory rendered')
  return (
    <div>
      {/* Component content */}
    </div>
  )
}

// With React.memo
export const WorkflowCategory = React.memo(({ category, examples, isExpanded, onToggle }) => {
  console.log('WorkflowCategory rendered')
  return (
    <div>
      {/* Component content */}
    </div>
  )
}, (prevProps, nextProps) => {
  // Custom comparison function (optional)
  return (
    prevProps.category.id === nextProps.category.id &&
    prevProps.isExpanded === nextProps.isExpanded
  )
})
```

### useMemo for Expensive Calculations

```javascript
// Current approach - recalculates on every render
function AnalyticsPage() {
  const totalQueries = workflowData.reduce((sum, item) => sum + item.count, 0)
  const avgQueriesPerDay = totalQueries / 30

  return <div>{avgQueriesPerDay}</div>
}

// Optimized with useMemo
import { useMemo } from 'react'

function AnalyticsPage() {
  const totalQueries = useMemo(() => {
    return workflowData.reduce((sum, item) => sum + item.count, 0)
  }, [workflowData])

  const avgQueriesPerDay = useMemo(() => {
    return totalQueries / 30
  }, [totalQueries])

  return <div>{avgQueriesPerDay}</div>
}
```

### useCallback for Event Handlers

```javascript
// Without useCallback - new function on every render
function ChatInterface() {
  const handleSendMessage = () => {
    console.log('Send message')
  }

  return <ChatInput onSend={handleSendMessage} />
}

// With useCallback - stable function reference
import { useCallback } from 'react'

function ChatInterface() {
  const [messages, setMessages] = useState([])

  const handleSendMessage = useCallback(() => {
    console.log('Send message')
    // Use functional update to avoid dependency on messages
    setMessages(prev => [...prev, newMessage])
  }, []) // Empty deps because we use functional update

  return <ChatInput onSend={handleSendMessage} />
}
```

### Code Splitting with React.lazy

```javascript
// Current - everything loaded upfront
import Dashboard from './Dashboard'
import Analytics from './Analytics'

function App() {
  return activePage === 'dashboard' ? <Dashboard /> : <Analytics />
}

// Optimized - lazy load pages
import { lazy, Suspense } from 'react'

const Dashboard = lazy(() => import('./Dashboard'))
const Analytics = lazy(() => import('./Analytics'))

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      {activePage === 'dashboard' ? <Dashboard /> : <Analytics />}
    </Suspense>
  )
}
```

### Virtual Scrolling for Long Lists

```javascript
// For long chat message lists
import { useVirtualizer } from '@tanstack/react-virtual'

function MessageList({ messages }) {
  const parentRef = useRef()

  const virtualizer = useVirtualizer({
    count: messages.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 100, // Estimated height of each message
    overscan: 5 // Render 5 items above/below visible area
  })

  return (
    <div ref={parentRef} className="h-full overflow-y-auto">
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          position: 'relative'
        }}
      >
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.index}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              transform: `translateY(${virtualItem.start}px)`
            }}
          >
            <Message message={messages[virtualItem.index]} />
          </div>
        ))}
      </div>
    </div>
  )
}
```

---

## Accessibility Patterns

### ARIA Labels for Icon Buttons

```javascript
// Current - no aria-label
<button className="p-2">
  <Bell className="w-5 h-5" />
</button>

// Accessible
<button
  className="p-2"
  aria-label="View notifications"
  aria-describedby="notification-count"
>
  <Bell className="w-5 h-5" />
  <span id="notification-count" className="sr-only">
    3 unread notifications
  </span>
</button>

// Screen reader only class (add to index.css)
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
```

### Keyboard Navigation

```javascript
// Add keyboard shortcuts
import { useEffect } from 'react'

function ChatInterface() {
  useEffect(() => {
    const handleKeyboard = (e) => {
      // Ctrl+/ to focus chat input
      if (e.ctrlKey && e.key === '/') {
        e.preventDefault()
        document.getElementById('chat-input')?.focus()
      }

      // Esc to clear input
      if (e.key === 'Escape') {
        setInputMessage('')
      }
    }

    window.addEventListener('keydown', handleKeyboard)
    return () => window.removeEventListener('keydown', handleKeyboard)
  }, [])

  return (
    <input
      id="chat-input"
      aria-label="Chat message input"
      aria-describedby="chat-input-help"
    />
  )
}
```

### Focus Management

```javascript
// Trap focus in modals
import { useRef, useEffect } from 'react'

function Modal({ isOpen, onClose, children }) {
  const modalRef = useRef()
  const firstFocusableRef = useRef()
  const lastFocusableRef = useRef()

  useEffect(() => {
    if (!isOpen) return

    // Focus first element when modal opens
    firstFocusableRef.current?.focus()

    const handleTab = (e) => {
      if (e.key !== 'Tab') return

      if (e.shiftKey) {
        // Shift+Tab
        if (document.activeElement === firstFocusableRef.current) {
          e.preventDefault()
          lastFocusableRef.current?.focus()
        }
      } else {
        // Tab
        if (document.activeElement === lastFocusableRef.current) {
          e.preventDefault()
          firstFocusableRef.current?.focus()
        }
      }
    }

    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        onClose()
      }
    }

    document.addEventListener('keydown', handleTab)
    document.addEventListener('keydown', handleEscape)

    return () => {
      document.removeEventListener('keydown', handleTab)
      document.removeEventListener('keydown', handleEscape)
    }
  }, [isOpen, onClose])

  if (!isOpen) return null

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      ref={modalRef}
    >
      <div className="bg-white rounded-lg p-6 max-w-md w-full">
        <button ref={firstFocusableRef} aria-label="Close modal">
          X
        </button>
        <h2 id="modal-title">Modal Title</h2>
        {children}
        <button ref={lastFocusableRef}>Last Focusable</button>
      </div>
    </div>
  )
}
```

### Color Contrast

```javascript
// Ensure WCAG AA compliance (4.5:1 for normal text)

// Bad - insufficient contrast
<p className="text-gray-400 bg-white">Low contrast text</p>

// Good - sufficient contrast
<p className="text-gray-700 bg-white">Good contrast text</p>
<p className="text-white bg-blue-600">Good contrast on colored background</p>

// Check contrast ratios:
// - Normal text (4.5:1): text-gray-600 on white
// - Large text (3:1): text-gray-500 on white
// - UI components (3:1): border-gray-400 on white
```

---

## Common Snippets

### Loading Spinner

```javascript
export const LoadingSpinner = ({ size = 'md' }) => {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  }

  return (
    <div className="flex items-center justify-center">
      <div className={`${sizes[size]} border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin`} />
    </div>
  )
}
```

### Copy to Clipboard

```javascript
const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    addToast('Copied to clipboard!', 'success')
  } catch (err) {
    addToast('Failed to copy', 'error')
  }
}

// Usage
<button
  onClick={() => copyToClipboard(sqlQuery)}
  className="text-blue-500 hover:text-blue-600"
  aria-label="Copy SQL query to clipboard"
>
  Copy
</button>
```

### Auto-scroll to Bottom

```javascript
import { useEffect, useRef } from 'react'

function MessageList({ messages }) {
  const endRef = useRef(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="overflow-y-auto">
      {messages.map((msg, i) => (
        <Message key={i} message={msg} />
      ))}
      <div ref={endRef} />
    </div>
  )
}
```

---

These patterns provide the foundation for building robust, maintainable frontend features in the ProActive People recruitment system.
