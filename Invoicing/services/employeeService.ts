import * as fs from 'fs';

export interface EmployeeData {
    name: string;
    hours: number;
    hourlyRate: number;
    bonus: number;
    total: number;
}

// Helper function to parse employee CSV data
export function parseEmployeeData(csvPath: string): EmployeeData[] {
    const csvContent = fs.readFileSync(csvPath, 'utf-8');
    const lines = csvContent.split('\n').slice(1); // Skip header

    return lines
        .filter(line => line.trim().length > 0)
        .map(line => {
            const parts = line.split(',');
            return {
                name: parts[0].trim(),
                hours: parseFloat(parts[1]),
                hourlyRate: parseFloat(parts[2]),
                bonus: parseFloat(parts[3]),
                total: parseFloat(parts[4])
            };
        });
}
