import { Document, Packer, Paragraph, ImageRun, TextRun, AlignmentType, Table, TableCell, TableRow, WidthType, BorderStyle, Header, Footer, HeightRule, VerticalAlign } from 'docx';
import * as fs from 'fs';
import { formatAddressBlock } from './addressParser';
import { InvoiceConfig } from '../config/invoiceConfig';
import { formatDateWithOrdinal, getMostRecentMonday } from '../utils/dateUtils';
import { parseEmployeeData, EmployeeData } from '../services/employeeService';

export interface InvoiceData {
    logoBuffer: Uint8Array;  // Logo image as buffer (works in browser & Node)
    employees: EmployeeData[];  // Employee data array
    addressText: string;
    invoiceRef: string;
    invoiceDate: string;
}

export class InvoiceGenerator {
    constructor(private data: InvoiceData) { }

    // Build the invoice document (shared by both Buffer and Blob generation)
    private buildDocument(): Document {
        const addressLines = formatAddressBlock(this.data.addressText);
        const logoImage = this.data.logoBuffer;
        const employees = this.data.employees;
        const weekCommencing = getMostRecentMonday();
        const currentDate = formatDateWithOrdinal(new Date());

        const subTotal = employees.reduce((acc, emp) => acc + emp.total + emp.bonus, 0);
        const vatAmount = subTotal * InvoiceConfig.business.vatRate;
        const totalDue = subTotal + vatAmount;

        return new Document({
            sections: [{
                properties: {
                    page: {
                        margin: InvoiceConfig.layout.margins,
                    },
                },
                headers: {
                    default: this.createHeader(logoImage),
                },
                footers: {
                    default: this.createFooter(),
                },
                children: [
                    new Paragraph({ text: '' }),
                    new Paragraph({ text: '' }),
                    this.createAddressAndMetadataTable(addressLines, currentDate),
                    new Paragraph({ text: '' }),
                    new Paragraph({ text: '' }),
                    new Paragraph({
                        children: [
                            new TextRun({
                                text: `Hours for week commencing Monday ${weekCommencing}:`,
                                font: InvoiceConfig.layout.font,
                                size: 20,
                            }),
                        ],
                    }),
                    new Paragraph({ text: '' }),
                    new Paragraph({ text: '' }),
                    ...this.createEmployeeSection(employees),
                    new Paragraph({ text: '' }),
                    this.createVatTable(subTotal, vatAmount),
                    new Paragraph({ text: '' }),
                    new Paragraph({
                        text: '',
                        border: {
                            bottom: {
                                color: InvoiceConfig.layout.colors.secondary,
                                space: 1,
                                style: BorderStyle.SINGLE,
                                size: 6,
                            },
                        },
                    }),
                    new Paragraph({ text: '' }),
                    this.createTotalsTable(subTotal, vatAmount, totalDue),
                    new Paragraph({ text: '' }),
                    new Paragraph({ text: '' }),
                    new Paragraph({ text: '' }),
                    ...this.createPaymentDetails(),
                ],
            }],
        });
    }

    // Generate Buffer for Node.js/CLI
    public async generateBuffer(): Promise<Buffer> {
        const doc = this.buildDocument();
        return await Packer.toBuffer(doc);
    }

    // Generate Blob for browser
    public async generateBlob(): Promise<Blob> {
        const doc = this.buildDocument();
        return await Packer.toBlob(doc);
    }

    private createHeader(logoImage: Uint8Array): Header {
        return new Header({
            children: [
                new Paragraph({
                    alignment: AlignmentType.CENTER,
                    children: [
                        new ImageRun({
                            data: logoImage,
                            type: 'png',
                            transformation: InvoiceConfig.layout.logo,
                        }),
                    ],
                }),
            ],
        });
    }

    private createFooter(): Footer {
        return new Footer({
            children: [
                new Paragraph({
                    alignment: AlignmentType.CENTER,
                    children: [
                        new TextRun({
                            text: InvoiceConfig.company.address,
                            font: InvoiceConfig.layout.font,
                            size: 18,
                            color: InvoiceConfig.layout.colors.secondary,
                        }),
                    ],
                }),
                new Paragraph({
                    alignment: AlignmentType.CENTER,
                    children: [
                        new TextRun({
                            text: InvoiceConfig.company.registeredOffice,
                            font: InvoiceConfig.layout.font,
                            size: 18,
                            color: InvoiceConfig.layout.colors.secondary,
                        }),
                    ],
                }),
            ],
        });
    }

