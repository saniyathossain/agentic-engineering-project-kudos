import { Chip } from '@/components/ui/chip';
import { t } from '@/lib/i18n';
import { type DashboardRange } from '@/types';

const RANGES: DashboardRange[] = [7, 30, 90];

interface RangeToggleProps {
    value: DashboardRange;
    onChange: (range: DashboardRange) => void;
}

export default function RangeToggle({ value, onChange }: RangeToggleProps) {
    return (
        <div className="flex gap-1.5" role="group" aria-label={t('dashboard.range.label')}>
            {RANGES.map((range) => (
                <Chip key={range} asChild selected={range === value} tone="outline" className="px-3 py-1.5 text-sm">
                    <button type="button" aria-pressed={range === value} onClick={() => onChange(range)}>
                        {t('dashboard.range.days', { days: range })}
                    </button>
                </Chip>
            ))}
        </div>
    );
}
