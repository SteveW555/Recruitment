import * as XLSX from 'xlsx';
import Papa from 'papaparse';
import type { ParsedData } from '../types';

export async function parseSpreadsheet(file: File): Promise<ParsedData> {
  const extension = file.name.split('.').pop()?.toLowerCase();

  if (extension === 'csv') {
    return parseCSV(file);
  } else if (extension === 'xlsx' || extension === 'xls') {
    return parseExcel(file);
  } else {
    throw new Error('Unsupported file format. Please use .csv, .xlsx, or .xls');
  }
}

async function parseCSV(file: File): Promise<ParsedData> {
  return new Promise((resolve, reject) => {
    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        if (results.errors.length > 0) {
          reject(new Error(`CSV parsing error: ${results.errors[0].message}`));
          return;
        }
        resolve({
          headers: results.meta.fields || [],
          rows: results.data as Record<string, any>[],
        });
      },
      error: (error) => reject(error),
    });
  });
}

async function parseExcel(file: File): Promise<ParsedData> {
  const buffer = await file.arrayBuffer();
  const workbook = XLSX.read(buffer, { type: 'array' });

  const firstSheetName = workbook.SheetNames[0];
  const worksheet = workbook.Sheets[firstSheetName];

  const jsonData: any[] = XLSX.utils.sheet_to_json(worksheet);

  if (jsonData.length === 0) {
    throw new Error('Spreadsheet is empty');
  }

  const headers = Object.keys(jsonData[0]);

  return {
    headers,
    rows: jsonData,
  };
}
