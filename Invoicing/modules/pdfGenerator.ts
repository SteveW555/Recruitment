import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';
import type { InvoiceData } from '../types';

export function generateInvoicePDF(data: InvoiceData): Blob {
  const doc = new jsPDF();

  // Header
  doc.setFontSize(20);
  doc.text('INVOICE', 105, 20, { align: 'center' });

  // Invoice details
  doc.setFontSize(10);
  doc.text(`Invoice #: ${data.invoiceNumber}`, 20, 40);
  doc.text(`Date: ${data.date}`, 20, 46);
  doc.text(`Client: ${data.clientName}`, 20, 52);

  // Items table
  const tableData = data.items.map(item => [
    item.description,
    item.quantity.toString(),
    `$${item.unitPrice.toFixed(2)}`,
    `$${item.total.toFixed(2)}`,
  ]);

  autoTable(doc, {
    startY: 60,
    head: [['Description', 'Quantity', 'Unit Price', 'Total']],
    body: tableData,
    theme: 'striped',
    headStyles: { fillColor: [52, 152, 219] },
  });

  // Totals
  const finalY = (doc as any).lastAutoTable.finalY || 60;
  doc.text(`Subtotal: $${data.subtotal.toFixed(2)}`, 150, finalY + 10);
  doc.text(`Tax: $${data.tax.toFixed(2)}`, 150, finalY + 16);
  doc.setFontSize(12);
  doc.text(`Total: $${data.total.toFixed(2)}`, 150, finalY + 24);

  return doc.output('blob');
}
