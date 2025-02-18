/** @odoo-module */

export function formatAmount(number) {
    const abbreviations = ['', 'K', 'M', 'B'];
    
    let index = Math.floor(Math.log10(Math.abs(number)) / 3);
    index = Math.min(abbreviations.length - 1, index);
    let formattedNumber = (number / Math.pow(10, index * 3)).toFixed(2);
    return formattedNumber + abbreviations[index];
}

export function getDateInterval(interval) {
    const now = new Date();
    let start, end;

    switch (interval.toLowerCase()) {
        case 'last_week':
            start = new Date(now);
            start.setDate(now.getDate() - now.getDay() - 7);
            start.setHours(0, 0, 0, 0);

            end = new Date(start);
            end.setDate(start.getDate() + 6);
            end.setHours(23, 59, 59, 999);
            break;

        case 'this_week':
            start = new Date(now);
            start.setDate(now.getDate() - now.getDay());
            start.setHours(0, 0, 0, 0);

            end = new Date(now);
            end.setHours(23, 59, 59, 999);
            break;

        case 'last_month':
            start = new Date(now.getFullYear(), now.getMonth() - 1, 1);
            end = new Date(now.getFullYear(), now.getMonth(), 0);
            end.setHours(23, 59, 59, 999);
            break;

        case 'last_year':
            start = new Date(now.getFullYear() - 1, 0, 1);
            end = new Date(now.getFullYear() - 1, 11, 31);
            end.setHours(23, 59, 59, 999);
            break;

        default:
            throw new Error('Invalid interval specified');
    }

    function formatDateLocal(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    return {
        start: formatDateLocal(start),
        end: formatDateLocal(end)
    };
}