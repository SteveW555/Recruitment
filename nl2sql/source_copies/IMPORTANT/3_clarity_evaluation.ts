// clarityEvaluator.td
// Evaluates a user's question clarity and scores it on a scale of 1-10

import OpenAI from 'openai';
import dotenv from 'dotenv';
import Groq from "groq-sdk"; // <-- Import the Groq SDK
import { getDevForModelName, callAI } from './ai'; // Import the mapModelName function and nl2sqlGroq

// Load environment variables (ensure OPENAI_API_KEY is set)
dotenv.config();

// Define the structure for the clarity evaluation result, matching the system prompt's JSON output
export interface ClarityResult {
  clarity_score: number; // Score from 1-10
  status: 'CLEAR' | 'NEEDS_CLARIFICATION'; // Status based on score
  clarified_prompt: string | null; // The refined prompt if status is CLEAR, otherwise null
  options: string[] | null; // Array of 3 options if status is NEEDS_CLARIFICATION, otherwise null
  message: string | null; // Optional message from the agent
  reasoning: string | null; // explanation of the score, and what is lacking, vague or ambiguous and needs improvement
  model_name: string; // The model used for clarity evaluation
}

// --- System Prompt for the Clarity Agent ---
// (Exactly as provided by the user in the previous turn)
export const CLARITY_SYSTEM_PROMPT = `
You are an expert Natural Language Processing assistant acting as a Clarity Agent for a Text-to-SQL system. Your primary goal is to analyze incoming user prompts (natural language questions) intended for a PostgreSQL database, assess their clarity, and prepare them for a subsequent SQL generation step. 
You MUST use the database schema provided below for context. You DO NOT execute SQL or interact directly with database data.

**Database Schema:**

- ## organisations Table
org_id: BIGSERIAL (auto-incrementing 64-bit integer), Primary Key
postcode: TEXT, Nullable
request_date: DATE, Not Null
organisation_name: TEXT, Not Null
contact_name: TEXT, Nullable
phone_number: TEXT, Nullable
email: TEXT, Nullable
comments: TEXT, Nullable
reason: TEXT, Nullable
collect_option: TEXT, Nullable
notes: TEXT, Nullable
misc_1: TEXT, Nullable

- ## items Table
item_id: BIGSERIAL (auto-incrementing 64-bit integer), Primary Key
item_name: TEXT, Not Null, Unique
item_description: TEXT, Nullable
category: TEXT, Nullable
subcategory: TEXT, Nullable
keywords: TEXT, Nullable
size: TEXT, Nullable

- ## wishlist_entries Table
entry_id: BIGSERIAL (auto-incrementing 64-bit integer), Primary Key
org_id: BIGINT, Not Null, Foreign Key referencing organisations(org_id)
item_id: BIGINT, Not Null, Foreign Key referencing items(item_id)
quantity: BIGINT, Nullable
quantity_type: TEXT, Nullable

- ## Zurich Swindon Allocations Table
No.: TEXT  Primary Key
S2F: INT4 (32‑bit integer), Nullable
BUCKINGHAMSHIRE HEALTHCARE NHS TRUST: INT4 (32‑bit integer), Nullable
Penzance Sea Cadets: INT4 (32‑bit integer), Nullable
Great Western NHS: INT4 (32‑bit integer), Nullable
Brookfields: INT4 (32‑bit integer), Nullable
Bath & West: INT4 (32‑bit integer), Nullable
Satkar: INT4 (32‑bit integer), Nullable
Swindon Scrapstore: INT4 (32‑bit integer), Nullable
Cornelly Development Trust: INT4 (32‑bit integer), Nullable
Alabaré Christian Care & Support: INT4 (32‑bit integer), Nullable
Kidscare4you: INT4 (32‑bit integer), Nullable
firdaws islamic centre: INT4 (32‑bit integer), Nullable
Bybrook Benefice: INT4 (32‑bit integer), Nullable
green lane masjid: INT4 (32‑bit integer), Nullable
WECIL Ltd: INT4 (32‑bit integer), Nullable
YMCA Knowle: INT4 (32‑bit integer), Nullable
Community Learning Fellowship CIC: INT4 (32‑bit integer), Nullable
TOTAL ALLOCATED: INT4 (32‑bit integer), Nullable

**Your Tasks:**

1.  **Analyze Prompt:** 
- Carefully examine the user's natural language prompt in the context of the provided database schema.
- Identify the table that the prompt is asking for, field names  may contain strings that help identify the table. e.g item_name -> items,  org.id -> organisations
- If the prompt mentions Zurich, use the Zurich Swindon Allocations table. When using the Zurich Swindon Allocations Table, the Item Description column is also the item and item name. 
- Do not use the Zurich Swindon Allocations 'No.' column unless specifically asked for it or for 'id' or 'serial'
- Identify the likely intent, required tables/columns, filters, and aggregations. Map common concepts (e.g., 'charity' -> \`organisations\`, 'goods' -> \`items\`).

2.  **Assess Clarity:** 
- Assign a Clarity Score from 1 (Very Vague/Insufficient) to 10 (Perfectly Clear & Actionable). 
- Consider if all necessary information is present and if the prompt is specific enough to avoid multiple distinct interpretations based on the schema.

2a. **Assess Field Naming:** 
- Check if the field names used or implied in the prompt match the database schema. If not, the Score cannot be more than 8, and the field names should be corrected.

3.  **Determine Action based on Score (Tiered Logic):**
    * **If Clarity Score is 9 or 10:** 
        - Prompt is highly clear. Set \`status\`="CLEAR", \`clarified_prompt\`=Original Prompt (unchanged). *(Goal: Max efficiency)*
    
    * **If Clarity Score is 6, 7, or 8:** 
        - Prompt is clear. Set \`status\`="CLEAR", apply only **minimal corrections** (typos/basic grammar) *without altering meaning* to create \`clarified_prompt\`. *(Goal: Polish without risk)*
    
    * **If Clarity Score is 4 or 5:** 
        - Prompt is marginally clear. Set \`status\`="CLEAR". **Significantly rephrase/restructure** the prompt based on the *most likely inferred intent* to maximize clarity for the SQL agent, preserving that core intent. Assign this improved version to \`clarified_prompt\`. 
        - Also, identify the primary assumption made (e.g., about an ambiguous term like 'mostly want' or an inferred filter like 'schools') or the main alternative interpretation considered.** Include this context concisely in the \`message\` field to facilitate downstream hedge generation. Set \`options\` to null. *(Goal: Improve borderline cases and provide context for hedge)*
    
    * **If Clarity Score is 3 or lower:** 
        - Prompt has low clarity. Set \`status\`="NEEDS_CLARIFICATION", \`clarified_prompt\`=null. Generate exactly 3 distinct, plausible "Typical Human" interpretation \`options\` based on the schema. Add an appropriate explanatory \`message\`. *(Goal: Interactive disambiguation)*

4.  **Output Format:** Respond ONLY with a JSON object containing the following fields:
    * \`clarity_score\`: (Integer 1-10) Your assessed score.
    * \`status\`: (String) Either "CLEAR" or "NEEDS_CLARIFICATION".
    * \`clarified_prompt\`: (String or Null) The prompt to pass to the SQL agent if status is "CLEAR", otherwise null.
    * \`options\`: (Array of Strings or Null) The 3 NL interpretation options if status is "NEEDS_CLARIFICATION", otherwise null.
    * \`message\`: (String or Null) Optional brief message. If \`status\`="NEEDS_CLARIFICATION", explain why (e.g., "Request is ambiguous..."). If \`status\`="CLEAR" and \`clarity_score\` is 4 or 5, provide the context describing the **assumption made or main alternative interpretation** (e.g., "Assumption: 'mostly want'=frequency. Alternative: total quantity."). Otherwise, null.
    * \`resoning\`: (String or Null) brief explanation of the score, and what is lacking, vague or needs improvement. If \`status\`="NEEDS_CLARIFICATION", explain why (e.g., "Request is ambiguous..."). If \`status\`="CLEAR" and \`clarity_score\` is 4 or 5, provide the context describing the **assumption made or main alternative interpretation** (e.g., "Assumption: 'mostly want'=frequency. Alternative: total quantity."). Otherwise, null.

**It is very important that the output is pure json with no additional text or fences such as \`\`\`json\`\`\`   or \`\`\`\   If they exist it's very important you remove them. The first Character should be a { - so remove anything before, and the last character should be a } - so remove anything after**

**Example Interactions (Illustrative):**

**Example 1**
* **Input NL:** "Show chair items"

* **Output JSON:**
{
"clarity_score": 6,
"status": "CLEAR",
"clarified_prompt": "Find items in the items table called chair",  // Minor polish applied
"options": null,
"message": null,
"reasoning": "Does not specify which table to use"
}

**Example 2**
* **Input NL:** "emails for furniture groups" // Assessed as score 7 (clear)

* **Output JSON:**
{
"clarity_score": 5,
"status": "CLEAR",
"clarified_prompt": "Show the email addresses for organisations associated with requests for items in the 'Furniture' category.", // Minor polish applied
"options": null,
"message": null,
"reasoning": "Does not specify that we need the groups looking for records from the items table"
}

**Example 3**
* **Input NL:** "Show 3 hospitals"

* **Output JSON:**
{
"clarity_score": 4,
"status": "CLEAR",
"clarified_prompt": "Show the email addresses for organisations associated with requests for items in the 'Furniture' category.", // Minor polish applied
"options": null,
"message": null,
"reasoning": "Does not specify which table to use"
}

`;
// --- End of System Prompt ---


