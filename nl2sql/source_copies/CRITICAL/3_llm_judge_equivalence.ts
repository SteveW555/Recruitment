import { Query } from 'pg';
import { callAI } from '../ai'; // Adjust the path to your callAI function implementation

// Define the System Prompt for the LLM
const systemPrompt = `You are an expert SQL analyst. Your task is to determine whether two given SQL queries are semantically equivalent, meaning they will produce the same result set when executed against the same database schema and data.

The user will provide two SQL queries. You should output "Equivalent" or "Not Equivalent".

Consider the following factors when assessing equivalence:

* **Table and Column Names:** Equivalence depends on the tables and columns being queried.
* **WHERE Clause:** The WHERE clause filters the data. Different conditions lead to different results.
* **SELECTed Columns:** The order and set of columns in the SELECT statement matter.
* **Joins:** How tables are joined affects the result. Different join conditions or join types (INNER, LEFT, etc.) can lead to different results.
* **Aliases:** Table and column aliases do not affect the meaning of the query, as long as they are used consistently.
* **Whitespace and Formatting:** Extra spaces, line breaks, and indentation do not change the query's meaning.
* **Case Sensitivity:** SQL is generally case-insensitive for keywords, table names, and column names (but string values in WHERE clauses might be case-sensitive, depending on the database).
* **Order of Operations:** Pay close attention to the order in which operations are performed (e.g., filtering before joining).
* **Set Operations:** Consider how set operations (UNION, INTERSECT, EXCEPT) affect the result.
* **Aggregation:** Ensure that aggregation functions (COUNT, SUM, AVG, etc.) are applied to the same groups of data in both queries.
* **Ordering:** The ORDER BY clause does NOT affect semantic equivalence.  Two queries that return the same rows in a different order are considered equivalent.
* **Category Equivalence Exception (\`=\` vs \`LIKE\`):** When comparing conditions specifically on the \`items.category\` column within the WHERE clause, treat an exact match condition (e.g., \`category = 'SomeCategory'\`) as equivalent to a broad \`LIKE\` pattern condition using the same category name (e.g., \`category LIKE '%SomeCategory%'\`), provided all other parts of the queries (other WHERE conditions, SELECT lists subject to the \`SELECT *\` exception, JOINs, etc.) are identical. 
- For all other columns or different types of \`LIKE\` patterns, standard comparison rules apply.

* **Equivalence Exception for SELECT *:**
A query using SELECT * is considered Equivalent to a query selecting specific columns if and only if all other parts of the queries (WHERE clauses, JOIN conditions, ORDER BY clauses, LIMIT clauses, GROUP BY clauses, etc.) are identical, AND one of the following conditions regarding the selected columns is met:
a)  The specific columns consist only of the primary identifying column (e.g., item_name for items, organisation_name for organisations).
b)  The specific columns consist only of the primary identifying column AND exactly one other single column.

Here are some examples to illustrate equivalence and non-equivalence:

**Equivalent Queries:**

1.  **Trivial Equivalence:**
    * Query 1: \`SELECT item_name FROM items WHERE category = 'desks';\`
    * Query 2: \`SELECT item_name FROM items WHERE category = 'desks';\`
    * Output: Equivalent

2.  **Alias Equivalence:**
    * Query 1: \`SELECT item_name FROM items WHERE category = 'desks';\`
    * Query 2: \`SELECT i.item_name FROM items AS i WHERE i.category = 'desks';\`
    * Output: Equivalent

3.  **Column Order Equivalence:**
    * Query 1: \`SELECT item_name, item_description FROM items WHERE category = 'desks';\`
    * Query 2: \`SELECT item_description, item_name FROM items WHERE category = 'desks';\`
    * Output: Equivalent

4.  **Whitespace and Formatting Equivalence:**
    * Query 1: \`SELECT item_name FROM items WHERE category = 'desks';\`
    * Query 2: \`SELECT\\n  item_name\\nFROM\\n  items\\nWHERE\\n  category = 'desks';\`
    * Output: Equivalent

5.  **Case Insensitivity Equivalence:**
    * Query 1: \`SELECT item_name FROM items WHERE category = 'desks';\`
    * Query 2: \`select ITEM_NAME from ITEMS where CATEGORY = 'desks';\`
    * Output: Equivalent

6.  **Equivalent WHERE Clause (Reordering):**
    * Query 1: \`SELECT item_name FROM items WHERE category = 'desks' AND item_id > 10;\`
    * Query 2: \`SELECT item_name FROM items WHERE item_id > 10 AND category = 'desks';\`
    * Output: Equivalent

7.  **Implicit vs. Explicit Joins:**
    * Query 1:  \`SELECT o.organisation_name, i.item_name FROM organisations o, items i, wishlist_entries w WHERE o.org_id = w.org_id AND i.item_id = w.item_id;\`
    * Query 2: \`SELECT o.organisation_name, i.item_name FROM organisations o JOIN wishlist_entries w ON o.org_id = w.org_id JOIN items i ON i.item_id = w.item_id;\`
    * Output: Equivalent
    
8.  **Simple Query Equivalence (SELECT * vs Name Column Exception):**
    * Query 1: \`SELECT * FROM items WHERE category = 'desks';\`
    * Query 2: \`SELECT item_name FROM items WHERE category = 'desks';\`
    * Output: Equivalent

9.  **Simple Query Equivalence (SELECT * vs Name Column Exception):**
    * Query 1: \`SELECT * FROM items;\`
    * Query 2: \`SELECT i.item_name FROM items AS i;\`
    * Output: Equivalent

10.  **Simple Query Equivalence (SELECT * vs Name Column Exception):**
    * Query 1: \`SELECT * FROM items WHERE category = 'desks';\`
    * Query 2: \`SELECT item_name, size FROM items WHERE category = 'desks';\`
    * Output: Equivalent
    
11. **Category Equivalence (\`=\` vs \`LIKE\` Exception):**
    * Query 1: \`SELECT item_name FROM items WHERE category = 'Lighting' AND size = 'compact';\`
    * Query 2: \`SELECT item_name FROM items WHERE category LIKE '%Lighting%' AND size = 'compact';\`
    * Output: Equivalent


**Non-Equivalent Queries:**

1.  **Different WHERE Clause:**
    * Query 1: \`SELECT item_name FROM items WHERE category = 'desks';\`
    * Query 2: \`SELECT item_name FROM items WHERE category = 'chairs';\`
    * Output: Not Equivalent

2.  **Different Columns:**
    * Query 1: \`SELECT item_name FROM items WHERE category = 'desks';\`
    * Query 2: \`SELECT item_description FROM items WHERE category = 'desks';\`
    * Output: Not Equivalent

3.  **Missing Join Condition:**
    * Query 1: \`SELECT o.organisation_name, i.item_name FROM organisations o JOIN wishlist_entries w ON o.org_id = w.org_id JOIN items i ON i.item_id = w.item_id;\`
    * Query 2: \`SELECT o.organisation_name, i.item_name FROM organisations o JOIN items i ON i.item_id = w.item_id;\`
    * Output: Not Equivalent

Now, analyze the two queries provided by the user and respond with ONLY "Equivalent" or "Not Equivalent". Do not provide any other explanation.`;

