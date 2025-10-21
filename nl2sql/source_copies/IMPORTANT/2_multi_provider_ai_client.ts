import dotenv from 'dotenv';
import { createClient, SupabaseClient } from '@supabase/supabase-js';
import { getOrganisationsTableSystemPrompt } from './sysPrompts';
import { supabaseExecuteSQL, getSupabaseClient } from '../supabase/supabaseQuery';
import OpenAI from "openai";
import Groq from "groq-sdk"; // <-- Import the Groq SDK
import { Anthropic } from '@anthropic-ai/sdk';
import { GoogleGenerativeAI } from "@google/generative-ai";

dotenv.config(); // Load environment variables from .env file

// Initialize OpenAI client
const openaiClient = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY, // Ensure OPENAI_API_KEY is set in your .env file
});

// Initialize Groq client
const groqClient = new Groq({
  apiKey: process.env.GROQ_API_KEY
});

// Initialize Anthropic client
const anthropicClient = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY, // Ensure ANTHROPIC_API_KEY is set in your .env file
});

// Initialize Google client
const googleClient = new GoogleGenerativeAI(process.env.GOOGLE_AI_KEY || '');


// Initialize Supabase client
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_KEY; // Use anon key or service role key as needed

if (!supabaseUrl || !supabaseKey) {
  throw new Error(
    'Supabase URL or Key is missing. Ensure SUPABASE_URL and SUPABASE_KEY are set in your .env file.'
  );
}
// Using the centralized Supabase client instead of creating a new one
const supabase: SupabaseClient = getSupabaseClient();

// Get the system prompt from the prompts file
const sysPrompt = getOrganisationsTableSystemPrompt();

//==========================================================
//               Run Prompt
//==========================================================
// Define a return type for runPrompt
export interface PromptResult {
  sql: string;      // The generated SQL query
  data?: any;       // The data returned by the query, if successful
  error?: any;      // Any error encountered during RPC call or SQL execution
}

/**
 * Processes a natural language prompt, generates SQL, executes it via Supabase RPC,
 * and returns the SQL along with the result data or error.
 * @param promptText The natural language prompt.
 * @param model Optional model name to use for the OpenAI API call. Defaults to "gpt-4o-mini".
 * @returns A Promise resolving to a PromptResult object.
 */
export async function runPrompt(promptText: string, model: string = "gpt-4o-mini"): Promise<PromptResult> {
  console.log(`AI processing prompt: ${promptText} using model: ${model}`);

  let sqlQuery = '';
  let queryData: any = null;
  let queryError: any = null;

  try {

    //===============================================================
    //  Call the actual nl2sql function with the specified model
    //===============================================================
    sqlQuery = await callAI(model, promptText, sysPrompt);
    console.log(`Generated SQL: ${sqlQuery}`);
    // --- Added Supabase Query ---
    console.log('\n--- Attempting Supabase query in runPrompt using generated SQL ---');
    try {

      //=========================================================================
      // Call QUERY - (Use the centralized supabaseExecuteSQL function instead of direct RPC call)
      //=========================================================================
      const result = await supabaseExecuteSQL(sqlQuery);
      queryData = result.queryResultData;
      queryError = result.queryResultError;

    } catch (rpcError) {
      console.error('!!! Error during Supabase query attempt block in runPrompt:', rpcError);
      console.error(`Attempted SQL during catch: ${sqlQuery}`);
      queryError = rpcError; // Capture the error from the catch block
    } finally {
      console.log('--- Supabase query execution attempt finished in runPrompt ---\n');
    }
    // -----------------------------

  } catch (nl2sqlError) {
    console.error('!!! Error during nl2sql generation:', nl2sqlError);
    // If nl2sql fails, we won't have SQL or data, just the error
    queryError = nl2sqlError;
    sqlQuery = 'Error generating SQL'; // Placeholder SQL for the result object
  }

  // Return the comprehensive result object
  return {
    sql: sqlQuery,
    data: queryData,
    error: queryError
  };

  /* Original placeholder logic:
  await new Promise(resolve => setTimeout(resolve, 50)); // Simulate network delay
  return `SELECT * FROM your_table WHERE condition = 'based_on_prompt'; // Placeholder SQL for: ${promptText}`;
  */
}
//------------------------------------------- 
/**
 * Common helper function to handle the core logic of generating SQL from natural language
 * @param aiDev The AI provider name (for logging)
 * @param userPrompt The query to convert to SQL
 * @param modelName The model name being used
 * @param generateSqlFn The function that actually generates the SQL
 * @returns The generated SQL query
 */
