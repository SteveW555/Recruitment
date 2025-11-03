import React, { useState, useEffect } from 'react';
import {
  Mail,
  User,
  Calendar,
  Paperclip,
  Download,
  Star,
  MessageSquare,
  X,
  AlertCircle,
  FileText,
} from 'lucide-react';
import gmailApi from '../lib/gmail-api-client';

/**
 * Email Preview Component
 * Displays full email content with HTML rendering and attachments
 */
export default function EmailPreview({ emailId, onClose }) {
  const [preview, setPreview] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showHtml, setShowHtml] = useState(true);
  const [downloadingAttachments, setDownloadingAttachments] = useState(new Set());

  useEffect(() => {
    if (emailId) {
      loadEmailPreview();
    }
  }, [emailId]);

  const loadEmailPreview = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await gmailApi.getEmailPreview(emailId);
      setPreview(response.data);
    } catch (err) {
      setError(err.message || 'Failed to load email preview');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownloadAttachment = async (attachment) => {
    setDownloadingAttachments((prev) => new Set(prev).add(attachment.attachmentId));

    try {
      // First, download the attachment to backend
      const downloadResponse = await gmailApi.downloadAttachment(
        emailId,
        attachment.attachmentId,
        attachment.filename
      );

      // Then, get the file and trigger browser download
      const blob = await gmailApi.getDownloadedFile(downloadResponse.data.downloadId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = attachment.filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      alert(`Failed to download attachment: ${err.message}`);
    } finally {
      setDownloadingAttachments((prev) => {
        const next = new Set(prev);
        next.delete(attachment.attachmentId);
        return next;
      });
    }
  };

  const handleDownloadAll = async () => {
    if (!preview?.attachments || preview.attachments.length === 0) return;

    try {
      // Download all attachments
      const attachments = preview.attachments.map((a) => ({
        attachmentId: a.attachmentId,
        filename: a.filename,
      }));

      const downloadResponse = await gmailApi.downloadEmailAttachments(emailId, attachments);

      const downloadIds = downloadResponse.data.downloads.map((d) => d.downloadId);

      // Create ZIP and download
      const zipBlob = await gmailApi.bulkDownload(downloadIds);
      const url = window.URL.createObjectURL(zipBlob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `attachments-${emailId}.zip`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      alert(`Failed to download attachments: ${err.message}`);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-GB', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  if (!emailId) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 flex items-center justify-center h-full">
        <div className="text-center text-gray-500">
          <Mail size={64} className="mx-auto mb-4 text-gray-300" />
          <p className="text-lg">Select an email to view</p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 flex items-center justify-center h-full">
        <div className="flex flex-col items-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
          <span className="text-gray-600">Loading email...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8">
        <div className="flex items-center text-red-600 mb-4">
          <AlertCircle className="mr-2" size={24} />
          <h3 className="text-lg font-semibold">Error Loading Email</h3>
        </div>
        <p className="text-gray-700 mb-4">{error}</p>
        <button
          onClick={loadEmailPreview}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!preview) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden h-full flex flex-col">
      {/* Header */}
      <div className="p-4 bg-gray-50 border-b border-gray-200">
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1">
            <h2 className="text-xl font-bold text-gray-900 mb-2 pr-8">
              {preview.subject || '(No Subject)'}
            </h2>

            {preview.isCVEmail && (
              <span className="inline-flex items-center px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full font-medium mb-2">
                <FileText size={12} className="mr-1" />
                CV Email
              </span>
            )}
          </div>

          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 flex-shrink-0"
          >
            <X size={24} />
          </button>
        </div>

        {/* From/To/Date */}
        <div className="space-y-2 text-sm">
          <div className="flex items-center">
            <User size={14} className="mr-2 text-gray-500" />
            <span className="font-medium text-gray-700">From:</span>
            <span className="ml-2 text-gray-900">
              {preview.from.name ? `${preview.from.name} <${preview.from.email}>` : preview.from.email}
            </span>
          </div>

          <div className="flex items-center">
            <Mail size={14} className="mr-2 text-gray-500" />
            <span className="font-medium text-gray-700">To:</span>
            <span className="ml-2 text-gray-900">
              {preview.to.map((addr) => addr.email).join(', ')}
            </span>
          </div>

          {preview.cc && preview.cc.length > 0 && (
            <div className="flex items-center">
              <MessageSquare size={14} className="mr-2 text-gray-500" />
              <span className="font-medium text-gray-700">Cc:</span>
              <span className="ml-2 text-gray-900">
                {preview.cc.map((addr) => addr.email).join(', ')}
              </span>
            </div>
          )}

          <div className="flex items-center">
            <Calendar size={14} className="mr-2 text-gray-500" />
            <span className="font-medium text-gray-700">Date:</span>
            <span className="ml-2 text-gray-900">{formatDate(preview.date)}</span>
          </div>
        </div>

        {/* Flags */}
        <div className="flex items-center gap-2 mt-3">
          {preview.isStarred && (
            <span className="flex items-center px-2 py-1 bg-yellow-100 text-yellow-700 text-xs rounded">
              <Star size={12} className="mr-1 fill-current" />
              Starred
            </span>
          )}
          {!preview.isRead && (
            <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
              Unread
            </span>
          )}
          {preview.cached && (
            <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
              Cached
            </span>
          )}
        </div>
      </div>

      {/* Attachments */}
      {preview.attachments && preview.attachments.length > 0 && (
        <div className="p-4 bg-blue-50 border-b border-blue-200">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold text-gray-800 flex items-center">
              <Paperclip size={16} className="mr-1" />
              Attachments ({preview.attachments.length})
            </h3>
            {preview.attachments.length > 1 && (
              <button
                onClick={handleDownloadAll}
                className="text-xs text-blue-600 hover:text-blue-700 font-medium flex items-center"
              >
                <Download size={12} className="mr-1" />
                Download All
              </button>
            )}
          </div>

          <div className="space-y-2">
            {preview.attachments.map((attachment) => {
              const isDownloading = downloadingAttachments.has(attachment.attachmentId);

              return (
                <div
                  key={attachment.attachmentId}
                  className="flex items-center justify-between p-2 bg-white rounded border border-blue-200"
                >
                  <div className="flex items-center flex-1 min-w-0">
                    <Paperclip size={14} className="mr-2 text-gray-500 flex-shrink-0" />
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {attachment.filename}
                      </p>
                      <p className="text-xs text-gray-500">
                        {attachment.mimeType} • {formatFileSize(attachment.size)}
                      </p>
                    </div>
                  </div>

                  <button
                    onClick={() => handleDownloadAttachment(attachment)}
                    disabled={isDownloading}
                    className="ml-2 px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-blue-300 flex items-center flex-shrink-0"
                  >
                    {isDownloading ? (
                      <>
                        <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white mr-1"></div>
                        Downloading...
                      </>
                    ) : (
                      <>
                        <Download size={12} className="mr-1" />
                        Download
                      </>
                    )}
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Body Toggle */}
      {preview.body.html && preview.body.text && (
        <div className="px-4 py-2 bg-gray-100 border-b border-gray-200 flex items-center gap-2">
          <span className="text-xs text-gray-600">View:</span>
          <button
            onClick={() => setShowHtml(true)}
            className={`px-3 py-1 text-xs rounded ${showHtml ? 'bg-white text-blue-600 font-medium' : 'text-gray-600 hover:bg-gray-200'}`}
          >
            HTML
          </button>
          <button
            onClick={() => setShowHtml(false)}
            className={`px-3 py-1 text-xs rounded ${!showHtml ? 'bg-white text-blue-600 font-medium' : 'text-gray-600 hover:bg-gray-200'}`}
          >
            Plain Text
          </button>
        </div>
      )}

      {/* Body Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {showHtml && preview.body.html ? (
          <div
            className="prose prose-sm max-w-none"
            dangerouslySetInnerHTML={{ __html: preview.body.html }}
          />
        ) : (
          <div className="whitespace-pre-wrap text-sm text-gray-700 font-mono">
            {preview.body.text || preview.snippet || 'No content available'}
          </div>
        )}
      </div>
    </div>
  );
}