    private createAddressAndMetadataTable(addressLines: string[], currentDate: string): Table {
        return new Table({
            width: { size: 100, type: WidthType.PERCENTAGE },
            borders: {
                top: { style: BorderStyle.NONE },
                bottom: { style: BorderStyle.NONE },
                left: { style: BorderStyle.NONE },
                right: { style: BorderStyle.NONE },
                insideHorizontal: { style: BorderStyle.NONE },
                insideVertical: { style: BorderStyle.NONE },
            },
            rows: [
                new TableRow({
                    children: [
                        new TableCell({
                            width: { size: 65, type: WidthType.PERCENTAGE },
                            borders: { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE } },
                            children: [
                                new Paragraph({ text: '' }),
                                new Paragraph({
                                    children: [new TextRun({ text: 'Accounts', bold: false, font: InvoiceConfig.layout.font, size: 20 })],
                                }),
                                ...addressLines.map(line => new Paragraph({
                                    children: [new TextRun({ text: line, font: InvoiceConfig.layout.font, size: 20 })],
                                })),
                            ],
                        }),
                        new TableCell({
                            width: { size: 35, type: WidthType.PERCENTAGE },
                            borders: { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE } },
                            children: [
                                new Paragraph({
                                    alignment: AlignmentType.LEFT,
                                    children: [new TextRun({ text: 'INVOICE', bold: true, font: InvoiceConfig.layout.font, size: 24 })],
                                }),
                                new Paragraph({ text: '' }),
                                new Paragraph({
                                    alignment: AlignmentType.LEFT,
                                    children: [new TextRun({ text: `Invoice ref: ${this.data.invoiceRef}`, font: InvoiceConfig.layout.font, size: 20 })],
                                }),
                                new Paragraph({
                                    alignment: AlignmentType.LEFT,
                                    children: [new TextRun({ text: `Date: ${currentDate}`, font: InvoiceConfig.layout.font, size: 20 })],
                                }),
                            ],
                        }),
                    ],
                }),
            ],
        });
    }

    private createEmployeeSection(employees: EmployeeData[]): Paragraph[] {
        return employees.flatMap(emp => [
            new Paragraph({
                children: [
                    new TextRun({
                        text: `${emp.name}\t\t${emp.hours} hours @ £${emp.hourlyRate.toFixed(2)}ph`,
                        font: InvoiceConfig.layout.font,
                        size: 20,
                    }),
                    new TextRun({
                        text: `\t\t\t\t\t\t\t £${emp.total.toFixed(2)}`,
                        font: InvoiceConfig.layout.font,
                        size: 20,
                    }),
                ],
            }),
            new Paragraph({
                children: [
                    new TextRun({ text: 'Bonus', font: InvoiceConfig.layout.font, size: 20 }),
                    new TextRun({
                        text: `\t\t\t\t\t\t\t\t\t\t\t\t £${emp.bonus.toFixed(2)}`,
                        font: InvoiceConfig.layout.font,
                        size: 20,
                    }),
                ],
            }),
            new Paragraph({ text: '' }),
        ]);
    }

    private createVatTable(subTotal: number, vatAmount: number): Table {
        const headerCell = (text: string) => new TableCell({
            shading: { fill: InvoiceConfig.layout.colors.tableHeader },
            verticalAlign: VerticalAlign.CENTER,
            children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text, font: InvoiceConfig.layout.font, size: 20 })] })],
        });

        const dataCell = (text: string) => new TableCell({
            verticalAlign: VerticalAlign.CENTER,
            children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text, font: InvoiceConfig.layout.font, size: 20 })] })],
        });

        return new Table({
            width: { size: 40, type: WidthType.PERCENTAGE },
            borders: {
                top: { style: BorderStyle.SINGLE, size: 1 },
                bottom: { style: BorderStyle.SINGLE, size: 1 },
                left: { style: BorderStyle.SINGLE, size: 1 },
                right: { style: BorderStyle.SINGLE, size: 1 },
                insideHorizontal: { style: BorderStyle.SINGLE, size: 1 },
                insideVertical: { style: BorderStyle.SINGLE, size: 1 },
            },
            rows: [
                new TableRow({
                    height: { value: 320, rule: HeightRule.ATLEAST },
                    children: [headerCell('Vat rate'), headerCell('Vat amount'), headerCell('Total')],
                }),
                new TableRow({
                    height: { value: 320, rule: HeightRule.ATLEAST },
                    children: [
                        dataCell(`${(InvoiceConfig.business.vatRate * 100)}%`),
                        dataCell(`£${vatAmount.toFixed(2)}`),
                        dataCell(`£${subTotal.toFixed(2)}`),
                    ],
                }),
            ],
        });
    }

    private createTotalsTable(subTotal: number, vatAmount: number, totalDue: number): Table {
        const labelCell = (text: string, borderTop = false) => new TableCell({
            width: { size: 60, type: WidthType.PERCENTAGE },
            borders: {
                top: borderTop ? { style: BorderStyle.SINGLE, size: 1 } : { style: BorderStyle.NONE },
                bottom: borderTop ? { style: BorderStyle.SINGLE, size: 1 } : { style: BorderStyle.NONE },
                left: borderTop ? { style: BorderStyle.SINGLE, size: 1 } : { style: BorderStyle.NONE },
                right: { style: BorderStyle.NONE },
            },
            children: [new Paragraph({ children: [new TextRun({ text, font: InvoiceConfig.layout.font, size: 20 })] })],
        });

        const valueCell = (text: string, borderTop = false) => new TableCell({
            width: { size: 40, type: WidthType.PERCENTAGE },
            borders: {
                top: borderTop ? { style: BorderStyle.SINGLE, size: 1 } : { style: BorderStyle.NONE },
                bottom: borderTop ? { style: BorderStyle.SINGLE, size: 1 } : { style: BorderStyle.NONE },
                left: { style: BorderStyle.NONE },
                right: borderTop ? { style: BorderStyle.SINGLE, size: 1 } : { style: BorderStyle.NONE },
            },
            children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text, font: InvoiceConfig.layout.font, size: 20 })] })],
        });

        return new Table({
            width: { size: 40, type: WidthType.PERCENTAGE },
            alignment: AlignmentType.RIGHT,
            borders: { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE }, insideHorizontal: { style: BorderStyle.NONE }, insideVertical: { style: BorderStyle.NONE } },
            rows: [
                new TableRow({ children: [labelCell('Total excluding VAT'), valueCell(`£  ${subTotal.toFixed(2)}`)] }),
                new TableRow({ children: [labelCell('VAT'), valueCell(`£  ${vatAmount.toFixed(2)}`)] }),
                new TableRow({ children: [labelCell('Total Due', true), valueCell(`£${totalDue.toFixed(2)}`, true)] }),
            ],
        });
    }

    private createPaymentDetails(): Paragraph[] {
        return [
            new Paragraph({
                children: [new TextRun({ text: InvoiceConfig.bank.paymentTerms, font: InvoiceConfig.layout.font, size: 20 })],
            }),
            new Paragraph({ text: '' }),
            new Paragraph({
                children: [
                    new TextRun({ text: `Sort Code:\t\t${InvoiceConfig.bank.sortCode}`, font: InvoiceConfig.layout.font, size: 20, break: 1 }),
                    new TextRun({ text: `Account No:\t\t${InvoiceConfig.bank.accountNo}`, font: InvoiceConfig.layout.font, size: 20, break: 1 }),
                    new TextRun({ text: `Account Name:\t\t${InvoiceConfig.bank.accountName}`, font: InvoiceConfig.layout.font, size: 20, break: 1 }),
                ],
            }),
        ];
    }
}

// For CLI usage: generates invoice buffer and writes to file
export async function buildInvoice(data: InvoiceData, outputPath: string): Promise<void> {
    const generator = new InvoiceGenerator(data);
    const buffer = await generator.generateBuffer();
    fs.writeFileSync(outputPath, buffer);
    console.log(`Invoice generated: ${outputPath}`);
}

// For browser usage: generates invoice blob
export async function generateInvoiceBlob(data: InvoiceData): Promise<Blob> {
    const generator = new InvoiceGenerator(data);
    return await generator.generateBlob();
}
