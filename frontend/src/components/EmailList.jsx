import React from 'react';
import { Mail, Paperclip, Star, Calendar, User, FileText, ChevronRight } from 'lucide-react';

/**
 * Email List Component
 * Displays search results in a list format
 */
export default function EmailList({ emails, onSelectEmail, selectedEmail, isLoading }) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Loading emails...</span>
        </div>
      </div>
    );
  }

  if (!emails || emails.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8">
        <div className="text-center text-gray-500">
          <Mail size={48} className="mx-auto mb-3 text-gray-400" />
          <p className="text-lg">No emails found</p>
          <p className="text-sm mt-2">Try adjusting your search filters</p>
        </div>
      </div>
    );
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
      return date.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
    } else if (diffDays === 1) {
      return 'Yesterday';
    } else if (diffDays < 7) {
      return date.toLocaleDateString('en-GB', { weekday: 'short' });
    } else {
      return date.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' });
    }
  };

  const truncate = (text, maxLength = 100) => {
    if (!text) return '';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="p-4 bg-gray-50 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-800 flex items-center">
            <Mail className="mr-2" size={20} />
            Search Results ({emails.length})
          </h3>
        </div>
      </div>

      <div className="divide-y divide-gray-200">
        {emails.map((email) => {
          const isSelected = selectedEmail?.id === email.id;
          const isUnread = !email.isRead;
          const isCVEmail = email.isCVEmail || false;

          return (
            <div
              key={email.id}
              onClick={() => onSelectEmail(email)}
              className={`
                p-4 cursor-pointer transition-colors hover:bg-blue-50
                ${isSelected ? 'bg-blue-100 border-l-4 border-l-blue-600' : ''}
                ${isUnread ? 'bg-blue-50/50' : ''}
              `}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  {/* Header: From + Date */}
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center flex-1 min-w-0">
                      <User size={14} className="mr-1 text-gray-500 flex-shrink-0" />
                      <span className={`text-sm truncate ${isUnread ? 'font-semibold text-gray-900' : 'font-medium text-gray-700'}`}>
                        {email.from.name || email.from.email}
                      </span>
                    </div>

                    <div className="flex items-center gap-2 ml-2 flex-shrink-0">
                      {email.isStarred && (
                        <Star size={14} className="text-yellow-500 fill-current" />
                      )}
                      {isCVEmail && (
                        <span className="px-1.5 py-0.5 bg-green-100 text-green-700 text-xs rounded font-medium">
                          CV
                        </span>
                      )}
                      <Calendar size={14} className="text-gray-400" />
                      <span className="text-xs text-gray-500">
                        {formatDate(email.date)}
                      </span>
                    </div>
                  </div>

                  {/* Subject */}
                  <div className="mb-1">
                    <h4 className={`text-sm leading-tight ${isUnread ? 'font-bold text-gray-900' : 'font-medium text-gray-800'}`}>
                      {email.subject || '(No Subject)'}
                    </h4>
                  </div>

                  {/* Snippet */}
                  <div className="flex items-start justify-between">
                    <p className="text-xs text-gray-600 line-clamp-2 flex-1">
                      {truncate(email.snippet, 150)}
                    </p>
                  </div>

                  {/* Footer: Attachments + Labels */}
                  <div className="flex items-center gap-3 mt-2">
                    {email.hasAttachments && (
                      <div className="flex items-center text-xs text-gray-500">
                        <Paperclip size={12} className="mr-1" />
                        {email.attachmentCount || 1}
                      </div>
                    )}

                    {email.labels && email.labels.length > 0 && (
                      <div className="flex items-center gap-1">
                        {email.labels.slice(0, 3).map((label, index) => (
                          <span
                            key={index}
                            className="px-1.5 py-0.5 bg-gray-100 text-gray-600 text-xs rounded"
                          >
                            {label.replace('CATEGORY_', '').toLowerCase()}
                          </span>
                        ))}
                        {email.labels.length > 3 && (
                          <span className="text-xs text-gray-500">
                            +{email.labels.length - 3}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>

                {/* Selection Indicator */}
                <div className="ml-3 flex-shrink-0">
                  <ChevronRight
                    size={20}
                    className={`text-gray-400 ${isSelected ? 'text-blue-600' : ''}`}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Pagination placeholder */}
      {emails.length >= 50 && (
        <div className="p-4 bg-gray-50 border-t border-gray-200">
          <div className="text-center text-sm text-gray-600">
            <p>Showing {emails.length} results</p>
            <button className="mt-2 text-blue-600 hover:text-blue-700 font-medium">
              Load More
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
