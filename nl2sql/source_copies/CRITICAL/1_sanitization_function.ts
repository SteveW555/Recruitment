/**
 * CRITICAL FILE #1: Input Sanitization
 *
 * Source: src/backend/sql/promptEval/testing.ts:61-84
 * Priority: CRITICAL - Must copy exactly
 * Modifications: None - copy as-is
 *
 * Purpose: Prevents SQL injection and prompt manipulation attacks
 *
 * Usage:
 *   const [sanitized, wasModified] = sanitizeNlInputForSqlLLM(userInput);
 *   if (wasModified) {
 *     console.warn('⚠️ Potential attack attempt');
 *   }
 */

/**
 * Sanitizes natural language input before sending to LLM for SQL generation.
 * Focuses on removing common SQL syntax characters to mitigate prompt injection.
 * WARNING: This is NOT a replacement for parameterized queries during execution.
 *
 * @param userInput The raw natural language string from the user.
 * @returns A tuple: [sanitizedString, wasModified]
 */
function sanitizeNlInputForSqlLLM(userInput: string): [string, boolean] {
  if (!userInput) {
    return ['', false];
  }
  let sanitizedStr = userInput;

  // Remove single-line comments (-- ...)
  sanitizedStr = sanitizedStr.replace(/--.*$/gm, '');
  // Remove multi-line comments (/* ... */)
  sanitizedStr = sanitizedStr.replace(/\/\*.*?\*\//gs, '');
  // Remove single quotes (') - often used in injection
  sanitizedStr = sanitizedStr.replace(/'/g, '');
  // Remove semicolons (;) - statement terminators
  sanitizedStr = sanitizedStr.replace(/;/g, '');
  // Trim whitespace
  sanitizedStr = sanitizedStr.trim();

  let isSanitized = false;
  if(sanitizedStr != userInput)
  {
    isSanitized = true;
  }

  return [sanitizedStr, isSanitized];
}

// Example usage:
// const potentiallyMaliciousInput = "Show ' ; DROP TABLE testytable; --";
// const [sanitized, wasModified] = sanitizeNlInputForSqlLLM(potentiallyMaliciousInput);
// console.log(`Sanitized: "${sanitized}"`); // Output: "Sanitized: "Show  DROP TABLE projects""
// console.log(`Was modified: ${wasModified}`); // Output: true

export { sanitizeNlInputForSqlLLM };
