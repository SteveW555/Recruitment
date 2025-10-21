/**
 * DEPRECATED: This file is deprecated and will be removed in a future release.
 * 
 * Please import from '../sql/schemaReporter.ts' instead.
 * See housekeeping/SCHEMA_MANAGEMENT.md for more information.
 */

// This file now contains the actual implementation instead of being a re-export

// Schema Reporter for NL2SQL Application
// Uses @supabase/supabase-js client with Service Role Key

import { createClient, SupabaseClient } from '@supabase/supabase-js';
import { TableSchema, TableColumn } from '../types';

// Load environment variables (assuming dotenv is configured in the calling script, e.g., testSchemaReporter.ts)
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseUrl || !supabaseServiceKey) {
    throw new Error(
        'Supabase URL or Service Role Key is missing. Ensure SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are set in your environment.'
    );
}

// Initialize Supabase client with Service Role Key for elevated privileges
const supabase: SupabaseClient = createClient(supabaseUrl, supabaseServiceKey);

/**
 * Get a list of all tables in the public schema using Supabase client
 * @returns Promise<string[]> Array of table names
 */
export async function getAllTables(): Promise<string[]> {
    try {
        // Use supabase.sql() to execute a raw SQL query
        const query = `
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
              AND table_type = 'BASE TABLE' 
              AND table_name <> 'supabase_migrations' -- Use standard Supabase migrations table name
              AND table_name NOT LIKE 'pg_%' 
              AND table_name NOT LIKE 'sql_%'
              AND table_name NOT LIKE '_sqlx_%'; -- Exclude sqlx internal tables
        `;
        // Specify the expected return type for better type safety
        // Cast to any to bypass potential type definition issue for .sql()
        const { data, error } = await (supabase as any).sql(query);

        if (error) {
            console.error('Error fetching tables using supabase.sql():', error);
            throw error; 
        }

        if (!data) {
            console.warn('No data returned when fetching tables using supabase.sql().');
            return [];
        }

        // Extract table names
        return data.map((row: any) => row.table_name);

    } catch (error) {
        console.error('Error in getAllTables using supabase.sql():', error);
        return []; // Return empty array on failure
    }
}

/**
 * Get detailed schema information for a specific table using Supabase client
 * @param tableName Name of the table to get schema for
 * @returns Promise<TableSchema | null> Table schema details or null if error
 */
export async function getTableSchema(tableName: string): Promise<TableSchema | null> {
    try {
        // Use supabase.sql() for column information
        const columnsQuery = `
            SELECT 
                column_name, 
                data_type, 
                column_default, 
                is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = $1
            ORDER BY ordinal_position;
        `;
        // Cast to any to bypass potential type definition issue for .sql()
        const { data: columnsData, error: columnsError } = await (supabase as any).sql(columnsQuery, [tableName]);

        if (columnsError) {
             console.error(`Error fetching columns for table ${tableName} using supabase.sql():`, columnsError);
             throw columnsError;
        }
        
        if (!columnsData || columnsData.length === 0) {
            console.warn(`No columns found for table ${tableName} using supabase.sql().`);
            return null;
        }

        const columns: TableColumn[] = columnsData.map((col: any) => ({
            name: col.column_name,
            type: col.data_type,
            default: col.column_default,
            nullable: col.is_nullable === 'YES'
        }));

        // Fetch Primary Keys using supabase.sql()
        const primaryKeys = await getPrimaryKeys(tableName);
        // Fetch Foreign Keys using supabase.sql()
        const foreignKeys = await getForeignKeys(tableName);

        // Mark primary key columns
        for (const column of columns) {
            if (primaryKeys.includes(column.name)) {
                (column as any).isPrimary = true;
            }
        }

        return {
            name: tableName,
            schema: 'public',
            description: '', // We could fetch this from pg_description if needed
            columns
        };
    } catch (error) {
        console.error(`Error in getTableSchema for ${tableName}:`, error);
        return null;
    }
}

/**
 * Get primary keys using Supabase client's sql() method
 * @param tableName Name of the table
 * @returns Promise<string[]> Array of primary key column names
 */
export async function getPrimaryKeys(tableName: string): Promise<string[]> {
    try {
        const query = `
          SELECT kcu.column_name
          FROM information_schema.table_constraints tc
          JOIN information_schema.key_column_usage kcu 
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
          WHERE tc.constraint_type = 'PRIMARY KEY' 
            AND tc.table_schema = 'public'
            AND tc.table_name = $1
          ORDER BY kcu.ordinal_position;
        `;
        // Cast to any to bypass potential type definition issue for .sql()
        const { data, error } = await (supabase as any).sql(query, [tableName]);

        if (error) {
            console.error(`Error fetching primary keys for ${tableName}:`, error);
            return [];
        }
        return data ? data.map((row: any) => row.column_name) : [];
    } catch (error) {
        console.error(`Exception in getPrimaryKeys for ${tableName}:`, error);
        return [];
    }
}

/**
 * Get foreign keys using Supabase client's sql() method
 * @param tableName Name of the table
 * @returns Promise<Record<string, { table: string, column: string }>> Map of column names to their foreign key constraints
 */
export async function getForeignKeys(tableName: string): Promise<Record<string, { table: string, column: string }>> {
    try {
        const query = `
          SELECT
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name 
          FROM 
            information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
          WHERE tc.constraint_type = 'FOREIGN KEY' 
            AND tc.table_schema = 'public'
            AND tc.table_name = $1;
        `;
        // Cast to any to bypass potential type definition issue for .sql()
        const { data, error } = await (supabase as any).sql(query, [tableName]);

        if (error) {
            console.error(`Error fetching foreign keys for ${tableName}:`, error);
            return {};
        }

        const foreignKeys: Record<string, { table: string, column: string }> = {};
        if (data) {
            data.forEach((row: any) => {
                foreignKeys[row.column_name] = {
                    table: row.foreign_table_name,
                    column: row.foreign_column_name
                };
            });
        }
        return foreignKeys;
    } catch (error) {
        console.error(`Exception in getForeignKeys for ${tableName}:`, error);
        return {};
    }
}

/**
 * Get sample data for a table using Supabase client
 * @param tableName Name of the table
 * @returns Promise<any[]> Array of sample data rows
 */
export async function getTableSampleData(tableName: string): Promise<any[]> {
  try {
    // Use the standard .from().select() which works for user tables
    const { data, error } = await supabase
      .from(tableName)
      .select('*')
      .limit(5);
    
    if (error) throw error;
    
    return data || [];

  } catch (error) {
    console.error(`Error fetching sample data for table ${tableName}:`, error);
    return [];
  }
}

/**
 * Close database connections (No-op for Supabase client)
 */
export async function closeConnections(): Promise<void> {
  // The Supabase client doesn't require explicit connection closing like a Pool
  console.log('Supabase client does not require explicit connection closing.');
}
