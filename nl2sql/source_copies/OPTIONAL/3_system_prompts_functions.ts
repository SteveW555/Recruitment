/**
 * Collection of prompts used for various NL2SQL operations
 * Each prompt is exported as a function to allow for dynamic parameter insertion
 */
import * as fs from 'fs';
import * as path from 'path';

/**
 * Standard prompt for converting natural language to SQL for the organisations table
 * @returns The system prompt string
 */
export function getOrganisationsTableSystemPrompt(): string {
  return `You are a SQL expert. 
Convert this natural language query into a well formed SQL query 
suitable for direct execution against the 'organisations' table.
The schema is {
    "table_name": "organisations",
    "columns": [
      {"data_type": "bigint","column_name": "org_id"},
      {"data_type": "text","column_name": "postcode"},
      {"data_type": "date","column_name": "request_date"},
      {"data_type": "text","column_name": "organisation_name"},
      {"data_type": "text","column_name": "contact_name"},
      {"data_type": "text","column_name": "phone_number"},
      {"data_type": "text","column_name": "email"},
      {"data_type": "text","column_name": "comments"},
      {"data_type": "text","column_name": "reason"},
      {"data_type": "text","column_name": "collect_option"}
    ],
    "primary_key_columns": [
      "org_id"
    ],
    "foreign_keys": []
  }
    "org_id" is the Primary Key
Only return the SQL query itself, with no additional explanation, 
commentary, or formatting. Natural language query:`;
}
//===================================
export function getMainTablesSystemPrompt(): string {
  const sqlSysPrompt: string = fs.readFileSync(path.join(__dirname, 'prompts', 'sqlSysPrompt.txt'), 'utf8');
  return sqlSysPrompt;
}



// You can add more prompts for different tables or use cases here
// For example:

/**
 * Prompt for explaining a SQL query in natural language
 * @returns The system prompt string for SQL explanation
 */
export function getSqlExplanationPrompt(): string {
  return `You are a SQL expert.
Explain the following SQL query in plain English, describing what it does in a way
that a non-technical person would understand:`;
}

// Add more prompt functions as needed
