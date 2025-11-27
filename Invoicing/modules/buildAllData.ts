import type { ExtractedHoursData, ParsedData, CombinedData } from '../types';

/**
 * Combines extracted employee hours with rate and bonus information.
 *
 * @param extractedData - Data extracted from the hours spreadsheet
 * @param ratesData - Data parsed from the rates CSV
 * @param bonusData - (Optional) Data parsed from the bonus CSV
 * @param holidayData - (Optional) Data parsed from the holiday CSV
 * @returns Array of combined data with calculated totals
 */
export function buildAllData(
    extractedData: ExtractedHoursData,
    ratesData: ParsedData,
    bonusData?: ParsedData,
    holidayData?: ParsedData
): CombinedData[] {
    // 1. Create a map for Rates: Name -> Rate
    const rateMap = new Map<string, number>();

    // Find the rate column (assume it's the first numeric column after the name)
    // For now, we'll look for a column named "Rate" or similar, or just pick the second column
    // Based on PersonRate.csv: Name, Rate
    const rateHeaders = ratesData.headers;
    const rateNameCol = rateHeaders[0]; // Assume first col is name
    const rateValueCol = rateHeaders.find(h => h.toLowerCase().includes('rate')) || rateHeaders[1];

    for (const row of ratesData.rows) {
        const name = String(row[rateNameCol] || '').trim();
        const rateStr = row[rateValueCol];
        const rate = parseFloat(String(rateStr));

        if (name && !isNaN(rate)) {
            // Normalize name for matching (simple lowercase trim for now)
            rateMap.set(name.toLowerCase(), rate);
        }
    }

    // 2. Create a map for Bonuses: Name -> Bonus
    const bonusMap = new Map<string, number>();

    if (bonusData) {
        const bonusHeaders = bonusData.headers;
        const bonusNameCol = bonusHeaders[0]; // Assume first col is name
        // Based on PersonBonus.csv, it seems to be Name, BonusAmount
        // But wait, looking at the file content:
        // Row 1: Enhancement Bonus OCT 27th 2025,
        // Row 2: Alison Coulter,14.36
        // It seems the header might be the first row, or maybe it's headerless?
        // Let's assume standard parsing where headers are detected.
        // If the first row is "Enhancement Bonus...", that might be the header for the second col?
        // Actually, let's look at the file content again.
        // 1: Enhancement Bonus OCT 27th 2025,
        // 2: Alison Coulter,14.36
        // PapaParse might treat line 1 as headers: ["Enhancement Bonus...", ""]
        // So column 0 is name, column 1 is bonus.

        const bonusValueCol = bonusHeaders[1] || bonusHeaders.find(h => h.toLowerCase().includes('bonus'));

        for (const row of bonusData.rows) {
            const name = String(row[bonusNameCol] || '').trim();
            const bonusStr = row[bonusValueCol as string]; // Cast because we know it exists if we're here, or undefined
            const bonus = parseFloat(String(bonusStr));

            if (name && !isNaN(bonus)) {
                bonusMap.set(name.toLowerCase(), bonus);
            }
        }
    }

    // 3. Create a map for Holiday Hours: Name -> Hours
    const holidayMap = new Map<string, number>();

    if (holidayData) {
        const holidayHeaders = holidayData.headers;
        const holidayNameCol = holidayHeaders[0]; // Assume first col is name
        const holidayValueCol = holidayHeaders[1] || holidayHeaders.find(h => h.toLowerCase().includes('holiday') || h.toLowerCase().includes('hours'));

        for (const row of holidayData.rows) {
            const name = String(row[holidayNameCol] || '').trim();
            const holidayStr = row[holidayValueCol as string];
            const holiday = parseFloat(String(holidayStr));

            if (name && !isNaN(holiday)) {
                holidayMap.set(name.toLowerCase(), holiday);
            }
        }
    }

    // 4. Combine Data
    const combined: CombinedData[] = extractedData.data.map(item => {
        const normalizedName = item.employee.trim().toLowerCase();

        // Lookup Rate
        // Try exact match first, then fuzzy if needed (for now just exact/normalized)
        let rate = rateMap.get(normalizedName);

        // Fallback: Try to find by partial match if not found?
        // For now, default to 0 if not found.
        if (rate === undefined) {
            console.warn(`Rate not found for employee: ${item.employee}`);
            rate = 0;
        }

        // Lookup Bonus
        let bonus = bonusMap.get(normalizedName) || 0;

        // Lookup Holiday Hours
        let holidayHours = holidayMap.get(normalizedName) || 0;

        // Calculate Total
        // Total = (Hours * Rate) + Bonus + (HolidayHours * Rate)
        const total = (item.hours * rate) + bonus + (holidayHours * rate);

        return {
            name: item.employee,
            hours: item.hours,
            rate,
            bonus,
            holidayHours,
            total
        };
    });

    return combined;
}

/**
 * Combines MasterDataEntry (already merged hours/bonuses) with rate and holiday information.
 */
import type { MasterDataEntry } from './masterDataTable';

export function buildAllDataFromMaster(
    masterData: MasterDataEntry[],
    ratesData: ParsedData,
    holidayData?: ParsedData
): CombinedData[] {
    // 1. Create a map for Rates: Name -> Rate
    const rateMap = new Map<string, number>();
    const rateHeaders = ratesData.headers;
    const rateNameCol = rateHeaders[0];
    const rateValueCol = rateHeaders.find(h => h.toLowerCase().includes('rate')) || rateHeaders[1];

    for (const row of ratesData.rows) {
        const name = String(row[rateNameCol] || '').trim();
        const rateStr = row[rateValueCol];
        const rate = parseFloat(String(rateStr));
        if (name && !isNaN(rate)) {
            rateMap.set(name.toLowerCase(), rate);
        }
    }

    // 2. Create a map for Holiday Hours: Name -> Hours
    const holidayMap = new Map<string, number>();
    if (holidayData) {
        const holidayHeaders = holidayData.headers;
        const holidayNameCol = holidayHeaders[0];
        const holidayValueCol = holidayHeaders[1] || holidayHeaders.find(h => h.toLowerCase().includes('holiday') || h.toLowerCase().includes('hours'));

        for (const row of holidayData.rows) {
            const name = String(row[holidayNameCol] || '').trim();
            const holidayStr = row[holidayValueCol as string];
            const holiday = parseFloat(String(holidayStr));
            if (name && !isNaN(holiday)) {
                holidayMap.set(name.toLowerCase(), holiday);
            }
        }
    }

    // 3. Combine Data
    return masterData.map(item => {
        const normalizedName = item.employeeName.trim().toLowerCase();

        // Lookup Rate
        let rate = rateMap.get(normalizedName);
        if (rate === undefined) {
            console.warn(`Rate not found for employee: ${item.employeeName}`);
            rate = 0;
        }

        // Bonus is already in MasterDataEntry
        const bonus = item.bonus;

        // Lookup Holiday Hours
        let holidayHours = holidayMap.get(normalizedName) || 0;

        // Calculate Total
        const total = (item.totalHours * rate) + bonus + (holidayHours * rate);

        return {
            name: item.employeeName,
            hours: item.totalHours,
            rate,
            bonus,
            holidayHours,
            total
        };
    });
}
