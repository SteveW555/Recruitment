import { v4 as uuidv4 } from 'uuid';
import * as fs from 'fs'; // Node.js file system module
import * as Papa from 'papaparse'; // CSV parsing library
import { MedTemplate } from '../medTemplateLists'; // Assuming MedTemplate is defined here

// --- Define Interfaces ---

interface ItemRecord {
    item_id: string;
    item_name: string;
    item_description: string;
    category: string;
    subcategory: string;
    keywords: string;
    size: string;
    [key: string]: string;
}

interface OrganisationRecord {
    org_id: string;
    postcode: string;
    request_date: string;
    organisation_name: string;
    contact_name: string;
    phone_number: string;
    email: string;
    comments: string;
    reason: string;
    collect_option: string;
    notes: string;
    misc_1: string;
    [key: string]: string;
}

// --- Load and Cache Item CSV Data ---

let cachedItemRecords: ItemRecord[] = [];
const itemCsvFilePath = 'data/allItemsWithCategories.csv';

try {
    console.log(`Attempting to load item records from: ${itemCsvFilePath}`);
    const itemFileContent = fs.readFileSync(itemCsvFilePath, 'utf8');
    const itemParsedData = Papa.parse<ItemRecord>(itemFileContent, {
        header: true, skipEmptyLines: true, dynamicTyping: false
    });
    if (itemParsedData.errors.length > 0) console.warn(`CSV parsing errors (Items):`, itemParsedData.errors);
    cachedItemRecords = itemParsedData.data.filter(row => typeof row === 'object' && row !== null);
    if (cachedItemRecords.length === 0 && itemParsedData.data.length > 0) console.warn(`Item CSV parsed but resulted in zero valid records.`);
    else console.log(`Successfully loaded ${cachedItemRecords.length} item records.`);
} catch (error) {
    console.error(`FATAL: Failed to load Item CSV: ${itemCsvFilePath}.`, error);
}

// --- Load and Cache Organisation CSV Data ---

let cachedOrganisationRecords: OrganisationRecord[] = [];
const orgCsvFilePath = 'data/organisations.csv';

try {
    console.log(`Attempting to load organisation records from: ${orgCsvFilePath}`);
    const orgFileContent = fs.readFileSync(orgCsvFilePath, 'utf8');
    const orgParsedData = Papa.parse<OrganisationRecord>(orgFileContent, {
        header: true, skipEmptyLines: true, dynamicTyping: false
    });
    if (orgParsedData.errors.length > 0) console.warn(`CSV parsing errors (Organisations):`, orgParsedData.errors);
    cachedOrganisationRecords = orgParsedData.data.filter(row => typeof row === 'object' && row !== null);
     if (cachedOrganisationRecords.length === 0 && orgParsedData.data.length > 0) console.warn(`Organisation CSV parsed but resulted in zero valid records.`);
    else console.log(`Successfully loaded ${cachedOrganisationRecords.length} organisation records.`);
} catch (error) {
    console.error(`FATAL: Failed to load Organisation CSV: ${orgCsvFilePath}.`, error);
}

// --- Helper Data (Fallbacks) ---
const fallbackCategory = 'desks';
const fallbackPostcode = 'SW1A 0AA';
const fallbackOrgName = 'Default Org';
const sampleItemKeywords: string[] = ['office', 'computer', 'wood', 'metal', 'plastic', 'large', 'small']; // Keep simple keywords for now

// --- Helper Functions ---

/**
 * Gets a random element from an array.
 * @param arr The array to sample from.
 * @returns A random element from the array, or undefined if the array is empty.
 */
function getRandomElement<T>(arr: T[]): T | undefined {
    if (!arr || arr.length === 0) {
        return undefined; // Handle empty array case
    }
    return arr[Math.floor(Math.random() * arr.length)];
}


function getRandomItemRecord(fieldName: keyof ItemRecord): string | undefined {
    if (!cachedItemRecords || cachedItemRecords.length === 0) return undefined;
    const randomRow = cachedItemRecords[Math.floor(Math.random() * cachedItemRecords.length)];
    if (randomRow && typeof randomRow === 'object' && fieldName in randomRow) {
        const value = randomRow[fieldName];
        return value !== null && value !== undefined ? String(value).trim() : undefined;
    }
    return undefined;
}

