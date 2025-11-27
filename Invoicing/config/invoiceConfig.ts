export const InvoiceConfig = {
    company: {
        name: 'Effective Recruitment Solutions Ltd',
        address: 'Effective Recruitment Solutions Ltd, 33 Portland Square, Bristol, BS2 8BG',
        registeredOffice: 'Registered Office: 28 The Mall, London, N14 6LN | Company number 13751335',
    },
    bank: {
        sortCode: '04-03-70',
        accountNo: '53974902',
        accountName: 'Effective Recruitment Solutions Ltd',
        paymentTerms: 'Payment required within 7 days',
    },
    layout: {
        font: 'Calibri',
        colors: {
            primary: '000000',
            secondary: '999999', // Grey text
            tableHeader: 'C9C9C9', // Grey background
        },
        margins: {
            top: 250,
            right: 1270,
            bottom: 500,
            left: 1080,
        },
        logo: {
            width: 368,
            height: 78,
        }
    },
    business: {
        vatRate: 0.20,
    }
};
