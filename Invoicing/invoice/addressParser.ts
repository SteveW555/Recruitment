export const formatAddressBlock = (rawInput: string): string[] => {
    // 1. Defined known "Noise" phrases to strip out entirely (replaced with newline)
    const noisePatterns = [
        /is registered as company number \d+ in England and Wales\.?/gi,
        /Registered address is/gi,
        /\(?United Kingdom\)?/gi,
        /\(?Great Britain\)?/gi,
        /\(?England\)?/gi,
        /\(?Wales\)?/gi,
        /Company No:?\s*\d+/gi, // Remove Company No lines
        /VAT Reg:?\s*[A-Z0-9 ]+/gi, // Remove VAT Reg lines
        /\(Side Entrance - Ring Bell\)/gi, // Specific noise
        /\(CUST REF:[^)]*\)/gi, // Customer Ref noise (in parens)
    ];

    let cleanText = rawInput;
    noisePatterns.forEach(pattern => {
        cleanText = cleanText.replace(pattern, '\n');
    });

    // 2. Split by comma, newline, pipe, bullet, or tab
    // Also split if we see "House" or similar followed immediately by a number (e.g. "Sovereign House 15")
    cleanText = cleanText.replace(/(House|Building|Court|Lodge)\s+(\d+)/gi, '$1\n$2');

    const parts = cleanText.split(/,|\n|\||•|\t/);

    // 3. Clean up individual lines
    const addressLines = parts
        .map(p => {
            let line = p.trim();
            // Strip common prefixes
            line = line.replace(/^(BILL TO|Attn|Account Name|Registered Office|Invoice To|Deliver to):?\s*/i, '');

            // Helper for Title Case
            const toTitleCase = (str: string) => {
                // Special case for (UK)
                if (/\(UK\)/i.test(str)) {
                    return str.replace(/\(UK\)/i, '(UK)').replace(/\b(?!UK\b)\w\S*/g, (txt) => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase());
                }
                return str.replace(/\w\S*/g, (txt) => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase());
            };

            // Helper for Postcode detection (Simplified UK)
            const isPostcode = (str: string) => {
                return /^[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}$/i.test(str);
            };

            // Normalize Case: If ALL CAPS or all lower, convert to Title Case (except Postcodes)
            // We preserve mixed-case (e.g. "TechFlow")
            if ((line === line.toUpperCase() && /[A-Z]/.test(line)) || (line === line.toLowerCase() && /[a-z]/.test(line))) {
                if (isPostcode(line)) {
                    line = line.toUpperCase();
                } else {
                    line = toTitleCase(line);
                }
            }

            return line;
        })
        .filter(p => {
            if (p.length === 0) return false;

            // Filter out unwanted lines
            const lower = p.toLowerCase();
            if (lower.startsWith('tel:')) return false;
            if (lower.startsWith('fax:')) return false;
            if (lower.includes('@')) return false; // Email
            if (lower.startsWith('www.') || lower.startsWith('http')) return false; // URL
            if (/^\d+$/.test(p)) return false; // Just numbers (likely company number leftover)
            if (lower.includes('finance dept')) return false; // Specific noise

            return true;
        });

    return addressLines;
};
