import { cn } from '@/lib/utils';
import { type DashboardRange } from '@/types';

const RANGES: DashboardRange[] = [7, 30, 90];

interface RangeToggleProps {
    value: DashboardRange;
    onChange: (range: DashboardRange) => void;
}

export default function RangeToggle({ value, onChange }: RangeToggleProps) {
    return (
        <div className="bg-muted inline-flex rounded-xl p-1" role="group" aria-label="Date range">
            {RANGES.map((range) => (
                <button
                    key={range}
                    type="button"
                    aria-pressed={range === value}
                    onClick={() => onChange(range)}
                    className={cn(
                        'rounded-lg px-3 py-1 text-sm font-medium transition-[background-color,color,box-shadow] duration-200',
                        range === value ? 'bg-card text-foreground shadow-(--sh-sm)' : 'text-muted-foreground hover:text-foreground',
                    )}
                >
                    {range} days
                </button>
            ))}
        </div>
    );
}
