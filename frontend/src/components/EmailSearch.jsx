import React, { useState } from 'react';
import { Search, Calendar, Paperclip, X } from 'lucide-react';

/**
 * Email Search Component
 * Basic email search with date range and filters
 */
export default function EmailSearch({ onSearch, onClear, isLoading }) {
  const [filters, setFilters] = useState({
    dateFrom: '',
    dateTo: '',
    hasAttachment: false,
    fromAddress: '',
    subject: '',
    maxResults: 50,
  });

  const handleChange = (field, value) => {
    setFilters((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // Build search params (filter out empty values)
    const searchParams = Object.entries(filters).reduce((acc, [key, value]) => {
      if (value !== '' && value !== false && value !== null) {
        acc[key] = value;
      }
      return acc;
    }, {});

    onSearch(searchParams);
  };

  const handleClear = () => {
    setFilters({
      dateFrom: '',
      dateTo: '',
      hasAttachment: false,
      fromAddress: '',
      subject: '',
      maxResults: 50,
    });
    if (onClear) onClear();
  };

  const hasActiveFilters = Object.values(filters).some(
    (v) => v !== '' && v !== false && v !== 50
  );

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
        <Search className="mr-2" size={24} />
        Email Search
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Date Range */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <Calendar size={16} className="inline mr-1" />
              Date From
            </label>
            <input
              type="date"
              value={filters.dateFrom}
              onChange={(e) => handleChange('dateFrom', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <Calendar size={16} className="inline mr-1" />
              Date To
            </label>
            <input
              type="date"
              value={filters.dateTo}
              onChange={(e) => handleChange('dateTo', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        {/* From Address */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            From Address
          </label>
          <input
            type="email"
            value={filters.fromAddress}
            onChange={(e) => handleChange('fromAddress', e.target.value)}
            placeholder="sender@example.com"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Subject */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Subject Contains
          </label>
          <input
            type="text"
            value={filters.subject}
            onChange={(e) => handleChange('subject', e.target.value)}
            placeholder="Enter subject keywords..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Has Attachment & Max Results */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-center">
            <input
              type="checkbox"
              id="hasAttachment"
              checked={filters.hasAttachment}
              onChange={(e) => handleChange('hasAttachment', e.target.checked)}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
            />
            <label htmlFor="hasAttachment" className="ml-2 text-sm font-medium text-gray-700 flex items-center">
              <Paperclip size={16} className="mr-1" />
              Has Attachments
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Max Results
            </label>
            <select
              value={filters.maxResults}
              onChange={(e) => handleChange('maxResults', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value={10}>10</option>
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
              <option value={200}>200</option>
            </select>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3 pt-4">
          <button
            type="submit"
            disabled={isLoading}
            className="flex-1 bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:bg-blue-300 disabled:cursor-not-allowed transition-colors font-medium flex items-center justify-center"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Searching...
              </>
            ) : (
              <>
                <Search size={18} className="mr-2" />
                Search Emails
              </>
            )}
          </button>

          {hasActiveFilters && (
            <button
              type="button"
              onClick={handleClear}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors font-medium flex items-center"
            >
              <X size={18} className="mr-2" />
              Clear
            </button>
          )}
        </div>
      </form>

      {/* Active Filters Summary */}
      {hasActiveFilters && (
        <div className="mt-4 p-3 bg-blue-50 rounded-md">
          <p className="text-sm text-blue-800 font-medium mb-2">Active Filters:</p>
          <div className="flex flex-wrap gap-2">
            {filters.dateFrom && (
              <span className="px-2 py-1 bg-white text-blue-700 text-xs rounded-full border border-blue-200">
                From: {filters.dateFrom}
              </span>
            )}
            {filters.dateTo && (
              <span className="px-2 py-1 bg-white text-blue-700 text-xs rounded-full border border-blue-200">
                To: {filters.dateTo}
              </span>
            )}
            {filters.fromAddress && (
              <span className="px-2 py-1 bg-white text-blue-700 text-xs rounded-full border border-blue-200">
                From: {filters.fromAddress}
              </span>
            )}
            {filters.subject && (
              <span className="px-2 py-1 bg-white text-blue-700 text-xs rounded-full border border-blue-200">
                Subject: {filters.subject}
              </span>
            )}
            {filters.hasAttachment && (
              <span className="px-2 py-1 bg-white text-blue-700 text-xs rounded-full border border-blue-200">
                With Attachments
              </span>
            )}
            {filters.maxResults !== 50 && (
              <span className="px-2 py-1 bg-white text-blue-700 text-xs rounded-full border border-blue-200">
                Limit: {filters.maxResults}
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