/**
 * Asks an LLM to determine if two SQL queries are semantically equivalent.
 *
 * @param queryA The first SQL query string.
 * @param queryB The second SQL query string.
 * @param modelName The name of the LLM model to use (defaults to gpt-4o-mini).
 * @param temperature The temperature setting for the LLM call (defaults to 0.2 for consistency).
 * @returns A Promise resolving to true if the queries are deemed equivalent, false otherwise.
 */
export async function queriesAreEquivalent(
    queryA: string,
    queryB: string,
    modelName: string = "gpt-4o-mini", // Or your preferred model
    temperature: number = 0.2 // Lower temperature for more deterministic classification
): Promise<boolean> {

    // Construct the user prompt containing the two queries
    const userPrompt = `Please assess if the following two SQL queries are semantically equivalent:

Query 1:
\`\`\`sql
${queryA}
\`\`\`

Query 2:
\`\`\`sql
${queryB}
\`\`\`

Respond with only "Equivalent" or "Not Equivalent".`;

    const options = {
        temperature: temperature,
        response_format: { type: 'text' } // Expecting simple text "Equivalent" or "Not Equivalent"
    };

    try {
        //console.log(`Checking equivalence for:\nQuery 1: ${queryA}\nQuery 2: ${queryB}`);
        const result = await callAI(modelName, userPrompt, systemPrompt, options);
        //console.log(`LLM Response: "${result}"`);

        // Process the result
        const trimmedResult = result.trim();

        // Case-insensitive comparison for robustness
        if (trimmedResult.toLowerCase() === 'equivalent') {
            return true;
        } else if (trimmedResult.toLowerCase() === 'not equivalent') {
            return false;
        } else {
            // Handle unexpected responses
            console.warn(`Unexpected response from LLM for query equivalence check: "${result}". Assuming Not Equivalent.`);
            return false;
        }

    } catch (error) {
        console.error("Error calling AI in queriesAreEquivalent:", error);
        // Re-throw the error or return false depending on desired behavior
        // Returning false might be safer than throwing if equivalence check failure isn't critical
        console.error("Assuming queries are Not Equivalent due to error.");
        return false;
        // throw error; // Alternatively, re-throw if the caller should handle it
    }
}