function getRandomOrganisationRecord(fieldName: keyof OrganisationRecord): string | undefined {
     if (!cachedOrganisationRecords || cachedOrganisationRecords.length === 0) return undefined;
    const randomRow = cachedOrganisationRecords[Math.floor(Math.random() * cachedOrganisationRecords.length)];
     if (randomRow && typeof randomRow === 'object' && fieldName in randomRow) {
        const value = randomRow[fieldName];
        return value !== null && value !== undefined ? String(value).trim() : undefined;
    }
    return undefined;
}

function generateTestName(base: string, complexity: number): string {
    return `${base}_comp${complexity}_${uuidv4().substring(0, 4)}`;
}

function mapDifficulty(complexity: number): 'easy' | 'medium' | 'hard' {
    if (complexity <= 3) return 'easy';
    if (complexity <= 7) return 'medium';
    return 'hard';
}

// --- Main Generator Function ---

export function createMedTemplate(modelName: string, complexity: number): MedTemplate {
    const clampedComplexity = Math.max(1, Math.min(10, complexity));
    let known_sql = "";
    let nl_focused = "";
    let nl = "";
    let nl_simple = "";
    let test_name_base = "";
    let query_type: string[] = ['SELECT'];

    // --- Corrected Complexity Logic Flow ---

    if (clampedComplexity === 1) { // Complexity 1: Simple SELECT ALL
        const tableChoice = Math.random() < 0.5 ? 'items' : 'organisations';
        if (tableChoice === 'items') {
            test_name_base = "select_all_items";
            query_type = ['SELECT'];
            known_sql = `SELECT i.item_name FROM items AS i;`;
            nl_focused = "Retrieve a list showing the names of all items available in the items table.";
            nl = "show all the item names";
            nl_simple = "items list";
        } else {
            test_name_base = "select_all_orgs";
            query_type = ['SELECT'];
            known_sql = `SELECT o.organisation_name FROM organisations AS o;`;
            nl_focused = "Generate a list containing the names of every organisation recorded in the organisations table.";
            nl = "list all organisations";
            nl_simple = "org names";
        }
    } else if (clampedComplexity === 2) { // Complexity 2: Simple SELECT with single WHERE
        const tableChoice = Math.random() < 0.5 ? 'items' : 'organisations';
        if (tableChoice === 'items') {
            const category = getRandomItemRecord("category") ?? fallbackCategory;
            test_name_base = "select_items_by_category_simple";
            query_type = ['SELECT', 'WHERE'];
            known_sql = `SELECT i.item_name FROM items AS i WHERE i.category = '${category}';`;
            nl_focused = `Retrieve a list showing only the names of items that belong to the exact category: '${category}'.`;
            nl = `show names of items in ${category} category`;
            nl_simple = `${category} item names`;
        } else {
            // Use organisation sampling for consistency
            const postcode = getRandomOrganisationRecord("postcode") ?? fallbackPostcode;
            test_name_base = "select_orgs_by_postcode_simple";
            query_type = ['SELECT', 'WHERE'];
            known_sql = `SELECT o.organisation_name FROM organisations AS o WHERE o.postcode = '${postcode}';`;
            nl_focused = `Generate a list containing the names of organisations located specifically in the postcode area '${postcode}'.`;
            nl = `list orgs in postcode ${postcode}`;
            nl_simple = `orgs ${postcode}`;
        }
    } else if (clampedComplexity <= 4) { // Complexity 3-4: SELECT columns with single WHERE
        const tableChoice = Math.random() < 0.5 ? 'items' : 'organisations';
        if (tableChoice === 'items') {
            const category = getRandomItemRecord("category") ?? fallbackCategory;
            test_name_base = "select_items_details_by_category";
            query_type = ['SELECT', 'WHERE'];
            known_sql = `SELECT i.item_name, i.item_description FROM items AS i WHERE i.category = '${category}';`;
            nl_focused = `Display the item name and description for all items belonging to the exact category '${category}'.`;
            nl = `show items in the ${category} category`;
            nl_simple = `${category} items?`;
        } else {
            // Use organisation sampling
            const postcode = getRandomOrganisationRecord("postcode") ?? fallbackPostcode;
            test_name_base = "select_orgs_details_by_postcode";
            query_type = ['SELECT', 'WHERE'];
            known_sql = `SELECT o.organisation_name, o.email FROM organisations AS o WHERE o.postcode = '${postcode}';`;
            nl_focused = `Provide the organisation name and email address for all organisations located in the postcode area '${postcode}'.`;
            nl = `find orgs with postcode ${postcode}`;
            nl_simple = `orgs ${postcode}`;
        }
    } else if (clampedComplexity <= 7) { // Complexity 5-7: Multiple WHERE conditions or ORDER BY
        const queryVariant = Math.random();
        if (queryVariant < 0.5) { // WHERE with two conditions (items)
            const category = getRandomItemRecord("category") ?? fallbackCategory;
            // Use getRandomElement for the simple keyword list
            const keyword = getRandomElement(sampleItemKeywords) ?? 'test';
            test_name_base = "select_items_category_keyword";
            query_type = ['SELECT', 'WHERE', 'AND', 'LIKE']; // Added LIKE
            known_sql = `SELECT i.item_name, i.category, i.size FROM items AS i WHERE i.category = '${category}' AND i.keywords LIKE '%${keyword}%';`;
            nl_focused = `Retrieve the item name, category, and size for items that belong to the category '${category}' and also have the keyword '${keyword}' associated with them.`;
            nl = `find ${category} items that mention ${keyword}`;
            nl_simple = `${category} ${keyword} items`;
        } else { // WHERE and ORDER BY (organisations)
            const date = new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
            test_name_base = "select_orgs_after_date_ordered";
            query_type = ['SELECT', 'WHERE', 'ORDER BY'];
            known_sql = `SELECT o.organisation_name, o.request_date FROM organisations AS o WHERE o.request_date > '${date}' ORDER BY o.request_date DESC;`;
            nl_focused = `List the names and request dates of all organisations whose request date is after ${date}, ordering the results with the most recent request date first.`;
            nl = `show orgs added since ${date} sorted by date`;
            nl_simple = `new orgs since ${date}? sort`;
        }
    } else { // Complexity 8-10: Complex WHERE, multiple ORDER BY, LIMIT, Aggregation
        const queryVariant = Math.random();
        if (queryVariant < 0.33) { // Complex WHERE (items)
            const cat1 = getRandomItemRecord("category") ?? fallbackCategory;
            let cat2 = getRandomItemRecord("category") ?? fallbackCategory + "2";
            let attempts = 0;
            while (cat1 === cat2 && attempts < 5 && cachedItemRecords.length > 1) {
                cat2 = getRandomItemRecord("category") ?? fallbackCategory + "2"; attempts++;
            }
            const keyword = getRandomItemRecord("item_name")?.split(' ')[0] ?? 'item';
            test_name_base = "select_items_complex_filter";
            query_type = ['SELECT', 'WHERE', 'OR', 'AND', 'LIKE'];
            known_sql = `SELECT i.item_name, i.category FROM items AS i WHERE (i.category = '${cat1}' OR i.category = '${cat2}') AND i.item_name LIKE '%${keyword}%';`;
            nl_focused = `Display the item name and category for items whose category is either '${cat1}' or '${cat2}', and whose item name contains the term '${keyword}'.`;
            nl = `show ${cat1} or ${cat2} items with ${keyword} in the name`;
            nl_simple = `${cat1}/${cat2} ${keyword} things`;
        } else if (queryVariant < 0.66) { // ORDER BY multiple, LIMIT (organisations)
            test_name_base = "select_orgs_ordered_limit";
            query_type = ['SELECT', 'ORDER BY', 'LIMIT'];
            known_sql = `SELECT o.organisation_name, o.postcode, o.request_date FROM organisations AS o ORDER BY o.postcode ASC, o.request_date DESC LIMIT 5;`;
            nl_focused = "Retrieve the organisation name, postcode, and request date for the first 5 organisations when ordered primarily by postcode ascending, and secondarily by request date descending.";
            nl = "top 5 orgs sorted by postcode then date";
            nl_simple = "5 orgs postcode/date sort";
        } else { // Aggregation (COUNT) with WHERE (items)
            const category = getRandomItemRecord("category") ?? fallbackCategory;
            test_name_base = "count_items_by_category";
            query_type = ['SELECT', 'AGGREGATE', 'WHERE'];
            known_sql = `SELECT COUNT(i.item_id) FROM items AS i WHERE i.category = '${category}';`;
            nl_focused = `Calculate the total number of items that belong to the specific category '${category}'.`;
            nl = `how many ${category} items are there?`;
            nl_simple = `count ${category}`;
        }
    }

    // --- Assemble the MedTemplate Object ---
    const template: MedTemplate = {
        input: {
            test_name: generateTestName(test_name_base, clampedComplexity),
            nl_focused: nl_focused,
            nl: nl,
            nl_simple: nl_simple,
            known_sql: known_sql,
            expected_result_data: [],
            expected_result_row_count: null,
            model_name: modelName, // Use the parameter here
            difficulty: mapDifficulty(clampedComplexity),
            complexity_score: clampedComplexity,
            query_type: query_type,
        },
        output: { llm_sql: "", results: "" },
        analysis: { is_valid_sql: null, accuracy: null, accuracy_notes: null },
    };

    return template;
}

