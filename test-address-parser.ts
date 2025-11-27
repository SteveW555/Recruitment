import { formatAddressBlock } from './src/invoice/addressParser';

const testAddress = `
    BILL TO: Strategic Communications Inc (UK) Limited
    Attn: Finance Dept
    VAT Reg: GB 987 6543 21
    Sovereign House, 15 Towcester Road
    Old Stratford, Milton Keynes
    Buckinghamshire
    MK19 6AN
`;

const result = formatAddressBlock(testAddress);

console.log('Parsed address lines:');
result.forEach((line, index) => {
    console.log(`${index + 1}. "${line}"`);
});

console.log(`\nTotal lines: ${result.length}`);
