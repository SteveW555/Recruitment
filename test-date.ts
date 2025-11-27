// Test the getMostRecentMonday function
function getMostRecentMonday(): string {
    const today = new Date();
    const dayOfWeek = today.getDay(); // 0 = Sunday, 1 = Monday, etc.
    const daysToSubtract = dayOfWeek === 0 ? 6 : dayOfWeek - 1; // If Sunday, go back 6 days; otherwise, go back to Monday

    const monday = new Date(today);
    monday.setDate(today.getDate() - daysToSubtract);

    // Format as "27th October"
    const day = monday.getDate();
    const month = monday.toLocaleDateString('en-GB', { month: 'long' });

    // Add ordinal suffix
    const suffix = (day: number) => {
        if (day > 3 && day < 21) return 'th';
        switch (day % 10) {
            case 1: return 'st';
            case 2: return 'nd';
            case 3: return 'rd';
            default: return 'th';
        }
    };

    return `${day}${suffix(day)} ${month}`;
}

const result = getMostRecentMonday();
console.log(`Today is: ${new Date().toLocaleDateString('en-GB', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}`);
console.log(`Most recent Monday: ${result}`);
console.log(`\nFull text: "Hours for week commencing Monday ${result}:"`);