async function generateAI(
  aiDev: string,
  modelName: string,
  userPrompt: string,
  generateSqlFn: () => Promise<string>)
  : Promise<string> {
  try {
    console.log(`Using ${aiDev} model: ${modelName}`);

    const sqlQuery = await generateSqlFn();

    if (!sqlQuery) {
      throw new Error(`Failed to generate SQL query. ${aiDev} response was empty.`);
    }

    console.log(`Generated SQL: ${sqlQuery}`);
    return sqlQuery.trim();
  } catch (error) {
    console.error(`Error calling ${aiDev} API:`, error);
    throw new Error(`Failed to convert natural language to SQL using ${aiDev}.`);
  }
}

/**
 * Gets the developer/provider name for a given model name
 * @param modelName The model name to look up
 * @returns The developer/provider name for the model (openai, groq, anthropic, or google)
 */
export function getDevForModelName(modelName: string): string {
  // Define all models by provider
  const modelsByProvider: Record<string, string[]> = {
    openai: ["gpt-4o", "o3-mini", "gpt-4o-mini", "gpt-4.1", "gpt-4.1-mini", "o4-mini"],
    groq: ["qwen-qwq-32b", "llama3-70b", "llama3-70b-8192", "llama-3.3-70b-versatile", "llama3-8b", "llama3-8b-8192", "llama-3.2-3b-preview", "llama-3.2-1b-preview", "meta-llama/llama-4-scout-17b-16e-instruct"],
    anthropic: ["claude-3-7-sonnet-latest", "claude-3-7-haiku-latest"],
    google: ["gemini-2.5-pro-preview-03-25", "gemini-2.0-flash"]
  };

  // Check each provider's models
  for (const [provider, models] of Object.entries(modelsByProvider)) {
    // Check if the model name contains or exactly matches any model in this provider's list
    if (models.some(model =>
      modelName === model ||
      modelName.includes(model)
    )) {
      return provider;
    }
  }

  // If no match found, return unknown
  console.warn(`Unknown model: ${modelName}, cannot determine provider`);
  return "unknown";
}
//-------------------------------------
/**
 * Maps model names to their provider-specific identifiers
 * @param provider The AI provider name
 * @param model The input model name
 * @returns The mapped model name for the specific provider
 */
export function mapModelName(provider: string, model: string): string {
  // Model mapping definitions
  const modelMaps: Record<string, Record<string, string>> = {
    openai: {
      "gpt-4o": "gpt-4o",
      "gpt-4.1": "gpt-4.1",
      "o3-mini": "o3-mini",
      "gpt-4o-mini": "gpt-4o-mini",
      "default": "gpt-4o-mini"
    },
    groq: {
      "llama3-70b": "llama3-70b-8192",
      "llama3-8b-8192": "llama3-8b-8192",
      "llama-3.2-3b-preview": "llama-3.2-3b-preview",
      "qwen-qwq-32b": "qwen-qwq-32b"
    },
    anthropic: {
      "claude-3-7-sonnet-latest": "claude-3-7-sonnet-latest",
      "claude-3-7-haiku-latest": "claude-3-7-haiku-latest",
      "default": "claude-3-7-haiku-latest"
    },
    google: {
      "gemini-2.5-pro-preview-03-25": "gemini-2.5-pro-preview-03-25",
      "gemini-2.0-flash": "gemini-2.0-flash",
      "default": "gemini-2.0-flash"
    }
  };

  // Get the provider's model map
  const providerMap = modelMaps[provider.toLowerCase()];
  if (!providerMap) {
    console.warn(`Unknown provider: ${provider}, using original model name`);
    return model;
  }

  // Return the mapped model name or the original if not found
  // For Groq, we'll pass through unknown models as-is
  if (provider.toLowerCase() === 'groq' && !providerMap[model]) {
    return model;
  }

  return providerMap[model] || providerMap["default"];
}

//=====================================  CallAI  =========================================
/*
    Returns just the SQL string
*/
export async function callAI(
  modelName: string,
  userPrompt: string,
  systemPrompt: string,
  options: {
    temperature?: number;
    response_format?: { type: string };
  } = {}
): Promise<string> {

  // Determine the AI provider based on the model name
  const aiDev = getDevForModelName(modelName);
  let response;

  if (aiDev === 'openai') {
    response = await callOpenAI(modelName, userPrompt, systemPrompt, options);
  }
  else if (aiDev === 'groq') {
    response = await callGroq(modelName, userPrompt, systemPrompt, options);
  }
  /*else if (aiDev === 'anthropic') {
    response = await callAnthropic(modelName, userPrompt, systemPrompt, options);
  }
  else if (aiDev === 'google') {
    response = await callGoogle(modelName, userPrompt, systemPrompt, options);
  }*/
  return response || '';
}

