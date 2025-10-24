import React, { useState, useRef, useEffect } from 'react';
import {
  Search, Bell, ChevronDown, Send, Paperclip, Calendar, ChevronRight, Plus,
  Mail, FolderOpen, Briefcase, FileSpreadsheet, Monitor,
  Lightbulb, TrendingUp, Zap, Menu
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export default function Dashboard() {
  // Refs for auto-scrolling
  const messagesEndRef = useRef(null);
  const consoleEndRef = useRef(null);

  const [activePage, setActivePage] = useState('dashboard');
  const [messages, setMessages] = useState([
    { id: 1, type: 'ai', text: 'Hello! I\'m your AI assistant for querying the ProActive People candidates database. You can ask me questions like:\n\n• "Find Python developers"\n• "Show available candidates"\n• "Who was contacted this week?"\n• "Candidates with AWS skills wanting over 100k"\n\nWhat would you like to know?', timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false }) }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [expandedCategory, setExpandedCategory] = useState(null);
  const [selectedRole, setSelectedRole] = useState('Recruiter');
  const [isSending, setIsSending] = useState(false);
  const [consoleLogs, setConsoleLogs] = useState([
    { id: 1, level: 'info', message: 'System initialized', timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false }) },
    { id: 2, level: 'success', message: 'Connected to AI Router service', timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false }) }
  ]);

  const connectedSources = [
    { icon: Mail, name: 'Gmail', count: '2,847 emails', status: 'Connected', color: 'bg-red-100' },
    { icon: FolderOpen, name: 'Google Drive', count: '1,234 files', status: 'Connected', color: 'bg-blue-100' },
    { icon: Briefcase, name: 'Salesforce', count: '456 records', status: 'Connected', color: 'bg-cyan-100' },
    { icon: FileSpreadsheet, name: 'Excel Files', count: '89 spreadsheets', status: 'Connected', color: 'bg-green-100' },
    { icon: Monitor, name: 'Local Computer', count: 'Full access', status: 'Connected', color: 'bg-purple-100' }
  ];

  const roleWorkflows = {
    'Managing Director': {
      lookup: ['Find all board meeting notes from Q4', 'Search for strategic planning documents', 'Locate company performance reports'],
      problemSolve: ['Why is employee turnover increasing?', 'Identify bottlenecks in client acquisition', 'Analyze cost reduction opportunities'],
      report: ['Generate executive summary for board', 'Create company-wide performance dashboard', 'Compile financial overview report'],
      automation: ['Auto-send weekly executive briefings', 'Schedule monthly board report generation', 'Set up KPI tracking alerts']
    },
    'Sales': {
      lookup: ['Find all active client contracts', 'Search for proposals sent last month', 'Locate top performing accounts'],
      problemSolve: ['Why did revenue drop last quarter?', 'Identify lost deal patterns', 'Find gaps in sales pipeline'],
      report: ['Generate monthly sales performance report', 'Create client acquisition summary', 'Compile revenue forecast'],
      automation: ['Auto-send follow-up emails to prospects', 'Schedule weekly pipeline reviews', 'Set up deal stage notifications']
    },
    'Recruiter': {
      lookup: ['Find tech candidates with 5+ years experience', 'Search for active job openings', 'Locate candidate interview feedback'],
      problemSolve: ['Why are we losing candidates at offer stage?', 'Identify recruitment bottlenecks', 'Analyze time-to-hire trends'],
      report: ['Generate monthly placement report', 'Create candidate pipeline summary', 'Compile recruiter performance metrics'],
      automation: ['Auto-send candidate follow-up emails', 'Schedule interview reminders', 'Set up candidate status updates']
    },
    'Admin and Resources': {
      lookup: ['Find office expense reports', 'Search for vendor contracts', 'Locate IT equipment inventory'],
      problemSolve: ['Why are office costs increasing?', 'Identify resource allocation issues', 'Find unused software licenses'],
      report: ['Generate monthly expense report', 'Create facilities usage summary', 'Compile vendor spending analysis'],
      automation: ['Auto-approve routine expense claims', 'Schedule monthly budget reviews', 'Set up supply reorder alerts']
    },
    'HR': {
      lookup: ['Find employee performance reviews', 'Search for leave requests pending', 'Locate training completion records'],
      problemSolve: ['Why is employee satisfaction declining?', 'Identify training gaps', 'Analyze absenteeism patterns'],
      report: ['Generate employee engagement report', 'Create headcount summary', 'Compile benefits utilization analysis'],
      automation: ['Auto-send onboarding checklists', 'Schedule performance review reminders', 'Set up leave approval notifications']
    }
  };

  const workflowCategories = [
    {
      id: 'lookup',
      name: 'Lookup',
      icon: Search,
      color: 'bg-blue-100',
      examples: roleWorkflows[selectedRole].lookup
    },
    {
      id: 'problem-solve',
      name: 'Problem Solve',
      icon: Lightbulb,
      color: 'bg-yellow-100',
      examples: roleWorkflows[selectedRole].problemSolve
    },
    {
      id: 'report',
      name: 'Report',
      icon: TrendingUp,
      color: 'bg-green-100',
      examples: roleWorkflows[selectedRole].report
    },
    {
      id: 'automation',
      name: 'Automation',
      icon: Zap,
      color: 'bg-purple-100',
      examples: roleWorkflows[selectedRole].automation
    }
  ];

  const addLog = (message, level = 'info') => {
    const timestamp = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
    setConsoleLogs(prev => [...prev, {
      id: prev.length + 1,
      level,
      message,
      timestamp
    }]);
  };

  // Auto-scroll messages area when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Auto-scroll console when new logs arrive
  useEffect(() => {
    consoleEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [consoleLogs]);

  const classifyQuery = (query) => {
    const lowerQuery = query.toLowerCase();

    // General chat patterns
    if (/^(hi|hello|hey|good morning|good afternoon|good evening|how are you|whats up|sup|greetings)[\s\?]*$/i.test(lowerQuery)) {
      return 'general-chat';
    }

    // Information retrieval patterns
    if (/^(find|search|show|list|locate|retrieve|get|display|fetch|view|check|access|who|where|what|how many|give me|tell me|look up|pull up).*(candidate|job|placement|open|available|contact|email|phone|feedback|interview|notes|profile|record|data|information)/i.test(query) ||
      /^(find|search|locate|retrieve|get).*(with|having|that have).*(skill|experience|years|salary|location)/i.test(query)) {
      return 'information-retrieval';
    }

    // Problem solving patterns
    if (/^(why|analyze|identify|find|what.*issue|what.*problem|what.*challenge|what.*bottleneck|suggest|recommend|solve).*(is|are|we|our|the)/i.test(query)) {
      return 'problem-solving';
    }

    // Automation patterns
    if (/^(automate|workflow|set up|create|design|build).*(workflow|automation|process|pipeline|trigger|action)/i.test(query)) {
      return 'automation';
    }

    // Report generation patterns
    if (/^(generate|create|make|produce|compile|report|summary|dashboard|analytics|metrics|performance)/i.test(query)) {
      return 'report-generation';
    }

    // Industry knowledge patterns
    if (/^(what|tell me|explain|clarify).*(gdpr|ir35|right-to-work|employment law|compliance|regulation|standard|best practice|guideline|legal|law|requirement)/i.test(query) ||
      /^(gdpr|ir35|right-to-work|employment law|compliance|regulation)/i.test(query)) {
      return 'industry-knowledge';
    }

    // Default to general chat
    return 'general-chat';
  };

  const handleSendMessage = async (messageOverride = null) => {
    const callId = Math.random().toString(36).substring(7);
    console.log(`[DEBUG ${callId}] handleSendMessage called with:`, messageOverride, 'isSending:', isSending);

    // Prevent concurrent requests
    if (isSending) {
      console.log(`[DEBUG ${callId}] Already sending, ignoring duplicate call`);
      return;
    }

    // If messageOverride is an event object, ignore it and use inputMessage
    const messageToSend = (typeof messageOverride === 'string' ? messageOverride : null) || inputMessage;
    if (!messageToSend || !messageToSend.trim()) {
      console.log(`[DEBUG ${callId}] Empty message, returning`);
      return;
    }

    console.log(`[DEBUG ${callId}] Setting isSending to true`);
    setIsSending(true);

    const userMessage = messageToSend;
    const timestamp = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });

    // Add user message to chat
    setMessages(prev => [...prev, {
      id: prev.length + 1,
      type: 'user',
      text: userMessage,
      timestamp
    }]);

    addLog(`User query: "${userMessage.substring(0, 50)}${userMessage.length > 50 ? '...' : ''}"`, 'info');

    // Clear input immediately
    setInputMessage('');

    try {
      const routeStartTime = performance.now();

      // Classify the query to determine agent type
      const agentType = classifyQuery(userMessage);
      addLog('Routing query to appropriate agent...', 'info');
      addLog(`Classified as: ${agentType}`, 'info');

      // Call backend API through Vite proxy (no hardcoded URL needed)
      // Proxy automatically routes /api/* to http://localhost:3002/api/*
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          sessionId: 'elephant-session-1', // Could be dynamic per user
          useHistory: true, // Maintain conversation context
          agent: agentType // Send the classified agent type
        })
      });

      const routeEndTime = performance.now();
      const routingLatency = (routeEndTime - routeStartTime).toFixed(0);

      const data = await response.json();

      if (data.success) {
        const metadata = data.metadata || {};

        // Log low confidence warning if present
        if (metadata.lowConfidenceWarning) {
          addLog(metadata.lowConfidenceWarning, 'warn');
        }

        // Log detailed routing information
        addLog(`Agent: ${metadata.agent || 'general-chat'} | Confidence: ${metadata.confidence ? (metadata.confidence * 100).toFixed(1) + '%' : 'N/A'}`, 'info');

        if (metadata.classification) {
          addLog(`Classification: ${metadata.classification}`, 'info');
        }

        if (metadata.processingTime) {
          addLog(`Processing time: ${metadata.processingTime}ms | Network latency: ${routingLatency}ms`, 'info');
        } else {
          addLog(`Network latency: ${routingLatency}ms`, 'info');
        }
        addLog(`Agent response received`, 'success');

        // Add AI response to chat
        setMessages(prev => [...prev, {
          id: prev.length + 1,
          type: 'ai',
          text: data.message,
          timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false }),
          metadata: data.metadata
        }]);
      } else {
        addLog(`Routing failed: ${data.error || 'Unknown error'}`, 'error');

        if (data.metadata?.agent) {
          addLog(`Attempted agent: ${data.metadata.agent}`, 'warn');
        }

        // Handle error response
        setMessages(prev => [...prev, {
          id: prev.length + 1,
          type: 'ai',
          text: `Error: ${data.error || 'Failed to get response'}`,
          timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false })
        }]);
      }
    } catch (error) {
      addLog(`Connection error: ${error.message}`, 'error');
      addLog(`Failed to reach routing service at /api/chat`, 'warn');

      // Add error message to chat
      setMessages(prev => [...prev, {
        id: prev.length + 1,
        type: 'ai',
        text: 'Sorry, I encountered an error connecting to the server. Please try again.',
        timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false })
      }]);
    } finally {
      // Always reset sending state
      console.log(`[DEBUG ${callId}] Resetting isSending to false`);
      setIsSending(false);
    }
  };

  const handleExampleClick = (exampleQuery) => {
    // Set the input message so user can see what will be sent
    setInputMessage(exampleQuery);
    // Automatically send the message
    handleSendMessage(exampleQuery);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-100 to-gray-200 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-sm p-4 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <img
                src="/elephant-logo-black.svg"
                alt="Elephant Logo"
                className="w-8 h-8"
              />
              <span className="font-bold text-xl">ELEPHANT</span>
            </div>
            <nav className="flex items-center gap-6">
              <button
                onClick={() => setActivePage('dashboard')}
                className={activePage === 'dashboard' ? 'bg-black text-white px-6 py-2 rounded-full' : 'text-gray-600 hover:text-gray-900'}
              >
                Dashboard
              </button>
              <button
                onClick={() => setActivePage('analytics')}
                className={activePage === 'analytics' ? 'bg-black text-white px-6 py-2 rounded-full' : 'text-gray-600 hover:text-gray-900'}
              >
                Analytics
              </button>
              <button className="text-gray-600 hover:text-gray-900">Account</button>
              <button className="text-gray-600 hover:text-gray-900">Support</button>
            </nav>
            <div className="flex items-center gap-4">
              <button className="p-2 hover:bg-gray-100 rounded-full relative">
                <Bell size={20} />
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
              </button>
              <button className="p-2 hover:bg-gray-100 rounded-full">
                <Menu size={24} />
              </button>
            </div>
          </div>
        </div>

        {activePage === 'dashboard' && (
          <>
            {/* Connected Sources - Horizontal Bar */}
            <div className="bg-white rounded-2xl shadow-sm p-6 mb-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold">Connected Sources</h2>
                <button className="flex items-center gap-2 text-sm text-gray-600 border border-gray-300 px-3 py-1 rounded-lg hover:bg-gray-50">
                  <Calendar size={16} />
                  Last 7 days
                </button>
              </div>

              <div className="grid grid-cols-5 gap-4 mb-4">
                {connectedSources.map((source, index) => {
                  const IconComponent = source.icon;
                  return (
                    <div key={index} className="flex flex-col items-center p-4 rounded-xl hover:bg-gray-50 transition-colors border border-gray-200">
                      <div className={`w-16 h-16 ${source.color} rounded-xl flex items-center justify-center mb-3`}>
                        <IconComponent size={32} className="text-gray-700" />
                      </div>
                      <div className="text-center">
                        <div className="font-semibold text-sm mb-1">{source.name}</div>
                        <div className="text-xs text-gray-500 mb-2">{source.count}</div>
                        <div className="text-green-600 text-xs font-medium">● {source.status}</div>
                      </div>
                    </div>
                  );
                })}
              </div>

              <button className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-3 rounded-xl transition-colors">
                + Add New Source
              </button>
            </div>

            {/* Main Content Grid - Sidebar + Chat */}
            <div className="grid grid-cols-4 gap-6">
              {/* Left Sidebar - Workflows & Queries */}
              <div className="col-span-1 bg-white rounded-2xl shadow-sm overflow-hidden">
                <div className="p-6 border-b border-gray-200 flex items-center min-h-[88px]">
                  <h2 className="text-2xl font-bold">Workflows</h2>
                </div>

                <div className="p-6">
                  <div className="space-y-3 mb-4">
                    {workflowCategories.map((category) => {
                      const CategoryIcon = category.icon;
                      return (
                        <div key={category.id} className="border border-gray-200 rounded-xl overflow-hidden">
                          <button
                            onClick={() => setExpandedCategory(expandedCategory === category.id ? null : category.id)}
                            className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
                          >
                            <div className="flex items-center gap-3">
                              <div className={`w-10 h-10 ${category.color} rounded-lg flex items-center justify-center`}>
                                <CategoryIcon size={20} className="text-gray-700" />
                              </div>
                              <span className="font-semibold">{category.name}</span>
                            </div>
                            <ChevronRight
                              size={20}
                              className={`transition-transform ${expandedCategory === category.id ? 'rotate-90' : ''}`}
                            />
                          </button>

                          {expandedCategory === category.id && (
                            <div className="px-4 pb-4 space-y-2">
                              {category.examples.map((example, idx) => (
                                <button
                                  key={idx}
                                  onClick={() => handleExampleClick(example)}
                                  disabled={isSending}
                                  className={`w-full text-left text-sm p-2 rounded-lg transition-colors ${
                                    isSending
                                      ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                                      : 'hover:bg-gray-100 text-gray-700'
                                  }`}
                                >
                                  {example}
                                </button>
                              ))}
                              <button className="w-full text-left text-sm p-2 rounded-lg hover:bg-gray-100 transition-colors text-blue-600 flex items-center gap-2">
                                <Plus size={16} />
                                Add custom query
                              </button>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>

                  <button className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-3 rounded-xl transition-colors flex items-center justify-center gap-2">
                    <Plus size={20} />
                    Add Workflow
                  </button>
                </div>
              </div>

              {/* Chat Interface + Console Container */}
              <div className="col-span-3 flex flex-col gap-6">
                {/* Chat Interface */}
                <div className="bg-white rounded-2xl shadow-sm flex flex-col" style={{ height: '650px' }}>
                  {/* Chat Header */}
                  <div className="p-4 border-b border-gray-200 flex items-center justify-between">
                    <h2 className="text-2xl font-bold">AI Assistant</h2>
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-medium text-gray-600">Role:</span>
                      <select
                        value={selectedRole}
                        onChange={(e) => setSelectedRole(e.target.value)}
                        className="pl-4 pr-10 py-2 text-sm font-medium border border-gray-300 rounded-full bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-black transition-colors cursor-pointer appearance-none bg-[url('data:image/svg+xml;charset=utf-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20fill%3D%22none%22%20viewBox%3D%220%200%2020%2020%22%3E%3Cpath%20stroke%3D%22%236b7280%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%20stroke-width%3D%221.5%22%20d%3D%22M6%208l4%204%204-4%22%2F%3E%3C%2Fsvg%3E')] bg-[length:1.25rem_1.25rem] bg-[right_0.5rem_center] bg-no-repeat"
                      >
                        <option value="Managing Director">Managing Director</option>
                        <option value="Sales">Sales</option>
                        <option value="Recruiter">Recruiter</option>
                        <option value="Admin and Resources">Admin and Resources</option>
                        <option value="HR">HR</option>
                      </select>
                    </div>
                  </div>

                  {/* Messages Area */}
                  <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    {messages.map((message) => {
                      // Check if message is an error (starts with Error:)
                      const isError = message.type === 'ai' && message.text?.startsWith('Error:');

                      return (
                      <div key={message.id} className={`flex flex-col ${message.type === 'user' ? 'items-start' : 'items-end'}`}>
                        <p className="text-xs font-semibold text-gray-600 mb-1 px-2">
                          {message.type === 'user' ? 'You' : 'AI Assistant'}
                        </p>
                        <div className={`max-w-[70%] rounded-2xl px-4 py-3 ${
                          message.type === 'user'
                            ? 'bg-blue-500 text-white'
                            : isError
                            ? 'bg-red-50 text-red-900 border border-red-200'
                            : 'bg-gray-100 text-gray-900'
                        }`}>
                          {message.type === 'user' ? (
                            <p className="text-xs">{message.text}</p>
                          ) : (
                            <>
                              <div className="text-xs prose prose-xs max-w-none prose-headings:mt-3 prose-headings:mb-2 prose-p:my-2 prose-ul:my-2 prose-li:my-0.5 prose-strong:font-bold prose-a:text-blue-600 hover:prose-a:text-blue-800">
                                <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.text}</ReactMarkdown>
                              </div>
                              {/* Graph Analysis Display */}
                              {message.metadata?.graph_analysis && message.metadata.graph_analysis.requires_graph && (
                                <div className="mt-3 pt-3 border-t border-gray-300">
                                  <div className="flex items-start gap-2 mb-2">
                                    <BarChart3 size={16} className="text-blue-600 mt-0.5" />
                                    <div className="flex-1">
                                      <p className="text-xs font-bold text-gray-800 mb-1">Data Visualization Available</p>
                                      <p className="text-xs text-gray-600 mb-2">{message.metadata.graph_analysis.reasoning}</p>
                                      <div className="bg-white border border-gray-200 rounded-lg p-2 text-xs">
                                        <div className="grid grid-cols-2 gap-2 mb-2">
                                          <div>
                                            <span className="font-semibold">Chart Type:</span>
                                            <span className="ml-1 text-gray-700">{message.metadata.graph_analysis.graph_type}</span>
                                          </div>
                                          <div>
                                            <span className="font-semibold">Library:</span>
                                            <span className="ml-1 text-gray-700">{message.metadata.graph_analysis.recommended_library || 'Plotly'}</span>
                                          </div>
                                        </div>
                                        {message.metadata.graph_analysis.sql_query && (
                                          <div className="mt-2">
                                            <p className="font-semibold mb-1">SQL Query:</p>
                                            <pre className="bg-gray-50 p-2 rounded text-[10px] overflow-x-auto font-mono">
                                              {message.metadata.graph_analysis.sql_query}
                                            </pre>
                                            <button
                                              onClick={() => {
                                                navigator.clipboard.writeText(message.metadata.graph_analysis.sql_query);
                                                addLog('SQL query copied to clipboard', 'success');
                                              }}
                                              className="mt-2 text-xs bg-blue-500 text-white px-2 py-1 rounded hover:bg-blue-600"
                                            >
                                              Copy SQL
                                            </button>
                                          </div>
                                        )}
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              )}
                            </>
                          )}
                        </div>
                        <p className={`text-xs mt-1 ${message.type === 'user' ? 'text-blue-100' : 'text-gray-500'}`}>
                          {message.timestamp}
                        </p>
                      </div>
                      );
                    })}
                    <div ref={messagesEndRef} />
                  </div>

                  {/* Input Area */}
                  <div className="p-4 border-t border-gray-200">
                    <div className="flex items-center gap-2 bg-gray-100 rounded-xl p-2">
                      <button className="p-2 hover:bg-gray-200 rounded-lg transition-colors">
                        <Paperclip size={20} className="text-gray-600" />
                      </button>
                      <input
                        type="text"
                        placeholder="Type your message..."
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                        className="flex-1 bg-transparent border-none outline-none px-2"
                      />
                      <button
                        onClick={handleSendMessage}
                        disabled={isSending}
                        className={`p-2 rounded-lg transition-colors ${
                          isSending
                            ? 'bg-gray-400 cursor-not-allowed'
                            : 'bg-blue-500 hover:bg-blue-600'
                        }`}
                      >
                        <Send size={20} className="text-white" />
                      </button>
                    </div>
                  </div>
                </div>

                {/* Console Logs Panel */}
                <div className="bg-gray-900 rounded-2xl shadow-sm flex flex-col" style={{ height: '280px' }}>
                  {/* Console Header */}
                  <div className="p-3 border-b border-gray-700 flex items-center justify-between">
                    <h3 className="text-sm font-bold text-gray-300 uppercase tracking-wide">System Console</h3>
                    <button
                      onClick={() => setConsoleLogs([])}
                      className="text-xs text-gray-500 hover:text-gray-300 px-2 py-1 rounded border border-gray-700 transition-colors"
                    >
                      Clear
                    </button>
                  </div>

                  {/* Console Output */}
                  <div className="flex-1 overflow-y-auto p-3 font-mono text-xs space-y-1 bg-gray-950">
                    {consoleLogs.length === 0 ? (
                      <div className="text-gray-500">No logs yet...</div>
                    ) : (
                      consoleLogs.map((log) => (
                        <div key={log.id} className="flex items-start gap-3">
                          <span className="text-gray-600 flex-shrink-0">[{log.timestamp}]</span>
                          <span className={`flex-shrink-0 font-bold ${log.level === 'error' ? 'text-red-400' :
                              log.level === 'success' ? 'text-green-400' :
                                log.level === 'warn' ? 'text-yellow-400' :
                                  'text-blue-400'
                            }`}>
                            {log.level.toUpperCase()}
                          </span>
                          <span className="text-gray-300 break-words">{log.message}</span>
                        </div>
                      ))
                    )}
                    <div ref={consoleEndRef} />
                  </div>
                </div>
              </div>
            </div>
          </>
        )}

        {activePage === 'analytics' && (
          <div className="space-y-6">
            <h1 className="text-3xl font-bold">Analytics Dashboard</h1>

            {/* Top Metrics Row */}
            <div className="grid grid-cols-4 gap-6">
              <div className="bg-white rounded-2xl shadow-sm p-6">
                <h3 className="text-sm font-medium text-gray-600 mb-2">Total Queries</h3>
                <p className="text-3xl font-bold">1,247</p>
                <p className="text-sm text-green-600 mt-2">↑ 12% from last week</p>
              </div>

              <div className="bg-white rounded-2xl shadow-sm p-6">
                <h3 className="text-sm font-medium text-gray-600 mb-2">Time Saved</h3>
                <p className="text-3xl font-bold">42.5 hrs</p>
                <p className="text-sm text-green-600 mt-2">↑ 8% from last week</p>
              </div>

              <div className="bg-white rounded-2xl shadow-sm p-6">
                <h3 className="text-sm font-medium text-gray-600 mb-2">Active Users</h3>
                <p className="text-3xl font-bold">89</p>
                <p className="text-sm text-green-600 mt-2">↑ 5% from last week</p>
              </div>

              <div className="bg-white rounded-2xl shadow-sm p-6">
                <h3 className="text-sm font-medium text-gray-600 mb-2">Automations Run</h3>
                <p className="text-3xl font-bold">324</p>
                <p className="text-sm text-green-600 mt-2">↑ 18% from last week</p>
              </div>
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-2 gap-6">
              {/* Most Used Workflows */}
              <div className="bg-white rounded-2xl shadow-sm p-6">
                <h3 className="text-lg font-bold mb-4">Most Used Workflows</h3>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="font-medium">Lookup Queries</span>
                      <span className="text-gray-600">487 uses</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-blue-500 h-2 rounded-full" style={{ width: '78%' }}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="font-medium">Report Generation</span>
                      <span className="text-gray-600">342 uses</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-green-500 h-2 rounded-full" style={{ width: '55%' }}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="font-medium">Automation</span>
                      <span className="text-gray-600">256 uses</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-purple-500 h-2 rounded-full" style={{ width: '41%' }}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="font-medium">Problem Solve</span>
                      <span className="text-gray-600">162 uses</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '26%' }}></div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Data Source Usage */}
              <div className="bg-white rounded-2xl shadow-sm p-6">
                <h3 className="text-lg font-bold mb-4">Data Source Usage</h3>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="font-medium">Gmail</span>
                      <span className="text-gray-600">892 queries</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-red-400 h-2 rounded-full" style={{ width: '85%' }}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="font-medium">Google Drive</span>
                      <span className="text-gray-600">654 queries</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-blue-400 h-2 rounded-full" style={{ width: '62%' }}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="font-medium">Salesforce</span>
                      <span className="text-gray-600">423 queries</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-cyan-400 h-2 rounded-full" style={{ width: '40%' }}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="font-medium">Excel Files</span>
                      <span className="text-gray-600">287 queries</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-green-400 h-2 rounded-full" style={{ width: '27%' }}></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* ROI Metrics */}
            <div className="bg-white rounded-2xl shadow-sm p-6">
              <h3 className="text-lg font-bold mb-4">ROI Metrics</h3>
              <div className="grid grid-cols-3 gap-8">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Avg. Time per Query</p>
                  <p className="text-2xl font-bold">2.3 min</p>
                  <p className="text-xs text-gray-500 mt-1">vs 15 min manual</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Estimated Cost Savings</p>
                  <p className="text-2xl font-bold">$12,450</p>
                  <p className="text-xs text-gray-500 mt-1">this month</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Productivity Increase</p>
                  <p className="text-2xl font-bold">87%</p>
                  <p className="text-xs text-gray-500 mt-1">compared to manual processes</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