//======================================================================================
// --- Define an interface for the expected data from genSQL ---
export interface AutogenSqlData {
    sql: string;
    nl_focused: string;
    nl: string;
    nl_simple: string;
}

/**
 * Creates a MedTemplate object from model/complexity info and a parsed object
 * containing the generated SQL and NL variants.
 *
 * @param modelName The name of the model being tested.
 * @param complexity The complexity score (1-10) used to generate the inputs.
 * @param autogenSQLData An object containing sql, nl_focused, nl, and nl_simple strings.
 * @returns A MedTemplate object populated with the inputs.
 */
export function createTemplateFromInput(
    modelName: string,
    complexity: number,
    autogenSQLData: AutogenSqlData // Accept the parsed object directly
): MedTemplate {

    // Ensure complexity is within bounds for mapping difficulty
    const clampedComplexity = Math.max(1, Math.min(10, complexity));

    // Determine a base name for the test
    let test_name_base = "input_generated";
     if (autogenSQLData.sql.toLowerCase().includes('items')) {
        test_name_base = "items_input_gen";
    } else if (autogenSQLData.sql.toLowerCase().includes('organisations')) {
         test_name_base = "orgs_input_gen";
    }

    // Basic query type detection
    let query_type: string[] = [];
    const lowerSql = autogenSQLData.sql.toLowerCase(); // Use data from the object
    if (lowerSql.startsWith('select')) query_type.push('SELECT');
    if (lowerSql.includes('where')) query_type.push('WHERE');
    if (lowerSql.includes('order by')) query_type.push('ORDER BY');
    if (lowerSql.includes('limit')) query_type.push('LIMIT');
    if (lowerSql.includes('count(') || lowerSql.includes('avg(') || lowerSql.includes('sum(')) query_type.push('AGGREGATE');
    if (lowerSql.includes(' join ')) query_type.push('JOIN');


    // --- Assemble the MedTemplate Object ---
    const template: MedTemplate = {
        input: {
            test_name: generateTestName(test_name_base, clampedComplexity),
            // Access properties from the generatedData object
            nl_focused: autogenSQLData.nl_focused,
            nl: autogenSQLData.nl,
            nl_simple: autogenSQLData.nl_simple,
            known_sql: autogenSQLData.sql,
            expected_result_data: [],
            expected_result_row_count: null,
            model_name: modelName,
            difficulty: mapDifficulty(clampedComplexity),
            complexity_score: clampedComplexity,
            query_type: query_type,
        },
        output: {
            llm_sql: "",
            results: ""
        },
        analysis: {
            is_valid_sql: null,
            accuracy: null,
            accuracy_notes: null
        },
    };

    return template;
}


