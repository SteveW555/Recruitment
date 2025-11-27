/**
 * AI-powered Employee Hours extraction using LLM
 *
 * PURPOSE:
 * This module acts as a bridge between raw spreadsheet data and an AI model.
 * Its goal is to intelligently identify and extract employee names and their total worked hours from unstructured or messy spreadsheet 
 * content, which traditional rule-based parsers might fail to handle correctly.
 *
 * DATA FLOW:
 * 1. Input: Receives `ParsedData` (raw rows/headers from an uploaded .xlsx/.csv file). e.g. Invoicing source.csv
 * 
 * 2. Conversion: Transforms that structured data back into a raw CSV string to give
 *    the LLM a clear, text-based representation of the spreadsheet.
 * 3. Prompting: Combines the CSV data with a system prompt (loaded from
 *    `../prompts/employee_hours_summary.txt`) that instructs the AI on how to
 *    interpret the data and format the output.
 * 4. AI Processing: Sends the request to the selected LLM (e.g., GPT-4o-mini) via
 *    the `complete` function from the `llm` module.
 * 5. Parsing: Validates and parses the AI's JSON response into a strongly-typed
 *    array of records.
 * 
 * 6. Output: 
 *    Returns `ExtractedData`, which is used by the main application to
 *    display previews and generate invoices.
 */

import type { ParsedData, ExtractedHoursData, ExtractedBonusData } from '../types';
import { complete } from './llm';
// Import prompt file as raw string using Vite's ?raw import
// Source: src/prompts/employee_hours_summary.txt
import systemPromptTemplate from '../prompts/employee_hours_summary.txt?raw';
import bonusPromptTemplate from '../prompts/employee_bonuses_summary.txt?raw';

/**
 * Helper: Convert ParsedData object to a simple CSV string.
 * This string is what gets sent to the LLM as the "User Prompt".
 */
function parsedDataToCSV(data: ParsedData): string {
  const rows = [
    data.headers.join(','),
    ...data.rows.map(row =>
      data.headers.map(header => {
        const value = row[header];
        // Handle values that might contain commas by wrapping in quotes
        if (typeof value === 'string' && value.includes(',')) {
          return `"${value}"`;
        }
        return value ?? '';
      }).join(',')
    )
  ];
  return rows.join('\n');
}

/**
 * Main Function: Extract Employee Hours from spreadsheep/csv  using AI/LLM
 *
 * @param parsedData - The raw spreadsheet data loaded from the file input
 * @param model - The ID of the LLM model to use (default: 'gpt-4o-mini')
 * @returns Promise<ExtractedHoursData> - Structured data ready for the invoice generator
 */
export async function aiExtractEmployeeHours(
  parsedData: ParsedData,
  //model: string = 'gpt-4o-mini',
  model: string = 'gpt-5-nano-2025-08-07',
  previewCount: number = 20
): Promise<ExtractedHoursData> {
  // 1. Prepare Data: Convert parsed spreadsheet data to CSV format
  const csvData = parsedDataToCSV(parsedData);
  const systemPrompt = systemPromptTemplate;
  const userPrompt = csvData;

  // 4. Call LLM: Send to the AI provider
  const response = await complete({
    model,
    systemPrompt,
    userPrompt,
    temperature: 0.1, // Low temperature ensures consistent, structured output
    maxTokens: 4096
  });

  // 5. Parse Response: Convert AI's text output into a JSON object
  let extractedRecords: Array<{ name: string; hours: number }>;
  try {
    // Clean response - remove markdown code blocks (```json ... ```) if present
    let cleanedContent = response.content.trim();
    if (cleanedContent.startsWith('```json')) {
      cleanedContent = cleanedContent.replace(/^```json\s*/, '').replace(/\s*```$/, '');
    } else if (cleanedContent.startsWith('```')) {
      cleanedContent = cleanedContent.replace(/^```\s*/, '').replace(/\s*```$/, '');
    }

    extractedRecords = JSON.parse(cleanedContent);

    if (!Array.isArray(extractedRecords)) {
      throw new Error('LLM response is not an array');
    }

    // Validate structure of each record
    for (const record of extractedRecords) {
      if (!record.name || typeof record.hours !== 'number') {
        throw new Error('Invalid record format in LLM response');
      }
    }
  } catch (error) {
    throw new Error(`Failed to parse LLM response: ${error instanceof Error ? error.message : 'Invalid JSON'}\n\nResponse: ${response.content}`);
  }

  // 6. Format Output: Map to the application's internal data structure
  const data = extractedRecords.map(record => ({
    employee: record.name,
    hours: record.hours
  }));

  if (data.length === 0) {
    throw new Error('No employee hours data extracted by AI');
  }

  // Return the final ExtractedHoursData object
  return {
    employeeColumn: 'AI Extracted Name',
    hoursColumn: 'AI Extracted Hours',
    startRow: 0,
    endRow: data.length - 1,
    data,
    preview: data.slice(0, previewCount) // Preview first 5 records
  };
}

/**
 * Extract Employee Bonuses from spreadsheet/csv using AI/LLM
 *
 * @param parsedData - The raw spreadsheet data loaded from the file input
 * @param model - The ID of the LLM model to use
 * @returns Promise<ExtractedBonusData> - Structured bonus data
 */
export async function aiExtractEmployeeBonuses(
  parsedData: ParsedData,
  model: string = 'openai/gpt-oss-120b',
  previewCount: number = 20
): Promise<ExtractedBonusData> {
  // 1. Prepare Data: Convert parsed spreadsheet data to CSV format
  const csvData = parsedDataToCSV(parsedData);
  const systemPrompt = bonusPromptTemplate;
  const userPrompt = csvData;

  // 2. Call LLM: Send to the AI provider
  const response = await complete({
    model,
    systemPrompt,
    userPrompt,
    temperature: 0.1,
    maxTokens: 4096
  });

  // 3. Parse Response: Convert AI's text output into a JSON object
  let result: { employeeColumn?: string; bonusColumn?: string; data: Array<{ employee: string; bonus: number }> };
  try {
    // Clean response - remove markdown code blocks (```json ... ```) if present
    let cleanedContent = response.content.trim();
    if (cleanedContent.startsWith('```json')) {
      cleanedContent = cleanedContent.replace(/^```json\s*/, '').replace(/\s*```$/, '');
    } else if (cleanedContent.startsWith('```')) {
      cleanedContent = cleanedContent.replace(/^```\s*/, '').replace(/\s*```$/, '');
    }

    result = JSON.parse(cleanedContent);

    if (!result.data || !Array.isArray(result.data)) {
      throw new Error('LLM response is missing data array');
    }

    // Validate structure of each record
    for (const record of result.data) {
      if (!record.employee || typeof record.bonus !== 'number') {
        throw new Error('Invalid record format in LLM response');
      }
    }
  } catch (error) {
    throw new Error(`Failed to parse LLM response: ${error instanceof Error ? error.message : 'Invalid JSON'}\n\nResponse: ${response.content}`);
  }

  // 4. Format Output
  const data = result.data;

  if (data.length === 0) {
    throw new Error('No employee bonus data extracted by AI');
  }

  return {
    employeeColumn: result.employeeColumn || 'AI Extracted Name',
    bonusColumn: result.bonusColumn || 'AI Extracted Bonus',
    startRow: 0,
    endRow: data.length - 1,
    data,
    preview: data.slice(0, previewCount)
  };
}
