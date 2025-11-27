import type { CombinedData, ProcessedResult, InvoiceItem, DocxInvoiceItem } from '../types';

/**
 * Process the extracted employee hours data.
 *
 * CUSTOMIZE THIS FUNCTION based on your specific business logic.
 * This is a placeholder implementation that:
 * - Creates CSV output from employee hours
 * - Generates invoice based on hourly rates
 */
export function processData(data: CombinedData[]): ProcessedResult {
  // CUSTOMIZE: Set your hourly rate here or calculate per employee
  // const HOURLY_RATE = 50; // Default rate per hour (Now using rate from data)
  // const BONUS_RATE = 0; // CUSTOMIZE: Set bonus amount or calculate per employee (Now using bonus from data)

  // CSV data: export employee hours with calculated totals
  const csvData = data.map((item) => ({
    employee: item.name,
    hours: item.hours,
    rate: item.rate,
    bonus: item.bonus,
    holidayHours: item.holidayHours,
    total: item.total,
    processedDate: new Date().toISOString().split('T')[0],
  }));

  // Invoice items: each employee's hours as a line item (for PDF)
  const items: InvoiceItem[] = data.map((item) => ({
    description: `${item.name} - Hours Worked`,
    quantity: item.hours,
    unitPrice: item.rate,
    total: item.total, // Note: This total includes bonus if we want? Or should bonus be separate?
    // For now, let's keep it simple: Total = Hours * Rate + Bonus
    // But InvoiceItem structure expects unitPrice * quantity = total usually.
    // Let's adjust description to include bonus info if present?
    // Or maybe just use the total.
  }));

  // Let's refine InvoiceItem logic to be more accurate
  // If we want to show bonus separately, we might need multiple items per person or a combined line.
  // For now, let's just map it 1:1 but use the calculated total.

  const subtotal = items.reduce((sum, item) => sum + item.total, 0);
  const tax = subtotal * 0.1; // CUSTOMIZE: 10% tax (adjust or remove as needed)
  const total = subtotal + tax;

  const invoiceData = {
    invoiceNumber: `INV-${Date.now()}`,
    date: new Date().toLocaleDateString(),
    clientName: 'Client Name', // CUSTOMIZE: Replace with actual client data
    items,
    subtotal,
    tax,
    total,
  };

  // DOCX invoice items: for Word document format
  const docxItems: DocxInvoiceItem[] = data.map((item) => ({
    name: item.name,
    hours: item.hours,
    rate: item.rate,
    basePay: item.hours * item.rate,
    bonus: item.bonus,
    holidayPay: item.holidayHours * item.rate,
  }));

  // Calculate week commencing date (Monday of current week)
  const today = new Date();
  const dayOfWeek = today.getDay();
  const diff = dayOfWeek === 0 ? -6 : 1 - dayOfWeek; // Adjust to Monday
  const monday = new Date(today);
  monday.setDate(today.getDate() + diff);

  const weekCommencing = monday.toLocaleDateString('en-GB', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });

  const docxInvoiceData = {
    invoiceNumber: `INV-${Date.now()}`,
    date: new Date().toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    }),
    weekCommencing,
    items: docxItems,
  };

  return {
    csvData,
    invoiceData,
    docxInvoiceData,
  };
}
