import { Chip } from '@/components/ui/chip';
import DatePicker from '@/components/ui/date-picker';
import { addDays, type DayKey, toDayKey } from '@/lib/dates';
import { router } from '@inertiajs/react';
import { CalendarRange } from 'lucide-react';

interface DateRangeFilterProps {
    spaceId: string;
    filter: string;
    from: DayKey | null;
    to: DayKey | null;
}

const PRESETS: ReadonlyArray<{ label: string; days: number }> = [
    { label: 'Last 7 days', days: 7 },
    { label: 'Last 30 days', days: 30 },
];

export default function DateRangeFilter({ spaceId, filter, from, to }: DateRangeFilterProps) {
    const apply = (next: { from: DayKey | null; to: DayKey | null }) => {
        const query: Record<string, string> = { filter };
        if (next.from) {
            query.from = next.from;
        }
        if (next.to) {
            query.to = next.to;
        }
        router.get(route('spaces.show', spaceId), query, { preserveScroll: true, preserveState: true, replace: true });
    };

    const today = new Date();

    return (
        <div className="flex flex-wrap items-center gap-2" role="group" aria-label="Date range">
            <CalendarRange className="text-ink-3 size-4" strokeWidth={1.75} aria-hidden="true" />
            <DatePicker label="From" placeholder="From" value={from} max={to ?? undefined} onChange={(value) => apply({ from: value, to })} />
            <span className="text-ink-3 text-sm" aria-hidden="true">
                to
            </span>
            <DatePicker label="To" placeholder="To" value={to} min={from ?? undefined} onChange={(value) => apply({ from, to: value })} />
            <div className="flex flex-wrap gap-1.5">
                {PRESETS.map(({ label, days }) => (
                    <Chip key={label} asChild tone="outline">
                        <button type="button" onClick={() => apply({ from: toDayKey(addDays(today, -days)), to: toDayKey(today) })}>
                            {label}
                        </button>
                    </Chip>
                ))}
            </div>
        </div>
    );
}
