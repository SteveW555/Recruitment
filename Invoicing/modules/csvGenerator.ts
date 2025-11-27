import Papa from 'papaparse';

export function generateCSV(data: Record<string, any>[]): string {
  return Papa.unparse(data, {
    header: true,
    skipEmptyLines: true,
  });
}