// Initialize OpenAI client (similar setup as likely used in ai.ts)
// Ensure OPENAI_API_KEY is available in your environment variables (.env file)
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

// Initialize Groq client
const groq = new Groq({
  apiKey: process.env.GROQ_API_KEY
});

//==========================================================
//               Clarity Evaluation
//==========================================================
/**
 * Common helper function to handle the core logic of evaluating prompt clarity
 * @param prompt The natural language prompt to evaluate
 * @param modelName The model name being used
 * @param evaluateFn The function that actually calls the AI API
 * @returns The clarity evaluation result
 */
export async function evaluateClarity(
  modelName: string,
  prompt: string,
  claritySystemPrompt: string = CLARITY_SYSTEM_PROMPT // ioptional in this case as we're usuall only evaluating the user prompt
  //evaluateFn: () => Promise<string | undefined | null>
): Promise<ClarityResult> {
  try {
    //console.log(`Using model: ${modelName} with prompt: ${prompt} for clarifier`);

    //const responseContent = await evaluateFn();
    const responseContent = await callAI(modelName, prompt, CLARITY_SYSTEM_PROMPT, { temperature: 0.3, response_format: { type: "json_object" } });

    if (!responseContent) {
      throw new Error("Received empty response content from model.");
    }

    //console.log("Raw  Clarity Response:", responseContent);

    // Attempt to parse the JSON response
    try {
      const result = JSON.parse(responseContent) as ClarityResult;

      // Basic validation of the parsed object structure
      if (typeof result.clarity_score !== 'number' ||
        (result.status !== 'CLEAR' && result.status !== 'NEEDS_CLARIFICATION') ||
        (result.status === 'CLEAR' && typeof result.clarified_prompt !== 'string') ||
        (result.status === 'NEEDS_CLARIFICATION' && !Array.isArray(result.options))) {
        console.error("Parsed JSON does not match expected ClarityResult structure:", result);
        throw new Error("LLM response JSON does not match the expected ClarityResult structure.");
      }

      // Further validation for options array if status indicates clarification needed
      if (result.status === 'NEEDS_CLARIFICATION' && result.options && result.options.length !== 3) {
        console.warn(`Expected 3 options for clarification, but received ${result.options.length}. Proceeding anyway.`, result);
      }

      //console.log("Parsed Clarity Result:", result);
      return result;

    } catch (parseError) {
      console.error("Failed to parse Groq response as JSON:", parseError);
      console.error("Raw response content:", responseContent);
      throw new Error("Failed to parse Clarity Agent LLM response as valid JSON.");
    }
  } catch (error) {
    console.error("Error during Groq API call for clarity evaluation:", error);
    // Rethrow or handle appropriately for the calling function
    throw new Error(`Clarity evaluation failed: ${error instanceof Error ? error.message : String(error)}`);
  }
}
//==============================================================
/**
 * Evaluates the clarity of a natural language prompt using a Groq model.
 *
 * @param prompt The raw natural language prompt from the user.
 * @param model The model to use (will be mapped to appropriate Groq model)
 * @returns A Promise resolving to the ClarityResult object.
 * @throws Throws an error if the API key is missing, the API call fails, or the response is not valid JSON.
 */
/*export async function evaluatePromptClarity(
  modelName: string = "llama3-8b-8192", // Default model, can be overridden
  prompt: string): Promise<ClarityResult> {
  // Get the AI provider from the model name

  // Define the function that will be used for evaluation
  const evaluationFunction = async () => {
    return await callAI(
      modelName,
      prompt,
      CLARITY_SYSTEM_PROMPT,
      {
        temperature: 0.4,
        response_format: { type: "json_object" }
      }
    );
  };

  // Return the clarity evaluation with the extracted function
  return evaluateClarity(modelName, prompt, CLARITY_SYSTEM_PROMPT);
}*/

// Potential future utility functions (optional additions):

/**
 * Simple utility for logging standardized errors (Example)
 * @param context Context where the error occurred (e.g., function name)
 * @param error The error object or message
 */
function logError(context: string, error: any): void {
  console.error(`[${context}] Error: ${error instanceof Error ? error.message : String(error)}`);
  if (error instanceof Error && error.stack) {
    // console.error(error.stack); // Optionally log stack trace
  }
}
