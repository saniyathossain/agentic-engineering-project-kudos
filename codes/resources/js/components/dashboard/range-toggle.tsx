import { Button } from '@/components/ui/button';
import { type DashboardRange } from '@/types';

const RANGES: DashboardRange[] = [7, 30, 90];

interface RangeToggleProps {
    value: DashboardRange;
    onChange: (range: DashboardRange) => void;
}

export default function RangeToggle({ value, onChange }: RangeToggleProps) {
    return (
        <div className="flex gap-1" role="group" aria-label="Date range">
            {RANGES.map((range) => (
                <Button
                    key={range}
                    type="button"
                    size="sm"
                    variant={range === value ? 'default' : 'outline'}
                    aria-pressed={range === value}
                    onClick={() => onChange(range)}
                >
                    {range}d
                </Button>
            ))}
        </div>
    );
}
