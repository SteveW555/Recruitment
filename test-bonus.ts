import fs from 'fs';
import path from 'path';
import Papa from 'papaparse';
import { complete, configure } from './src/modules/llm';
import type { ParsedData } from './src/types';

// Load environment variables from .env file manually for Node execution
try {
    const envPath = path.resolve(process.cwd(), '.env');
    if (fs.existsSync(envPath)) {
        const envConfig = fs.readFileSync(envPath, 'utf-8');
        envConfig.split('\n').forEach(line => {
            const [key, value] = line.split('=');
            if (key && value) {
                process.env[key.trim()] = value.trim();
            }
        });
    }
} catch (e) {
    console.warn('Could not load .env file');
}

// Configure LLM with loaded environment variables
configure({
    apiKeys: {
        openai: process.env.VITE_OPENAI_API_KEY,
        anthropic: process.env.VITE_ANTHROPIC_API_KEY,
        groq: process.env.VITE_GROQ_API_KEY,
        openrouter: process.env.VITE_OPENROUTER_API_KEY,
    }
});

async function runTest() {
    // Get filename from command line arguments, default to 'Invoicing source.csv'
    const args = process.argv.slice(2);
    const filename = args[0] || 'Invoicing source.csv';

    console.log(`Starting Bonus Extraction Test on file: ${filename}`);

    // 1. Read CSV
    const csvPath = path.resolve(process.cwd(), filename);
    if (!fs.existsSync(csvPath)) {
        console.error(`File not found: ${csvPath}`);
        console.log('Usage: npx tsx test-bonus.ts <filename>');
        return;
    }

    const csvContent = fs.readFileSync(csvPath, 'utf-8');
    const parsed = Papa.parse(csvContent, { header: true, skipEmptyLines: true });

    const parsedData: ParsedData = {
        headers: parsed.meta.fields || [],
        rows: parsed.data as Record<string, any>[]
    };

    console.log(`Loaded ${parsedData.rows.length} rows.`);

    // 2. Read Prompt
    const promptPath = path.resolve(process.cwd(), 'src/prompts/employee_bonuses_summary.txt');
    if (!fs.existsSync(promptPath)) {
        console.error(`Prompt file not found: ${promptPath}`);
        return;
    }
    const systemPrompt = fs.readFileSync(promptPath, 'utf-8');

    // 3. Prepare Data for LLM
    // Convert parsed data back to CSV string for the prompt
    const csvString = [
        parsedData.headers.join(','),
        ...parsedData.rows.map(row =>
            parsedData.headers.map(h => {
                const val = row[h];
                return (typeof val === 'string' && val.includes(',')) ? `"${val}"` : (val ?? '');
            }).join(',')
        )
    ].join('\n');

    // 4. Call LLM
    console.log('Calling LLM...');
    try {
        const response = await complete({
            model: 'gpt-5-nano-2025-08-07',
            systemPrompt,
            userPrompt: csvString,
            temperature: 0.1,
            maxTokens: 4096
        });

        console.log('LLM Response received.');

        // 5. Parse Response
        let cleanedContent = response.content.trim();
        if (cleanedContent.startsWith('```json')) {
            cleanedContent = cleanedContent.replace(/^```json\s*/, '').replace(/\s*```$/, '');
        } else if (cleanedContent.startsWith('```')) {
            cleanedContent = cleanedContent.replace(/^```\s*/, '').replace(/\s*```$/, '');
        }

        const result = JSON.parse(cleanedContent);
        console.log('\n=== EXTRACTION RESULT ===');
        console.log(JSON.stringify(result, null, 2));

    } catch (error) {
        console.error('Error during extraction:', error);
    }
}

runTest();