//-----------------------------------
/*
    Returns just the SQL string
*/
export async function callOpenAI(
  modelName: string = "gpt-4o-mini",
  userPrompt: string,
  systemPrompt: string,
  options: {
    temperature?: number;
    response_format?: { type: string };
  } = {}
): Promise<string> {

  const params: any = {
    messages: [
      { role: "system", content: systemPrompt },
      { role: "user", content: userPrompt },
    ],
    model: modelName,
    temperature: options.temperature ?? 0.2,
    response_format: options.response_format
  };

  const completion = await openaiClient.chat.completions.create(params);
  const response = completion.choices[0]?.message?.content;

  return response || '';

}

//-----------------------------------
export async function callGroq(
  modelName: string = "llama3-8b-8192",
  userPrompt: string,
  systemPrompt?: string,
  options: {
    temperature?: number;
    response_format?: { type: string };
  } = {}
): Promise<string> {

  // Use the provided system prompt or fall back to the default SQL prompt
  const temperature = options.temperature ?? 0.2;
  //const response_Format = options.response_format ?? { type: "text" };

  const params: any = {
    messages: [
      { role: "system", content: systemPrompt },
      { role: "user", content: userPrompt },
    ],
    model: modelName,
    temperature: temperature,
    response_format: options.response_format
  };

  // Add response_format if provided
  if (options.response_format) {
    params.response_format = options.response_format;
  }

  const completion = await groqClient.chat.completions.create(params);
  const response = completion.choices[0]?.message?.content;

  return response || '';
}
//-----------------------------------
/*export async function callAnthropic(
  modelName: string = "claude-3-7-sonnet-latest",
  naturalLanguageQuery: string,
  systemPrompt?: string,
  options: {
    temperature?: number;
    maxTokens?: number;
  } = {}
): Promise<string> {
  const anthropicModel = mapModelName("anthropic", modelName);

  // Use the provided system prompt or fall back to the default SQL prompt
  const maxTokens = options.maxTokens ?? 1024;
  const temperature = options.temperature ?? 0.2;

  return generateAI("Anthropic", naturalLanguageQuery, anthropicModel, async () => {
    const message = await anthropicClient.messages.create({
      model: anthropicModel,
      system: systemPrompt,
      messages: [
        { role: "user", content: naturalLanguageQuery }
      ],
      max_tokens: maxTokens,
      temperature: temperature
    });

    // Access the content safely using optional chaining and type checking
    let responseText = '';
    if (message.content && message.content.length > 0) {
      const firstContent = message.content[0];
      if (typeof firstContent === 'object' && firstContent !== null && 'type' in firstContent) {
        if (firstContent.type === 'text' && 'text' in firstContent) {
          responseText = firstContent.text;
        }
      }
    }

    //console.log(`Anthropic response: ${responseText}`);
    return responseText;
  });
}*/
//-----------------------------------
/*export async function callGoogle(
  modelName: string = "gemini-2.5-pro-preview-03-25",
  naturalLanguageQuery: string,
  systemPrompt?: string,
  options: {
    systemPrompt?: string;
    temperature?: number;
  } = {}
): Promise<string> {
  const googleModel = mapModelName("google", modelName);

  // Use the provided system prompt or fall back to the default SQL prompt
  const temperature = options.temperature ?? 0.2;

  return generateAI("Google", naturalLanguageQuery, googleModel, async () => {
    const genAI = googleClient.getGenerativeModel({
      model: googleModel,
      generationConfig: {
        temperature: temperature
      }
    });

    const result = await genAI.generateContent([
      naturalLanguageQuery
    ]);

    // Access the content safely using optional chaining and type checking
    let sqlQuery = '';
    if (result.response && result.response.candidates &&
      result.response.candidates.length > 0 &&
      result.response.candidates[0].content &&
      result.response.candidates[0].content.parts &&
      result.response.candidates[0].content.parts.length > 0) {
      const part = result.response.candidates[0].content.parts[0];
      if (typeof part === 'object' && part !== null && 'text' in part) {
        sqlQuery = part.text ?? '';
      }
    }

    //console.log(`Google response: ${sqlQuery}`);
    return sqlQuery;
  });
}*/
