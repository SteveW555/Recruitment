import React, { useState } from 'react';
import { Mail, AlertCircle } from 'lucide-react';
import EmailSearch from './EmailSearch';
import EmailList from './EmailList';
import EmailPreview from './EmailPreview';
import gmailApi from '../lib/gmail-api-client';

/**
 * Gmail Email Search & CV Extraction App
 * Main application component integrating all features
 */
export default function GmailApp() {
  const [emails, setEmails] = useState([]);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState(null);
  const [searchResultsInfo, setSearchResultsInfo] = useState(null);

  const handleSearch = async (searchParams) => {
    setIsSearching(true);
    setError(null);
    setSelectedEmail(null);

    try {
      const response = await gmailApi.searchEmails(searchParams);

      if (response.success) {
        setEmails(response.data.emails || []);
        setSearchResultsInfo({
          totalResults: response.data.totalResults,
          resultSizeEstimate: response.data.resultSizeEstimate,
          nextPageToken: response.data.nextPageToken,
        });
      } else {
        throw new Error(response.message || 'Search failed');
      }
    } catch (err) {
      setError(err.message || 'Failed to search emails');
      setEmails([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleClear = () => {
    setEmails([]);
    setSelectedEmail(null);
    setError(null);
    setSearchResultsInfo(null);
  };

  const handleSelectEmail = (email) => {
    setSelectedEmail(email);
  };

  const handleClosePreview = () => {
    setSelectedEmail(null);
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center">
            <Mail className="text-blue-600 mr-3" size={32} />
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Gmail Email Search & CV Extraction
              </h1>
              <p className="text-gray-600 mt-1">
                Search your Gmail inbox for emails and CV attachments
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 gap-6">
          {/* Search Form */}
          <EmailSearch
            onSearch={handleSearch}
            onClear={handleClear}
            isLoading={isSearching}
          />

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-start">
                <AlertCircle className="text-red-600 mr-3 flex-shrink-0 mt-0.5" size={20} />
                <div>
                  <h3 className="text-red-800 font-semibold">Error</h3>
                  <p className="text-red-700 text-sm mt-1">{error}</p>
                </div>
              </div>
            </div>
          )}

          {/* Results Section */}
          {(emails.length > 0 || searchResultsInfo) && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Email List */}
              <div className="lg:h-[calc(100vh-320px)]">
                <EmailList
                  emails={emails}
                  onSelectEmail={handleSelectEmail}
                  selectedEmail={selectedEmail}
                  isLoading={isSearching}
                />
              </div>

              {/* Email Preview */}
              <div className="lg:h-[calc(100vh-320px)]">
                {selectedEmail ? (
                  <EmailPreview
                    emailId={selectedEmail.id}
                    onClose={handleClosePreview}
                  />
                ) : (
                  <div className="bg-white rounded-lg shadow-md p-8 flex items-center justify-center h-full">
                    <div className="text-center text-gray-500">
                      <Mail size={64} className="mx-auto mb-4 text-gray-300" />
                      <p className="text-lg">Select an email to view its content</p>
                      <p className="text-sm mt-2">
                        Click on any email from the list to see the full preview
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Welcome/Empty State */}
          {emails.length === 0 && !isSearching && !error && (
            <div className="bg-white rounded-lg shadow-md p-12">
              <div className="text-center text-gray-500">
                <Mail size={96} className="mx-auto mb-6 text-gray-300" />
                <h2 className="text-2xl font-semibold text-gray-700 mb-3">
                  Welcome to Gmail Email Search
                </h2>
                <p className="text-gray-600 mb-4">
                  Use the search form above to find emails in your Gmail inbox
                </p>

                <div className="max-w-2xl mx-auto mt-8 text-left">
                  <h3 className="text-lg font-semibold text-gray-800 mb-3">Features:</h3>
                  <ul className="space-y-2 text-gray-600">
                    <li className="flex items-start">
                      <span className="text-blue-600 mr-2">✓</span>
                      <span>Search emails by date range, sender, and subject</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-blue-600 mr-2">✓</span>
                      <span>Filter emails with attachments (CVs, documents)</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-blue-600 mr-2">✓</span>
                      <span>Preview full email content with HTML rendering</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-blue-600 mr-2">✓</span>
                      <span>Download individual attachments or bulk download</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-blue-600 mr-2">✓</span>
                      <span>Advanced filtering with saved searches (coming soon)</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="max-w-7xl mx-auto mt-6">
        <div className="text-center text-sm text-gray-500">
          <p>ProActive People - Gmail Email Search & CV Extraction Service</p>
          <p className="mt-1">
            Powered by Google Gmail API • Built with React & NestJS
          </p>
        </div>
      </div>
    </div>
  );
}
