import {
    Document,
    Packer,
    Paragraph,
    Table,
    TableRow,
    TableCell,
    WidthType,
    TextRun,
    AlignmentType,
    BorderStyle,
    convertInchesToTwip,
    HeightRule,
    VerticalAlign,
} from "docx";
import type { DocxInvoiceData } from '../types';

// Hardcoded test data (full 20-employee list)
const HARDCODED_DATA: DocxInvoiceData = {
    invoiceNumber: "10010097",
    date: "3rd November 2025",
    weekCommencing: "Monday 27th October",
    items: [
        { name: "Alison Coulter", hours: 42.5, rate: 19.01, basePay: 807.93, bonus: 16.80, holidayPay: 0 },
        { name: "Andreia Abrue", hours: 20.5, rate: 19.01, basePay: 389.71, bonus: 11.28, holidayPay: 0 },
        { name: "Caroline Wilson", hours: 28, rate: 20.25, basePay: 567.00, bonus: 15.42, holidayPay: 0 },
        { name: "Chloe Zvordadza", hours: 17.75, rate: 20.25, basePay: 359.44, bonus: 0, holidayPay: 0 },
        { name: "Ed Spencer", hours: 15, rate: 21.93, basePay: 328.95, bonus: 14.41, holidayPay: 0 },
        { name: "Eden Constaninof", hours: 17.75, rate: 19.01, basePay: 337.43, bonus: 4.91, holidayPay: 0 },
        { name: "Harry Atkinson", hours: 35, rate: 21.71, basePay: 759.85, bonus: 19.42, holidayPay: 0 },
        { name: "Jamal Walker", hours: 28, rate: 20.25, basePay: 567.00, bonus: 7.86, holidayPay: 0 },
        { name: "John Vanek", hours: 10, rate: 19.01, basePay: 190.10, bonus: 3.94, holidayPay: 0 },
        { name: "Katie Stainer", hours: 14, rate: 20.25, basePay: 283.50, bonus: 4.91, holidayPay: 0 },
        { name: "Leighton Mees", hours: 28.75, rate: 19.01, basePay: 546.54, bonus: 4.91, holidayPay: 0 },
        { name: "Matt Savill", hours: 21, rate: 19.01, basePay: 399.21, bonus: 13.83, holidayPay: 0 },
        { name: "Melissa Parish", hours: 23.5, rate: 20.25, basePay: 475.88, bonus: 9.41, holidayPay: 0 },
        { name: "Michael Barkes", hours: 25, rate: 20.47, basePay: 511.75, bonus: 1.64, holidayPay: 0 },
        { name: "Michaela Sawyer", hours: 27, rate: 19.01, basePay: 513.27, bonus: 20.55, holidayPay: 0 },
        { name: "Natalie Bennett", hours: 23.25, rate: 21.71, basePay: 504.76, bonus: 12.12, holidayPay: 0 },
        { name: "Natalie Collier", hours: 39, rate: 20.47, basePay: 0, bonus: 0, holidayPay: 0 },
        { name: "Shazia Begum", hours: 18.75, rate: 21.93, basePay: 411.19, bonus: 9.82, holidayPay: 0 },
        { name: "Steve Kemp", hours: 31, rate: 20.47, basePay: 634.57, bonus: 11.78, holidayPay: 0 },
        { name: "Zak Nicholson", hours: 35.25, rate: 19.01, basePay: 670.10, bonus: 20.64, holidayPay: 0 },
    ]
};

