// Helper function to add ordinal suffix to day
export function getOrdinalSuffix(day: number): string {
    if (day > 3 && day < 21) return 'th';
    switch (day % 10) {
        case 1: return 'st';
        case 2: return 'nd';
        case 3: return 'rd';
        default: return 'th';
    }
}

// Helper function to format date with ordinal suffix (includes year)
export function formatDateWithOrdinal(date: Date): string {
    const day = date.getDate();
    const month = date.toLocaleDateString('en-GB', { month: 'long' });
    const year = date.getFullYear();
    return `${day}${getOrdinalSuffix(day)} ${month} ${year}`;
}

// Helper function to get the most recent Monday
export function getMostRecentMonday(): string {
    const today = new Date();
    const dayOfWeek = today.getDay(); // 0 = Sunday, 1 = Monday, etc.
    const daysToSubtract = dayOfWeek === 0 ? 6 : dayOfWeek - 1; // If Sunday, go back 6 days; otherwise, go back to Monday

    const monday = new Date(today);
    monday.setDate(today.getDate() - daysToSubtract);

    // Format as "27th October" (no year for week commencing)
    const day = monday.getDate();
    const month = monday.toLocaleDateString('en-GB', { month: 'long' });

    return `${day}${getOrdinalSuffix(day)} ${month}`;
}
