import { Chip } from '@/components/ui/chip';
import DatePicker from '@/components/ui/date-picker';
import { addDays, type DayKey, toDayKey } from '@/lib/dates';
import { t, type TranslationKey } from '@/lib/i18n';
import { router } from '@inertiajs/react';
import { CalendarRange } from 'lucide-react';

interface DateRangeFilterProps {
    spaceId: string;
    filter: string;
    from: DayKey | null;
    to: DayKey | null;
}

const PRESETS: ReadonlyArray<{ label: TranslationKey; days: number }> = [
    { label: 'inbox.range.last_7', days: 7 },
    { label: 'inbox.range.last_30', days: 30 },
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
        <div className="flex flex-wrap items-center gap-2" role="group" aria-label={t('inbox.range.label')}>
            <CalendarRange className="text-ink-3 size-4" strokeWidth={1.75} aria-hidden="true" />
            <DatePicker
                label={t('inbox.range.from')}
                placeholder={t('inbox.range.from')}
                value={from}
                max={to ?? undefined}
                onChange={(value) => apply({ from: value, to })}
            />
            <span className="text-ink-3 text-sm" aria-hidden="true">
                {t('inbox.range.to_separator')}
            </span>
            <DatePicker
                label={t('inbox.range.to')}
                placeholder={t('inbox.range.to')}
                value={to}
                min={from ?? undefined}
                onChange={(value) => apply({ from, to: value })}
            />
            <div className="flex flex-wrap gap-1.5">
                {PRESETS.map(({ label, days }) => (
                    <Chip key={label} asChild tone="outline">
                        <button type="button" onClick={() => apply({ from: toDayKey(addDays(today, -days)), to: toDayKey(today) })}>
                            {t(label)}
                        </button>
                    </Chip>
                ))}
            </div>
        </div>
    );
}