export const generateInvoiceDocx = async (data?: DocxInvoiceData): Promise<Blob> => {
    const invoiceData = data || HARDCODED_DATA;

    // --- Calculations ---
    const subTotal = invoiceData.items.reduce((acc, item) => acc + item.basePay + item.bonus + item.holidayPay, 0);
    const vatRate = 0.20;
    const vatAmount = subTotal * vatRate;
    const totalDue = subTotal + vatAmount;

    const fmt = (num: number) => num.toLocaleString('en-GB', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

    // --- Helper for Invisible Borders ---
    const noBorders = {
        top: { style: BorderStyle.NONE, size: 0, color: "auto" },
        bottom: { style: BorderStyle.NONE, size: 0, color: "auto" },
        left: { style: BorderStyle.NONE, size: 0, color: "auto" },
        right: { style: BorderStyle.NONE, size: 0, color: "auto" },
        insideVertical: { style: BorderStyle.NONE, size: 0, color: "auto" },
        insideHorizontal: { style: BorderStyle.NONE, size: 0, color: "auto" },
    };

    // --- Document Definition ---
    const doc = new Document({
        styles: {
            default: {
                document: {
                    run: {
                        font: "Arial",
                        size: 20, // 10pt base size
                        color: "000000",
                    },
                    paragraph: {
                        spacing: { line: 240 }, // Standard line spacing
                    }
                },
            },
        },
        sections: [
            {
                properties: {
                    page: {
                        margin: {
                            top: convertInchesToTwip(1),
                            bottom: convertInchesToTwip(1),
                            left: convertInchesToTwip(1),
                            right: convertInchesToTwip(1),
                        },
                    },
                },
                children: [
                    // ==========================================
                    // HEADER SECTION (Address Left / Invoice Right)
                    // ==========================================
                    new Table({
                        width: { size: 100, type: WidthType.PERCENTAGE },
                        borders: noBorders,
                        rows: [
                            new TableRow({
                                children: [
                                    // Left Column: Address Block
                                    new TableCell({
                                        width: { size: 60, type: WidthType.PERCENTAGE },
                                        children: [
                                            new Paragraph({
                                                children: [
                                                    new TextRun({ text: "Accounts", bold: true }),
                                                    new TextRun({ text: "\nStrategic Communications Inc (UK) Limited" }),
                                                    new TextRun({ text: "\nSovereign House" }),
                                                    new TextRun({ text: "\n15 Towcester Road" }),
                                                    new TextRun({ text: "\nOld Stratford" }),
                                                    new TextRun({ text: "\nMilton Keynes" }),
                                                    new TextRun({ text: "\nBuckinghamshire" }),
                                                    new TextRun({ text: "\nMK19 6AN" }),
                                                ],
                                            }),
                                        ],
                                    }),
                                    // Right Column: Invoice Details
                                    new TableCell({
                                        width: { size: 40, type: WidthType.PERCENTAGE },
                                        verticalAlign: VerticalAlign.TOP,
                                        children: [
                                            new Paragraph({
                                                children: [
                                                    new TextRun({ text: "INVOICE", bold: true, size: 24 }), // Larger header
                                                    new TextRun({ text: `\n\nInvoice ref: ${invoiceData.invoiceNumber}` }),
                                                    new TextRun({ text: `\nDate: ${invoiceData.date}` }),
                                                ],
                                            }),
                                        ],
                                    }),
                                ],
                            }),
                        ],
                    }),

                    new Paragraph({ text: "\n" }),
                    new Paragraph({ text: "\n" }),

                    // ==========================================
                    // WEEK TITLE
                    // ==========================================
                    new Paragraph({
                        children: [
                            new TextRun({ text: `Hours for week commencing ${invoiceData.weekCommencing}:` })
                        ],
                    }),

                    new Paragraph({ text: "\n" }),

                    // ==========================================
                    // MAIN DATA TABLE
                    // ==========================================
                    new Table({
                        width: { size: 100, type: WidthType.PERCENTAGE },
                        borders: noBorders,
                        rows: invoiceData.items.flatMap((item) => {
                            const rows = [];

                            // Row 1: Name | Details | Cost
                            rows.push(
                                new TableRow({
                                    children: [
                                        new TableCell({
                                            width: { size: 35, type: WidthType.PERCENTAGE },
                                            children: [new Paragraph({ children: [new TextRun({ text: item.name })] })], // Not bold in target
                                        }),
                                        new TableCell({
                                            width: { size: 45, type: WidthType.PERCENTAGE },
                                            children: [new Paragraph({ text: `${item.hours} hours @ £${item.rate}ph` })],
                                        }),
                                        new TableCell({
                                            width: { size: 20, type: WidthType.PERCENTAGE },
                                            children: [new Paragraph({ text: `£${fmt(item.basePay)}`, alignment: AlignmentType.RIGHT })],
                                        }),
                                    ],
                                })
                            );

                            // Row 2: Bonus (Only add if bonus exists)
                            if (item.bonus > 0) {
                                rows.push(
                                    new TableRow({
                                        children: [
                                            new TableCell({
                                                children: [new Paragraph({ text: "Bonus" })],
                                            }),
                                            new TableCell({
                                                children: [],
                                            }),
                                            new TableCell({
                                                children: [new Paragraph({ text: `£${fmt(item.bonus)}`, alignment: AlignmentType.RIGHT })],
                                            }),
                                        ],
                                    })
                                );
                            }

                            // Row 3: Holiday Pay (Only add if holiday pay exists)
                            if (item.holidayPay > 0) {
                                rows.push(
                                    new TableRow({
                                        children: [
                                            new TableCell({
                                                children: [new Paragraph({ text: "Holiday Pay" })],
                                            }),
                                            new TableCell({
                                                children: [],
                                            }),
                                            new TableCell({
                                                children: [new Paragraph({ text: `£${fmt(item.holidayPay)}`, alignment: AlignmentType.RIGHT })],
                                            }),
                                        ],
                                    })
                                );
                            }

                            // Spacer Row for visual breathing room
                            rows.push(
                                new TableRow({
                                    height: { value: 100, rule: HeightRule.EXACT },
                                    children: [
                                        new TableCell({ children: [] }), new TableCell({ children: [] }), new TableCell({ children: [] })
                                    ]
                                })
                            );

                            return rows;
                        }),
                    }),

                    new Paragraph({ text: "\n" }),
                    new Paragraph({ text: "\n" }),

                    // ==========================================
                    // FOOTER / VAT SECTION
                    // ==========================================
                    new Table({
                        width: { size: 100, type: WidthType.PERCENTAGE },
                        borders: noBorders,
                        rows: [
                            new TableRow({
                                children: [
                                    // LEFT SIDE: The Grey/Bordered VAT Box
                                    new TableCell({
                                        width: { size: 40, type: WidthType.PERCENTAGE },
                                        children: [
                                            new Table({
                                                width: { size: 100, type: WidthType.PERCENTAGE },
                                                borders: {
                                                    top: { style: BorderStyle.SINGLE, size: 1 },
                                                    bottom: { style: BorderStyle.SINGLE, size: 1 },
                                                    left: { style: BorderStyle.SINGLE, size: 1 },
                                                    right: { style: BorderStyle.SINGLE, size: 1 },
                                                    insideVertical: { style: BorderStyle.SINGLE, size: 1 },
                                                },
                                                rows: [
                                                    // Header Row
                                                    new TableRow({
                                                        children: [
                                                            new TableCell({ shading: { fill: "D9D9D9" }, children: [new Paragraph({ text: "Vat rate" })] }),
                                                            new TableCell({ shading: { fill: "D9D9D9" }, children: [new Paragraph({ text: "Vat amount" })] }),
                                                            new TableCell({ shading: { fill: "D9D9D9" }, children: [new Paragraph({ text: "Total" })] }),
                                                        ]
                                                    }),
                                                    // Data Row
                                                    new TableRow({
                                                        children: [
                                                            new TableCell({ children: [new Paragraph({ text: "20%", alignment: AlignmentType.CENTER })] }),
                                                            new TableCell({ children: [new Paragraph({ text: `£${fmt(vatAmount)}`, alignment: AlignmentType.RIGHT })] }),
                                                            new TableCell({ children: [new Paragraph({ text: `£${fmt(subTotal)}`, alignment: AlignmentType.RIGHT })] }),
                                                        ]
                                                    })
                                                ]
                                            })
                                        ],
                                    }),

                                    // SPACER COLUMN
                                    new TableCell({ width: { size: 10, type: WidthType.PERCENTAGE }, children: [] }),

                                    // RIGHT SIDE: The Final Totals
                                    new TableCell({
                                        width: { size: 50, type: WidthType.PERCENTAGE },
                                        children: [
                                            new Table({
                                                width: { size: 100, type: WidthType.PERCENTAGE },
                                                borders: noBorders,
                                                rows: [
                                                    new TableRow({
                                                        children: [
                                                            new TableCell({ children: [new Paragraph({ text: "Total excluding VAT" })] }),
                                                            new TableCell({ children: [new Paragraph({ text: `£ ${fmt(subTotal)}`, alignment: AlignmentType.RIGHT })] }),
                                                        ]
                                                    }),
                                                    new TableRow({
                                                        children: [
                                                            new TableCell({ children: [new Paragraph({ text: "VAT" })] }),
                                                            new TableCell({ children: [new Paragraph({ text: `£ ${fmt(vatAmount)}`, alignment: AlignmentType.RIGHT })] }),
                                                        ]
                                                    }),
                                                    // Line separator before Total Due
                                                    new TableRow({
                                                        children: [
                                                            new TableCell({
                                                                columnSpan: 2,
                                                                borders: { bottom: { style: BorderStyle.SINGLE, size: 1 } },
                                                                children: []
                                                            })
                                                        ]
                                                    }),
                                                    new TableRow({
                                                        children: [
                                                            new TableCell({ children: [new Paragraph({ text: "Total Due" })] }),
                                                            new TableCell({ children: [new Paragraph({ text: `£${fmt(totalDue)}`, alignment: AlignmentType.RIGHT })] }),
                                                        ]
                                                    }),
                                                ]
                                            })
                                        ],
                                    }),
                                ],
                            }),
                        ],
                    }),

                    new Paragraph({ text: "\n" }),
                    new Paragraph({ text: "\n" }),

                    // ==========================================
                    // PAYMENT FOOTER
                    // ==========================================
                    new Paragraph({ text: "Payment required within 7 days" }),
                    new Paragraph({ text: "\n" }),

                    new Table({
                        width: { size: 50, type: WidthType.PERCENTAGE },
                        borders: noBorders,
                        rows: [
                            new TableRow({ children: [new TableCell({ children: [new Paragraph("Sort Code:")] }), new TableCell({ children: [new Paragraph("04-03-70")] })] }),
                            new TableRow({ children: [new TableCell({ children: [new Paragraph("Account No:")] }), new TableCell({ children: [new Paragraph("53974902")] })] }),
                            new TableRow({ children: [new TableCell({ children: [new Paragraph("Account Name:")] }), new TableCell({ children: [new Paragraph("Effective Recruitment Solutions Ltd")] })] }),
                        ]
                    }),

                    new Paragraph({ text: "\n\n" }),
                    new Paragraph({ text: "10152.68" }), // Unknown stray number from target

                    // ==========================================
                    // LEGAL FOOTER
                    // ==========================================
                    new Paragraph({
                        alignment: AlignmentType.CENTER,
                        children: [
                            new TextRun({ text: "Effective Recruitment Solutions Ltd, 33 Portland Square, Bristol, BS2 8RG", size: 16, color: "999999" }),
                            new TextRun({ text: "\nRegistered Office: 28 The Mall, London, N14 6LN | Company number 13751335", size: 16, color: "999999" })
                        ]
                    })
                ],
            },
        ],
    });

    return await Packer.toBlob(doc);
};