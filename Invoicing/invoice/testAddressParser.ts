import { formatAddressBlock } from './addressParser';

const exampleText = `STRATEGIC COMMUNICATIONS INC (UK) LIMITED is registered as company number 11193434 in England and Wales. Registered address is Sovereign House 15 Towcester Road, Old Stratford, Milton Keynes, Buckinghamshire,

United Kingdom, MK19 6AN`;

console.log("--- Input Text ---");
console.log(exampleText);
console.log("\n--- Parsed Output ---");
const result = formatAddressBlock(exampleText);
console.log(result);

if (result.length === 6 && result[0] === 'STRATEGIC COMMUNICATIONS INC (UK) LIMITED' && result[5] === 'MK19 6AN') {
    console.log("\n✅ Test Passed!");
} else {
    console.log("\n❌ Test Failed!");
}
