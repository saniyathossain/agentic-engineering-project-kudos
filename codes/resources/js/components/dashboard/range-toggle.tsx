import { Chip } from '@/components/ui/chip';
import { type DashboardRange } from '@/types';

const RANGES: DashboardRange[] = [7, 30, 90];

interface RangeToggleProps {
    value: DashboardRange;
    onChange: (range: DashboardRange) => void;
}

export default function RangeToggle({ value, onChange }: RangeToggleProps) {
    return (
        <div className="flex gap-1.5" role="group" aria-label="Date range">
            {RANGES.map((range) => (
                <Chip key={range} asChild selected={range === value} tone="outline" className="px-3 py-1.5 text-sm">
                    <button type="button" aria-pressed={range === value} onClick={() => onChange(range)}>
                        {range} days
                    </button>
                </Chip>
            ))}
        </div>
    );
}
