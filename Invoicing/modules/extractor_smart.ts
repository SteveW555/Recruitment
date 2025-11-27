import type { ParsedData, ExtractedHoursData } from '../types';

interface DataCluster {
    nameCol: string;
    hoursCol: string;
    rows: Array<{ rowIdx: number; name: string; hours: number }>;
    score: number;
}

/**
 * ROBUST EXTRACTION STRATEGY ("Island Hopping")
 * * Instead of looking for one perfect table, this finds all "clusters" of 
 * name/hour pairs and picks the best one based on "Summary-likeness".
 */
export function extractEmployeeHours(parsed: ParsedData): ExtractedHoursData {
    const { headers, rows } = parsed;
    const clusters: DataCluster[] = [];

    console.log('\n=== ISLAND HOPPING EXTRACTION STRATEGY ===');
    console.log(`Total rows: ${rows.length}`);
    console.log(`Total columns: ${headers.length}`);
    console.log(`Column headers:`, headers);
    console.log('\nScanning for data islands (clusters of name+hours pairs)...\n');

    // 1. Iterate through all column combinations (Name Col vs Hours Col)
    for (let i = 0; i < headers.length; i++) {
        const nameColKey = headers[i];

        // Limit search to neighbors (Hours must be within 4 cols of Name)
        for (let j = i + 1; j < Math.min(i + 4, headers.length); j++) {
            const hoursColKey = headers[j];

            let currentCluster: DataCluster['rows'] = [];
            let gapCounter = 0;

            // 2. Scan EVERY row (Do not break on empty rows)
            for (let r = 0; r < rows.length; r++) {
                const row = rows[r];
                const nameVal = row[nameColKey];
                const hoursVal = row[hoursColKey];

                if (isLikelyName(nameVal) && isLikelyHours(hoursVal)) {
                    currentCluster.push({
                        rowIdx: r,
                        name: String(nameVal).trim(),
                        hours: parseFloat(hoursVal)
                    });
                    gapCounter = 0;
                } else {
                    if (currentCluster.length > 0) {
                        gapCounter++;
                    }
                }

                // 3. Seal the Island if the gap is too big (>3 rows)
                if (gapCounter > 3 && currentCluster.length > 0) {
                    const clusterToAdd = {
                        nameCol: nameColKey,
                        hoursCol: hoursColKey,
                        rows: [...currentCluster],
                        score: 0
                    };
                    clusters.push(clusterToAdd);
                    console.log(`  Found island: "${nameColKey}" + "${hoursColKey}" → ${currentCluster.length} rows (sealed by gap)`);
                    currentCluster = [];
                    gapCounter = 0;
                }
            }

            if (currentCluster.length > 0) {
                const clusterToAdd = {
                    nameCol: nameColKey,
                    hoursCol: hoursColKey,
                    rows: [...currentCluster],
                    score: 0
                };
                clusters.push(clusterToAdd);
                console.log(`  Found island: "${nameColKey}" + "${hoursColKey}" → ${currentCluster.length} rows (end of file)`);
            }
        }
    }

    console.log(`\n=== FOUND ${clusters.length} DATA ISLANDS ===\n`);

    // 4. Score the Clusters
    console.log('Scoring islands (prefers summary tables over detail logs):\n');

    let bestCluster: DataCluster | null = null;
    let maxScore = -1;

    const scoredClusters = [];
    for (const cluster of clusters) {
        if (cluster.rows.length < 2) {
            console.log(`  ❌ Skipped: "${cluster.nameCol}" + "${cluster.hoursCol}" (only ${cluster.rows.length} row, need 2+)`);
            continue;
        }

        const uniqueNames = new Set(cluster.rows.map(r => r.name));
        const size = cluster.rows.length;
        const uniqueness = uniqueNames.size / size;

        // SCORING: Size * (Uniqueness^2) -> Prefers Summary Tables over Logs
        const score = size * (uniqueness * uniqueness);
        cluster.score = score;

        scoredClusters.push({
            cluster,
            uniqueNames: uniqueNames.size,
            size,
            uniqueness,
            score
        });

        console.log(`  "${cluster.nameCol}" + "${cluster.hoursCol}":`);
        console.log(`    Rows: ${size}`);
        console.log(`    Unique names: ${uniqueNames.size}`);
        console.log(`    Uniqueness: ${(uniqueness * 100).toFixed(1)}%`);
        console.log(`    Score: ${size} × (${uniqueness.toFixed(3)}²) = ${score.toFixed(2)}`);

        if (score > maxScore) {
            maxScore = score;
            bestCluster = cluster;
        }
    }

    // Sort and show top candidates
    scoredClusters.sort((a, b) => b.score - a.score);
    console.log(`\n=== TOP 3 ISLANDS (sorted by score) ===\n`);
    scoredClusters.slice(0, 3).forEach((sc, idx) => {
        const marker = sc.cluster === bestCluster ? '🏆' : '  ';
        console.log(`${marker} ${idx + 1}. "${sc.cluster.nameCol}" + "${sc.cluster.hoursCol}" → Score: ${sc.score.toFixed(2)}`);
    });

    // --- ERROR HANDLING (Corrected to match ExtractedData interface) ---
    if (!bestCluster) {
        console.warn("\n❌ No valid employee data found.");
        return {
            employeeColumn: '',
            hoursColumn: '',
            startRow: 0,
            endRow: 0,
            data: [],
            preview: []
        };
    }

    console.log(`\n=== SELECTED WINNER ===`);
    console.log(`Name Column: "${bestCluster.nameCol}"`);
    console.log(`Hours Column: "${bestCluster.hoursCol}"`);
    console.log(`Score: ${bestCluster.score.toFixed(2)}`);
    console.log(`Raw rows in island: ${bestCluster.rows.length}`);
    console.log(`Row range: ${bestCluster.rows[0].rowIdx + 1} to ${bestCluster.rows[bestCluster.rows.length - 1].rowIdx + 1}`);

    // 5. Format Output - Aggregate duplicate employees
    const aggregated = new Map<string, number>();

    for (const entry of bestCluster.rows) {
        const current = aggregated.get(entry.name) || 0;
        aggregated.set(entry.name, current + entry.hours);
    }

    const finalData = Array.from(aggregated.entries())
        .map(([employee, hours]) => ({
            employee,
            hours
        }))
        .sort((a, b) => b.hours - a.hours);

    console.log(`\n=== AGGREGATION ===`);
    console.log(`After aggregating duplicates: ${finalData.length} unique employees`);
    console.log(`Preview (top 3):`, finalData.slice(0, 3));
    console.log('===========================\n');

    return {
        employeeColumn: bestCluster.nameCol,
        hoursColumn: bestCluster.hoursCol,
        startRow: bestCluster.rows[0].rowIdx,
        endRow: bestCluster.rows[bestCluster.rows.length - 1].rowIdx,
        data: finalData,
        preview: finalData.slice(0, 5)
    };
}

// --- HELPER FUNCTIONS ---

function isLikelyName(val: any): boolean {
    if (typeof val !== 'string') return false;
    const str = val.trim();
    if (str.length < 3) return false;
    const stopWords = ['total', 'sum', 'bonus', 'week', 'invoice', 'description',
        'amount', 'pay', 'staff', 'proactive', 'internal', 'breakdown'];
    const lower = str.toLowerCase();
    if (stopWords.some(w => lower.includes(w))) return false;
    return /[a-zA-Z]/.test(str) && !/\d/.test(str);
}

function isLikelyHours(val: any): boolean {
    if (val === null || val === undefined || val === '') return false;
    const num = parseFloat(val);
    if (isNaN(num)) return false;
    return num >= 0 && num <= 168;
}