/** Calendar-day helpers. Days travel as `YYYY-MM-DD` strings, never as timestamps, so no timezone shifts them. */

export type DayKey = string;

const pad = (n: number): string => String(n).padStart(2, '0');

export const toDayKey = (date: Date): DayKey => `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;

export const fromDayKey = (key: DayKey): Date => {
    const [year, month, day] = key.split('-').map(Number);

    return new Date(year, month - 1, day);
};

export const addDays = (date: Date, amount: number): Date => new Date(date.getFullYear(), date.getMonth(), date.getDate() + amount);

export const startOfMonth = (date: Date): Date => new Date(date.getFullYear(), date.getMonth(), 1);

export const addMonths = (date: Date, amount: number): Date => new Date(date.getFullYear(), date.getMonth() + amount, 1);

/** The six-week grid (Sunday first) that contains the month of `view`. */
export const monthGrid = (view: Date): Date[] => {
    const first = startOfMonth(view);
    const gridStart = addDays(first, -first.getDay());

    return Array.from({ length: 42 }, (_, index) => addDays(gridStart, index));
};

export const formatDay = (key: DayKey, options: Intl.DateTimeFormatOptions = { month: 'short', day: 'numeric', year: 'numeric' }): string =>
    new Intl.DateTimeFormat(undefined, options).format(fromDayKey(key));

export const formatTimestamp = (iso: string): string =>
    new Intl.DateTimeFormat(undefined, { month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit' }).format(new Date(iso));
