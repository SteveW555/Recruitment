import dotenv from 'dotenv';
import { createClient, SupabaseClient } from '@supabase/supabase-js';

// Load environment variables
dotenv.config();

// Initialize Supabase client
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_KEY;

if (!supabaseUrl || !supabaseKey) {
    throw new Error(
        'Supabase URL or Key is missing. Ensure SUPABASE_URL and SUPABASE_KEY are set in your .env file.'
    );
}

// Create a singleton Supabase client instance
export const supabase: SupabaseClient = createClient(supabaseUrl, supabaseKey);

/**
 * Interface for the result of SQL execution
 * @param data The data returned by the query, if successful
 * @param error Any error encountered during execution
 */
export interface SqlExecutionResult {
    queryResultData: any;       // The data returned by the query, if successful
    queryResultError: any;      // Any error encountered during execution
}

/**
 * Executes a SQL query using Supabase RPC
 * @param sqlQuery The SQL query to execute
 * @returns A Promise resolving to a SqlExecutionResult object containing data and error properties
 */
export async function supabaseExecuteSQL(sqlQuery: string): Promise<SqlExecutionResult> {
    //console.log(`Executing SQL via supabaseExecuteSQL: ${sqlQuery}`);

    let queryData: any = null;
    let queryError: any = null;

    try {
        // Trim whitespace and remove trailing semicolon before executing
        const cleanedSqlQuery = sqlQuery.trim().replace(/;$/, '');
        //console.log(`Cleaned SQL query: ${cleanedSqlQuery}`);

        // Call the database function to execute the dynamic SQL
        const { data, error } = await supabase.rpc('execute_sql', {
            query_text: cleanedSqlQuery
        });

        queryData = data;
        queryError = error;

        // Log results
        if (error) {
            console.error('!!! SQL execution FAILED:', error);
            console.error(`Failed SQL: ${cleanedSqlQuery}`);
        } else if (data && data.length > 0) {
            console.log('✅ SQL execution SUCCEEDED.');
            //console.log('Fetched data:', JSON.stringify(data, null, 2));
        } else {
            console.warn('❓ SQL execution returned no data or empty data.');
            console.log(`Executed SQL:\n ${cleanedSqlQuery}\n`);
        }

    } catch (error) {
        console.error('!!! Error during SQL execution:', error);
        queryError = error;
    } finally {
        //console.log('--- SQL execution attempt finished ---\n');
    }

    return {
        queryResultData: (Array.isArray(queryData) && queryData.length === 0)
            ? [{ message: "No matching results were found" }]
            : queryData,
        queryResultError: queryError
    };
}

/**
 * Helper function to clean a SQL query (remove trailing semicolons, trim whitespace)
 * @param sqlQuery The SQL query to clean
 * @returns The cleaned SQL query
 */
export function cleanSqlQuery(sqlQuery: string): string {
    return sqlQuery.trim().replace(/;$/, '');
}

/**
 * Executes a raw SQL query directly using Supabase
 * This is useful for queries that don't need to go through the RPC function
 * @param sqlQuery The SQL query to execute
 * @returns A Promise resolving to the query result
 */
export async function supabaseExecuteRawSQL(sqlQuery: string): Promise<any> {
    const cleanedQuery = cleanSqlQuery(sqlQuery);
    // Using rpc instead of direct SQL method which caused a lint error
    return await supabase.rpc('execute_sql', {
        query_text: cleanedQuery
    });
}

/**
 * Gets the Supabase client instance
 * This allows other modules to access the same client instance when needed
 * @returns The Supabase client instance
 */
export function getSupabaseClient(): SupabaseClient {
    return supabase;
}