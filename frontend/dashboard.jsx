import React, { useState, useRef, useEffect } from 'react';
import * as XLSX from 'xlsx';
import {
  Search, Bell, ChevronDown, Send, Paperclip, Calendar, Plus,
  Mail, FolderOpen, Briefcase, FileSpreadsheet, Monitor,
  Lightbulb, TrendingUp, Zap, Menu, X, AlertTriangle, CheckCircle, Info,
  Eye, ClipboardList, Receipt, Maximize2, PanelRight, Terminal, ChevronUp
} from 'lucide-react';

export default function Dashboard() {
  const [activePage, setActivePage] = useState('dashboard');
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [expandedCategory, setExpandedCategory] = useState(null);
  const [selectedRole, setSelectedRole] = useState('Recruiter');
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);
  const [showCanvas, setShowCanvas] = useState(false);
  const [canvasTab, setCanvasTab] = useState('preview');
  const [uploadedFile, setUploadedFile] = useState(null);
  const [spreadsheetData, setSpreadsheetData] = useState(null);
  const [showReviewPanel, setShowReviewPanel] = useState(true);
  const [isTyping, setIsTyping] = useState(false);
  const [highlightedRow, setHighlightedRow] = useState(null);
  const [showConsole, setShowConsole] = useState(false);
  const [consoleLogs, setConsoleLogs] = useState([]);
  const messagesEndRef = useRef(null);
  const rowRefs = useRef({});
  const consoleEndRef = useRef(null);

  // Helper to add log entries to console
  const addLog = (type, message, data = null) => {
    const timestamp = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
    setConsoleLogs(prev => [...prev, { type, message, data, timestamp }]);
  };

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping, uploadedFile]);

  // Mock review issues - in production this would be AI-generated
  const reviewIssues = [
    { type: 'warning', message: 'Row 5: Hours exceed 12 per day - please verify', row: 5 },
    { type: 'warning', message: 'Row 8: Weekend work detected - confirm overtime rate applies', row: 8 },
    { type: 'info', message: 'Row 12: Break time not recorded', row: 12 },
    { type: 'success', message: 'All employee IDs match payroll records', row: null },
    { type: 'info', message: 'Total hours: 164.5 across 5 employees', row: null },
  ];

  // Toggle to show/hide Connected Sources panel
  const showConnectedSources = false;

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
      lookup: ['Find candidates with 5+ years experience', 'Search for active job openings', 'Locate candidate interview feedback'],
      problemSolve: ['Why are we losing candidates at offer stage?', 'Identify recruitment bottlenecks', 'Analyze time-to-hire trends'],
      report: ['Generate monthly placement report', 'Create candidate pipeline summary', 'Compile recruiter performance metrics'],
      automation: ['Timesheet to Invoice']
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
      id: 'automation',
      name: 'Automation',
      icon: Zap,
      color: 'bg-purple-100',
      examples: roleWorkflows[selectedRole].automation
    },
    {
      id: 'report',
      name: 'Report',
      icon: TrendingUp,
      color: 'bg-green-100',
      examples: roleWorkflows[selectedRole].report
    },
    {
      id: 'problem-solve',
      name: 'Problem Solve',
      icon: Lightbulb,
      color: 'bg-yellow-100',
      examples: roleWorkflows[selectedRole].problemSolve
    },
    {
      id: 'lookup',
      name: 'Lookup',
      icon: Search,
      color: 'bg-blue-100',
      examples: roleWorkflows[selectedRole].lookup
    }
  ];

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      addLog('info', `File selected: ${file.name}`, { size: file.size, type: file.type });
      setUploadedFile(file);
      setShowCanvas(true);
      setCanvasTab('preview');

      // Parse the spreadsheet
      const reader = new FileReader();
      reader.onload = (event) => {
        const data = new Uint8Array(event.target.result);
        const workbook = XLSX.read(data, { type: 'array' });
        const firstSheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[firstSheetName];
        const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
        setSpreadsheetData(jsonData);
        addLog('success', `Spreadsheet parsed: ${jsonData.length} rows`, { sheet: firstSheetName });
      };
      reader.readAsArrayBuffer(file);
    }
  };

  // Handle clicking on a review issue to highlight the row
  const handleReviewIssueClick = (row) => {
    if (row !== null) {
      setHighlightedRow(row);
      // Scroll to the highlighted row
      if (rowRefs.current[row]) {
        rowRefs.current[row].scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  };

  // Handle cell edit
  const handleCellEdit = (rowIdx, colIdx, value) => {
    const newData = [...spreadsheetData];
    // rowIdx is 0-based from slice(1), so actual index is rowIdx + 1
    newData[rowIdx + 1][colIdx] = value;
    setSpreadsheetData(newData);
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = inputMessage;
    const timestamp = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });

    addLog('info', `Sending message: "${userMessage.substring(0, 50)}${userMessage.length > 50 ? '...' : ''}"`);

    // Add user message to chat
    setMessages(prev => [...prev, {
      id: prev.length + 1,
      type: 'user',
      text: userMessage,
      timestamp
    }]);

    // Clear input immediately and show typing indicator
    setInputMessage('');
    setIsTyping(true);

    try {
      addLog('info', 'Calling backend API...');
      // Call backend API
      const response = await fetch('http://localhost:3001/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          sessionId: 'elephant-session-1', // Could be dynamic per user
          useHistory: true // Maintain conversation context
        })
      });

      const data = await response.json();
      setIsTyping(false);

      if (data.success) {
        addLog('success', 'Received AI response', { length: data.message?.length });
        // Add AI response to chat
        setMessages(prev => [...prev, {
          id: prev.length + 1,
          type: 'ai',
          text: data.message,
          timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false }),
          metadata: data.metadata
        }]);
      } else {
        addLog('error', `API error: ${data.error || 'Unknown error'}`);
        // Handle error response
        setMessages(prev => [...prev, {
          id: prev.length + 1,
          type: 'ai',
          text: `Error: ${data.error || 'Failed to get response'}`,
          timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false })
        }]);
      }
    } catch (error) {
      console.error('Chat error:', error);
      addLog('error', `Connection error: ${error.message}`);
      setIsTyping(false);
      // Add error message to chat
      setMessages(prev => [...prev, {
        id: prev.length + 1,
        type: 'ai',
        text: 'Sorry, I encountered an error connecting to the server. Please try again.',
        timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false })
      }]);
    }
  };

  return (
    <div className="h-screen bg-gradient-to-br from-gray-100 to-gray-200 p-4 pb-14 flex flex-col overflow-hidden">
      <div className="w-full flex flex-col flex-1 min-h-0">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-sm p-4 mb-4 flex-shrink-0">
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
          <React.Fragment>
        {/* Connected Sources - Horizontal Bar */}
        {showConnectedSources && (
          <div className="bg-white rounded-2xl shadow-sm p-3 mb-4 flex-shrink-0">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-lg font-bold">Connected Sources</h2>
              <button className="flex items-center gap-2 text-xs text-gray-600 border border-gray-300 px-2 py-1 rounded-lg hover:bg-gray-50">
                <Calendar size={14} />
                Last 7 days
              </button>
            </div>

            <div className="grid grid-cols-5 gap-3 mb-3">
              {connectedSources.map((source, index) => {
                const IconComponent = source.icon;
                return (
                  <div key={index} className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 transition-colors border border-gray-200">
                    <div className={`w-10 h-10 ${source.color} rounded-lg flex items-center justify-center flex-shrink-0`}>
                      <IconComponent size={20} className="text-gray-700" />
                    </div>
                    <div className="min-w-0">
                      <div className="font-semibold text-sm truncate">{source.name}</div>
                      <div className="text-xs text-gray-500">{source.count}</div>
                    </div>
                    <div className="text-green-600 text-xs ml-auto">●</div>
                  </div>
                );
              })}
            </div>

            <button className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-2 rounded-lg transition-colors text-sm">
              + Add New Source
            </button>
          </div>
        )}

        {/* Chat Interface with Canvas */}
        <div className="flex gap-4 flex-1 min-h-0">
          {/* Chat - shrinks when canvas is open */}
          <div className={`bg-white rounded-2xl shadow-sm flex flex-col transition-all duration-300 ${showCanvas ? 'w-1/3' : 'w-full'}`}>
          {/* Chat Header with Action Tabs */}
          <div className="p-4 border-b border-gray-200 flex items-center justify-between">
            {showCanvas && selectedWorkflow ? (
              // Show only the active workflow tab when canvas is open
              <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-gray-100 w-fit">
                <Zap size={16} className="text-purple-600" />
                <span className="text-sm font-medium text-gray-900">{selectedWorkflow.category}</span>
              </div>
            ) : (
              // Show all workflow tabs when canvas is closed
              <div className="flex items-center gap-2">
                {workflowCategories.map((category) => {
                  const CategoryIcon = category.icon;
                  return (
                    <div key={category.id} className="relative">
                      <button
                        onClick={() => setExpandedCategory(expandedCategory === category.id ? null : category.id)}
                        className={`flex items-center gap-3 px-4 py-2 rounded-full border transition-colors ${
                          expandedCategory === category.id
                            ? 'border-gray-400 bg-gray-50'
                            : 'border-gray-200 hover:bg-gray-50'
                        }`}
                      >
                        <div className={`w-8 h-8 ${category.color} rounded-full flex items-center justify-center`}>
                          <CategoryIcon size={16} className="text-gray-700" />
                        </div>
                        <span className="font-semibold text-gray-900">{category.name}</span>
                        <ChevronDown
                          size={16}
                          className={`transition-transform text-gray-500 ${expandedCategory === category.id ? 'rotate-180' : ''}`}
                        />
                      </button>

                      {expandedCategory === category.id && (
                        <div className="absolute top-full left-0 mt-2 w-72 bg-white rounded-2xl shadow-lg border border-gray-200 z-10 py-2">
                          {category.examples.map((example, idx) => (
                            <button
                              key={idx}
                              onClick={() => {
                                setSelectedWorkflow({ category: category.name, workflow: example });
                                setExpandedCategory(null);
                              }}
                              className="w-full text-left text-sm px-4 py-2 hover:bg-gray-100 transition-colors text-gray-700"
                            >
                              {example}
                            </button>
                          ))}
                          <div className="border-t border-gray-200 mt-2 pt-2">
                            <button className="w-full text-left text-sm px-4 py-2 hover:bg-gray-100 transition-colors text-blue-600 flex items-center gap-2">
                              <Plus size={16} />
                              Add custom query
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
            {showCanvas ? (
              <button
                onClick={() => setShowCanvas(false)}
                className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                title="Expand chat"
              >
                <Maximize2 size={18} className="text-gray-500" />
              </button>
            ) : (
              <button
                onClick={() => setShowCanvas(true)}
                className="flex items-center gap-2 px-3 py-1.5 hover:bg-gray-100 rounded-full transition-colors"
                title="Open canvas"
              >
                <PanelRight size={18} className="text-gray-500" />
                <span className="text-sm text-gray-600">Canvas</span>
              </button>
            )}
          </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {/* Empty state */}
              {!selectedWorkflow && messages.length === 0 && !uploadedFile && (
                <div className="h-full flex flex-col items-center justify-center text-center">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                    <Zap size={28} className="text-gray-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-700 mb-2">Start a conversation</h3>
                  <p className="text-sm text-gray-500 max-w-sm">
                    Select a workflow above or type a message to get started.
                  </p>
                </div>
              )}
              {selectedWorkflow && (
                <>
                  <div className="flex items-center justify-center">
                    <div className="inline-flex items-center gap-2 bg-purple-50 border border-purple-200 rounded-full px-4 py-2">
                      <Zap size={16} className="text-purple-600" />
                      <span className="text-sm font-medium text-purple-700">
                        {selectedWorkflow.category}: {selectedWorkflow.workflow}
                      </span>
                      <button
                        onClick={() => setSelectedWorkflow(null)}
                        className="ml-1 text-purple-400 hover:text-purple-600"
                      >
                        ×
                      </button>
                    </div>
                  </div>
                  <div className="flex flex-col items-end">
                    <p className="text-xs font-semibold text-gray-600 mb-1 px-2">AI Assistant</p>
                    <div className="max-w-[70%] bg-gray-100 text-gray-900 rounded-2xl px-4 py-3">
                      <p className="text-sm">Please add timesheet below</p>
                    </div>
                  </div>
                </>
              )}
              {messages.map((message) => (
                <div key={message.id} className={`flex flex-col ${message.type === 'user' ? 'items-start' : 'items-end'}`}>
                  <p className="text-xs font-semibold text-gray-600 mb-1 px-2">
                    {message.type === 'user' ? 'You' : 'AI Assistant'}
                  </p>
                  <div className={`max-w-[70%] ${message.type === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-900'} rounded-2xl px-4 py-3`}>
                    <p className="text-sm">{message.text}</p>
                    <p className={`text-xs mt-1 ${message.type === 'user' ? 'text-blue-100' : 'text-gray-500'}`}>
                      {message.timestamp}
                    </p>
                  </div>
                </div>
              ))}
              {/* Uploaded file message */}
              {uploadedFile && (
                <div className="flex flex-col items-start">
                  <p className="text-xs font-semibold text-gray-600 mb-1 px-2">You</p>
                  <div className="max-w-[70%] bg-blue-500 text-white rounded-2xl px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
                        <FileSpreadsheet size={20} className="text-white" />
                      </div>
                      <div>
                        <p className="text-sm font-medium">{uploadedFile.name}</p>
                        <p className="text-xs text-blue-100">
                          {(uploadedFile.size / 1024).toFixed(1)} KB • Spreadsheet
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              {/* Typing indicator */}
              {isTyping && (
                <div className="flex flex-col items-end">
                  <p className="text-xs font-semibold text-gray-600 mb-1 px-2">AI Assistant</p>
                  <div className="bg-gray-100 rounded-2xl px-4 py-3">
                    <div className="flex items-center gap-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                  </div>
                </div>
              )}
              {/* Auto-scroll anchor */}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 border-t border-gray-200">
              <div className="flex items-center gap-2 bg-gray-100 rounded-full p-2">
                <label className="p-2 hover:bg-gray-200 rounded-full transition-colors cursor-pointer">
                  <Paperclip size={20} className="text-gray-600" />
                  <input
                    type="file"
                    accept=".xlsx,.xls,.csv"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                </label>
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
                  className="p-2 bg-blue-500 hover:bg-blue-600 rounded-full transition-colors"
                >
                  <Send size={20} className="text-white" />
                </button>
              </div>
            </div>
          </div>

          {/* Canvas Panel */}
          {showCanvas && (
            <div className="w-2/3 bg-white rounded-2xl shadow-sm flex flex-col">
              {/* Canvas Header */}
              <div className="p-4 border-b border-gray-200 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {[
                    { id: 'preview', name: 'Preview', icon: Eye, color: 'bg-blue-100', iconColor: 'text-blue-600' },
                    { id: 'summary', name: 'Summary', icon: ClipboardList, color: 'bg-green-100', iconColor: 'text-green-600' },
                    { id: 'invoice', name: 'Invoice', icon: Receipt, color: 'bg-orange-100', iconColor: 'text-orange-600' }
                  ].map((tab) => {
                    const TabIcon = tab.icon;
                    return (
                      <button
                        key={tab.id}
                        onClick={() => setCanvasTab(tab.id)}
                        className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                          canvasTab === tab.id
                            ? 'bg-gray-200'
                            : 'bg-gray-100 hover:bg-gray-150'
                        }`}
                      >
                        <div className={`w-6 h-6 ${tab.color} rounded-full flex items-center justify-center`}>
                          <TabIcon size={14} className={tab.iconColor} />
                        </div>
                        <span className="text-gray-900">{tab.name}</span>
                      </button>
                    );
                  })}
                </div>
                <button
                  onClick={() => setShowCanvas(false)}
                  className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                >
                  <X size={20} className="text-gray-500" />
                </button>
              </div>

              {/* Canvas Content */}
              <div className="flex-1 overflow-hidden flex">
                {canvasTab === 'preview' && (
                  <div className="h-full flex flex-1 min-w-0 relative">
                    {/* Spreadsheet Table */}
                    {spreadsheetData && spreadsheetData.length > 0 ? (
                      <div className={`overflow-auto h-full p-4 ${showReviewPanel ? 'flex-1' : 'w-full'}`}>
                        <table className="w-full border-collapse text-sm">
                          <thead className="sticky top-0 bg-gray-100">
                            <tr>
                              {spreadsheetData[0].map((header, idx) => (
                                <th key={idx} className="border border-gray-300 px-3 py-2 text-left font-semibold text-gray-700 whitespace-nowrap">
                                  {header || `Column ${idx + 1}`}
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {spreadsheetData.slice(1).map((row, rowIdx) => {
                              const actualRowNum = rowIdx + 2; // +1 for header, +1 for 1-based indexing
                              const isHighlighted = highlightedRow === actualRowNum - 1; // reviewIssues use 1-based row numbers after header
                              return (
                                <tr
                                  key={rowIdx}
                                  ref={el => rowRefs.current[actualRowNum - 1] = el}
                                  className={`transition-colors ${
                                    isHighlighted
                                      ? 'bg-amber-100 ring-2 ring-amber-400 ring-inset'
                                      : rowIdx % 2 === 0 ? 'bg-white' : 'bg-gray-50'
                                  }`}
                                  onClick={() => setHighlightedRow(null)}
                                >
                                  {spreadsheetData[0].map((_, colIdx) => (
                                    <td key={colIdx} className="border border-gray-300 px-0 py-0 text-gray-600">
                                      <input
                                        type="text"
                                        value={row[colIdx] !== undefined ? row[colIdx] : ''}
                                        onChange={(e) => handleCellEdit(rowIdx, colIdx, e.target.value)}
                                        className={`w-full px-3 py-2 bg-transparent border-none outline-none focus:bg-blue-50 focus:ring-2 focus:ring-blue-400 focus:ring-inset ${
                                          isHighlighted ? 'bg-amber-100' : ''
                                        }`}
                                      />
                                    </td>
                                  ))}
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <div className="h-full flex-1 flex flex-col items-center justify-center text-gray-500 p-4">
                        <FileSpreadsheet size={48} className="mb-4 text-gray-300" />
                        <p className="text-lg font-medium">{uploadedFile?.name || 'Spreadsheet Preview'}</p>
                        <p className="text-sm">Loading spreadsheet data...</p>
                      </div>
                    )}

                    {/* Review Panel Toggle Button */}
                    {!showReviewPanel && spreadsheetData && (
                      <button
                        onClick={() => setShowReviewPanel(true)}
                        className="absolute right-4 bottom-4 flex items-center gap-2 px-4 py-2.5 bg-purple-500 hover:bg-purple-600 rounded-full shadow-lg transition-colors"
                      >
                        <div className="w-6 h-6 rounded-full bg-white/20 flex items-center justify-center">
                          <Lightbulb size={14} className="text-white" />
                        </div>
                        <span className="text-sm font-semibold text-white">Review</span>
                      </button>
                    )}

                    {/* Review Panel */}
                    {showReviewPanel && spreadsheetData && (
                      <div className="w-72 border-l border-gray-200 bg-white flex flex-col h-full flex-shrink-0">
                        <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <div className="w-6 h-6 rounded-full bg-purple-100 flex items-center justify-center">
                              <Lightbulb size={12} className="text-purple-600" />
                            </div>
                            <h3 className="font-medium text-gray-900 text-sm">Review</h3>
                          </div>
                          <button
                            onClick={() => setShowReviewPanel(false)}
                            className="p-1.5 hover:bg-gray-100 rounded-full transition-colors"
                          >
                            <X size={14} className="text-gray-400" />
                          </button>
                        </div>
                        <div className="flex-1 overflow-auto p-3 space-y-2">
                          {reviewIssues.map((issue, idx) => (
                            <div
                              key={idx}
                              onClick={() => handleReviewIssueClick(issue.row)}
                              className={`p-3 rounded-2xl transition-colors cursor-pointer ${
                                highlightedRow === issue.row
                                  ? 'bg-amber-100 ring-2 ring-amber-400'
                                  : 'bg-gray-50 hover:bg-gray-100'
                              } ${issue.row === null ? 'cursor-default' : ''}`}
                            >
                              <div className="flex items-start gap-3">
                                <div className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 ${
                                  issue.type === 'warning'
                                    ? 'bg-amber-100'
                                    : issue.type === 'success'
                                    ? 'bg-green-100'
                                    : 'bg-blue-100'
                                }`}>
                                  {issue.type === 'warning' && (
                                    <AlertTriangle size={11} className="text-amber-600" />
                                  )}
                                  {issue.type === 'success' && (
                                    <CheckCircle size={11} className="text-green-600" />
                                  )}
                                  {issue.type === 'info' && (
                                    <Info size={11} className="text-blue-600" />
                                  )}
                                </div>
                                <div className="flex-1">
                                  <p className="text-sm text-gray-700 leading-relaxed">
                                    {issue.message}
                                  </p>
                                  {issue.row !== null && (
                                    <p className="text-xs text-gray-400 mt-1">Click to highlight row</p>
                                  )}
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                        <div className="p-3 border-t border-gray-100">
                          <button className="w-full bg-blue-500 hover:bg-blue-600 text-white py-2.5 px-4 rounded-full text-sm font-medium transition-colors">
                            Confirm & Continue
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                )}
                {canvasTab === 'summary' && (
                  <div className="h-full w-full flex flex-col items-center justify-center text-gray-500">
                    <TrendingUp size={48} className="mb-4 text-gray-300" />
                    <p className="text-lg font-medium">Summary</p>
                    <p className="text-sm">Data summary will appear here</p>
                  </div>
                )}
                {canvasTab === 'invoice' && (
                  <div className="h-full w-full flex flex-col items-center justify-center text-gray-500">
                    <FileSpreadsheet size={48} className="mb-4 text-gray-300" />
                    <p className="text-lg font-medium">Invoice</p>
                    <p className="text-sm">Generated invoice will appear here</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
        </React.Fragment>
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

      {/* System Console */}
      <div className={`fixed bottom-0 left-0 right-0 bg-gray-900 text-gray-100 transition-all duration-300 ${showConsole ? 'h-48' : 'h-10'}`}>
        {/* Console Header */}
        <div
          className="h-10 px-4 flex items-center justify-between border-b border-gray-700 cursor-pointer hover:bg-gray-800"
          onClick={() => setShowConsole(!showConsole)}
        >
          <div className="flex items-center gap-2">
            <Terminal size={16} className="text-green-400" />
            <span className="text-sm font-medium">System Console</span>
            <span className="text-xs text-gray-500">({consoleLogs.length} logs)</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={(e) => { e.stopPropagation(); setConsoleLogs([]); }}
              className="text-xs text-gray-500 hover:text-gray-300 px-2 py-1"
            >
              Clear
            </button>
            <ChevronUp size={16} className={`text-gray-400 transition-transform ${showConsole ? '' : 'rotate-180'}`} />
          </div>
        </div>
        {/* Console Content */}
        {showConsole && (
          <div className="h-[calc(100%-40px)] overflow-auto p-2 font-mono text-xs">
            {consoleLogs.length === 0 ? (
              <p className="text-gray-500 text-center py-4">No logs yet. Interact with the app to see events.</p>
            ) : (
              consoleLogs.map((log, idx) => (
                <div key={idx} className="flex gap-2 py-0.5 hover:bg-gray-800 px-2 rounded">
                  <span className="text-gray-500 flex-shrink-0">{log.timestamp}</span>
                  <span className={`flex-shrink-0 ${
                    log.type === 'error' ? 'text-red-400' :
                    log.type === 'success' ? 'text-green-400' :
                    log.type === 'warning' ? 'text-yellow-400' :
                    'text-blue-400'
                  }`}>
                    [{log.type.toUpperCase()}]
                  </span>
                  <span className="text-gray-100">{log.message}</span>
                  {log.data && (
                    <span className="text-gray-500">{JSON.stringify(log.data)}</span>
                  )}
                </div>
              ))
            )}
            <div ref={consoleEndRef} />
          </div>
        )}
      </div>
    </div>
  );
}
