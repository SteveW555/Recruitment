import { buildInvoice } from './src/invoice/invoiceBuilder';
import { parseEmployeeData } from './src/services/employeeService';
import * as path from 'path';
import * as fs from 'fs';

// Load logo image
const logoPath = path.join(process.cwd(), 'ProactivePeople.png');
const logoBuffer = fs.readFileSync(logoPath);

// Load and parse employee data
const employeeDataPath = path.join(process.cwd(), 'email.csv');
const employees = parseEmployeeData(employeeDataPath);

// Sample invoice data using real address from AddressTests.txt
const invoiceData = {
    logoBuffer: new Uint8Array(logoBuffer),
    employees: employees,
    addressText: `
        BILL TO: Strategic Communications Inc (UK) Limited
        Attn: Finance Dept
        VAT Reg: GB 987 6543 21
        Sovereign House, 15 Towcester Road
        Old Stratford, Milton Keynes
        Buckinghamshire
        MK19 6AN
    `,
    invoiceRef: '10010097',
    invoiceDate: '3rd November 2025'
};

const outputPath = path.join(process.cwd(), 'strategic-comms-invoice.docx');

// Generate the invoice
async function generateTestInvoice() {
    try {
        console.log('Generating invoice...');
        console.log('Logo path:', logoPath);
        console.log('Employee data path:', employeeDataPath);
        console.log('Output path:', outputPath);

        await buildInvoice(invoiceData, outputPath);
        console.log('\n✅ Invoice generated successfully!');
        console.log(`📄 Output: ${outputPath}`);
    } catch (error) {
        console.error('❌ Error generating invoice:', error);
        process.exit(1);
    }
}

generateTestInvoice();
