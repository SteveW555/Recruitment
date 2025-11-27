import * as fs from 'fs';
import * as path from 'path';
import { formatAddressBlock } from './addressParser';

const testsDir = path.join(process.cwd(), 'src/invoice/AddressTests');

if (!fs.existsSync(testsDir)) {
    console.error(`Test directory not found: ${testsDir}`);
    process.exit(1);
}

const files = fs.readdirSync(testsDir).filter(f => f.endsWith('.txt'));

if (files.length === 0) {
    console.error(`No .txt test files found in: ${testsDir}`);
    process.exit(1);
}

console.log(`Found ${files.length} test files: ${files.join(', ')}\n`);

let totalFailures = 0;

files.forEach(fileName => {
    console.log(`\n##################################################`);
    console.log(`Running tests from: ${fileName}`);
    console.log(`##################################################`);

    const testFilePath = path.join(testsDir, fileName);
    const fileContent = fs.readFileSync(testFilePath, 'utf-8');

    const sections = fileContent.split('---').map(s => s.trim()).filter(s => s.length > 0);

    if (sections.length === 0) {
        console.log("No sections found in file.");
        return;
    }

    const idealResult = sections[0].split('\n').map(l => l.trim()).filter(l => l.length > 0);

    console.log("=== Ideal Result ===");
    console.log(idealResult);

    sections.slice(1).forEach((section, index) => {
        console.log(`\n=== Variation ${index + 1} ===`);
        console.log("Input:");
        console.log(section);

        const result = formatAddressBlock(section);
        console.log("Output:");
        console.log(result);

        // Simple comparison
        const isMatch = JSON.stringify(result) === JSON.stringify(idealResult);
        console.log(`Match Ideal? ${isMatch ? '✅' : '❌'}`);

        if (!isMatch) {
            totalFailures++;
            console.log("Diff:");
            // Basic diff output
            idealResult.forEach((line, i) => {
                if (result[i] !== line) {
                    console.log(`  Expected [${i}]: "${line}"`);
                    console.log(`  Actual   [${i}]: "${result[i] || '(missing)'}"`);
                }
            });
            if (result.length > idealResult.length) {
                console.log(`  Actual has extra lines:`, result.slice(idealResult.length));
            }
        }
    });
});

if (totalFailures > 0) {
    console.log(`\n❌ Total Failures: ${totalFailures}`);
    process.exit(1);
} else {
    console.log(`\n✅ All Tests Passed!`);
}