/**
 * Checks if two SQL snippets (one using '=' and one using 'LIKE') have the same inner value.
 * Only the inner quoted string is compared, ignoring SQL operator and wildcards.
 *
 * Example:
 * categoryLIKE_EQUALS_AreSame("category = 'Sport / Play / Sensory Equipment'", "category LIKE '%Sports / Play / Sensory Equipment%'") // true
 * categoryLIKE_EQUALS_AreSame("category = 'Sport'", "category LIKE '%Sports / Play / Sensory Equipment%'") // false
 *
 * Handles LIKE wildcards by stripping leading/trailing % from the LIKE pattern before comparison.
 */
export function categoryLIKE_EQUALS_AreSame(sql1: string, sql2: string): boolean {
    // Helper to extract the quoted value from a SQL snippet
    function extractInnerValue(sql: string): string | null {
        const match = sql.match(/['"](.*?)['"]/);
        return match ? match[1] : null;
    }

    // Helper to strip leading/trailing % from LIKE patterns
    function stripLikeWildcards(val: string): string {
        return val.replace(/^%+/, '').replace(/%+$/, '');
    }

    const val1 = extractInnerValue(sql1);
    const val2 = extractInnerValue(sql2);
    if (!val1 || !val2) return false;

    // Identify which is LIKE and which is =
    const isLike1 = /like/i.test(sql1);
    const isLike2 = /like/i.test(sql2);

    if (isLike1 && !isLike2) {
        return stripLikeWildcards(val1) === val2;
    } else if (!isLike1 && isLike2) {
        return val1 === stripLikeWildcards(val2);
    } else {
        // Both are = or both are LIKE, do a simple comparison (strip wildcards from both if LIKE)
        if (isLike1 && isLike2) {
            return stripLikeWildcards(val1) === stripLikeWildcards(val2);
        }
        return val1 === val2;
    }
}

//=====================================
/**
 * Asks the AI model for a Reason why two SQL queries are not equivalent, and provides exceptions where the reson is not important
 *
 * @param query1 - The first SQL query.
 * @param query2 - The second SQL query.
 * @returns A promise that resolves to the AI's explanation for non-equivalence.
 */
export async function getUnequivalentReason(model: string, query1: string, query2: string): Promise<{ reasonStruct: any; reasonsUnfiltered: any; exemptionString: string }> {
    const prompt = `You are an expert SQL analyst. Given the following two SQL queries, explain concisely why they are not semantically equivalent. 
    Focus on the differences in logic, data retrieved, or potential results. Do not state that they ARE equivalent unless you're sure they are identical.
    Give your response in a json format that uses category differences between the two queries:
    1. **Columns Selected:**  
        - Query 1 selects \`item_name\`, \`category\`, and \`size\`.
        - Query 2 selects only \`item_name\` and \`size\`.

    2. **Keyword Matching Logic:**  
        - Query 1 filters rows where the \`keywords\` column contains the substring \`'hdmi'\` (case-sensitive, depending on collation).
        - Query 2 filters rows where either \`item_name\` or \`item_description\` contains the substring \`'HDMI'\` (case-sensitive, and in different columns).

    3. **Case Sensitivity:**  
        - Query 1 uses lowercase \`'hdmi'\` in the \`LIKE\` clause.
        - Query 2 uses uppercase \`'HDMI'\` in the \`LIKE\` clauses. Depending on the database collation, this may yield different results.

    4. **Columns Used for Filtering:**  
        - Query 1 uses \`subcategory\` or \`keywords\` or \`size\` columns for filtering.
        - Query 2 uses none or different columns for filtering.

    5. **Order of Columns:**  
        - Query 1 orders by \`item_name\` ascending.
        - Query 2 orders by \`item_category\` descending.

    6. **Limiting Results:**  
        - Query 1 limits to 10 rows.
        - Query 2 does not limit the results.

    7. **NULL Usage:**  
        - Query 1 filters rows where the \`item_description\` column is null OR not null.
        OR
        - Query 2 filters rows where the \`item_description\` column is null OR not null.
        OR
        - Query 1: No explicit filter on item_description being NULL or NOT NULL.
        - Query 2: Filters rows where item_description IS NOT NULL.

        Any mismatch involving NULL or NOT NULL should fall under this category.

    8. **LIKE Usage:**  
        - Query 1  has "Exact match on category ( = 'Lighting')"
        - Query 2 has Partial match on category (LIKE '%Lighting%')
        OR
        - Query 1  has "Exact match on keywords ( = 'black')"
        - Query 2 has Partial match on keywords (LIKE '%black%')  

    9. **Identity Usage:**  
        - Query 1  looks for exact or partial match in category column
        - Query 2 looks for exact or partial match in item_name or item_description columns

    10. **Search Field Swap (Name/Description vs Category):** - One query searches using item_name/item_description.
       - The other query searches using category/item_name. 

    11. **Subset Search Logic:** - One query uses a broader set of OR'd LIKE conditions (e.g., searching name OR description).
        - The other query uses a narrower subset of those conditions (e.g., searching only name).


** ONLY show the categories of differences between the two queries when they are not equivalent. Do not provide any additional explanation or inroduction to the results.**
    If the queries are equivalent, you should not respond.
** ONLY respond in valid json format,  where the object has the categories of differences between the two queries from the 8 named reasons above, for example:
Do not add an extra "Reasons" key
|
Reasons: {
  "LIKE Usage": {
    "Query 1": "category is exact match (=) ",
    "Query 2": "category is partial match (LIKE)"
  },
  "Order of Columns": {
    "Query 1": "Orders by item_name ascending or descending.",
    "Query 2": "No explicit ordering."
  },
  "NULL Usage": {
    "Query 1": "item_description is null or not null.",
    "Query 2": "item_description is null or not null."
  }
}
Do not include fences like \`\`\`json or \`\`\`    Do not include any additional text**

    Query 1:
    \`\`\`sql
    ${query1}
    \`\`\`

    Query 2:
    \`\`\`sql
    ${query2}
    \`\`\`

    Reason: `;

    //-----------------------------------------
    try {
        //------------ Call AI ----------------
        const reason = await callAI(model, prompt, "You are a helpful assistant responds in json format", { temperature: 0.2, response_format: { type: "json_object" } });
        const unequivalentReason = reason.trim();
        let reasonStruct = JSON.parse(unequivalentReason);
        const reasonsUnfiltered = reasonStruct;
        let exemptionString = "";

        //============================================================
        // Allow  "=" and LIKE % % to be equivalent
        //============================================================
        if ("LIKE Usage" in reasonStruct) {
            const q1 = reasonStruct["LIKE Usage"]["Query 1"];
            const q2 = reasonStruct["LIKE Usage"]["Query 2"];
            const same = categoryLIKE_EQUALS_AreSame(q1, q2);
            if (same) {
                delete reasonStruct["LIKE Usage"];
                exemptionString += "LIKE Usage ";
            }
        }
        //============================================================
        // Allow  NULL or NOT NULL differences
        //============================================================
        if ("NULL Usage" in reasonStruct) {
            delete reasonStruct["NULL Usage"];
            exemptionString += "NULL Usage ";
            delete reasonStruct["NULL Usage"];
        }
            
        //============================================================
        // Allow  different columns selected to be equivalent
        //============================================================
        if ("Columns Selected" in reasonStruct) {
            delete reasonStruct["Columns Selected"];
            exemptionString += "Columns Selected ";
        }
        //============================================================
        // Allow  different order of columns to be equivalent
        //============================================================
        if ("Order of Columns" in reasonStruct) {
            delete reasonStruct["Order of Columns"];
            exemptionString += "Order of Columns ";
        }
        //============================================================
        // Allow  different Case Sensitivity to be equivalent
        //============================================================
        if ("Case Sensitivity" in reasonStruct) {
            delete reasonStruct["Case Sensitivity"];
            exemptionString += "Case Sensitivity ";
        }
        //============================================================
        // Allow  different Identity Usage to be equivalent
        //============================================================
        if ("Identity Usage" in reasonStruct) {
            delete reasonStruct["Identity Usage"];
            exemptionString += "Identity Usage ";
        }
        //============================================================
       // Allow specific swap between name/desc and category search
       // (as these are often interchangeable)
       //============================================================
       if ("Search Field Swap (Name/Description vs Category)" in reasonStruct) {
        delete reasonStruct["Search Field Swap (Name/Description vs Category)"];
        exemptionString += "Search Field Swap ";
       }
       //============================================================
       // Allow subset search logic (e.g., (A or B) vs (A))
       //============================================================
       if ("Subset Search Logic" in reasonStruct) {
        // Check if this is the *only* remaining difference if needed for safety:
        const remainingKeys = Object.keys(reasonStruct);
        if (remainingKeys.length === 1) { 
             console.log("Applying exemption for subset search logic.");
             delete reasonStruct["Subset Search Logic"];
             exemptionString += "Subset Search Logic ";
        }
    }

        return { reasonStruct, reasonsUnfiltered, exemptionString };
    }
    catch (error) {
        console.error("Error getting unequivalent reason from AI:", error);
        // Consider more specific error handling or re-throwing
        return { reasonStruct: null, reasonsUnfiltered: "An error occurred while looking for meaning.", exemptionString: "" };
    }
}