import { Card } from '@/components/ui/card';
import { type LucideIcon } from 'lucide-react';
import { type CSSProperties } from 'react';

interface StatCardProps {
    label: string;
    value: string | number;
    hint?: string;
    icon: LucideIcon;
    index?: number;
}

export default function StatCard({ label, value, hint, icon: Icon, index = 0 }: StatCardProps) {
    return (
        <Card className="rise flex flex-col gap-3 p-5" style={{ '--i': index } as CSSProperties}>
            <div className="flex items-center justify-between">
                <span className="text-muted-foreground text-sm">{label}</span>
                <span className="icon-chip">
                    <Icon className="size-[18px]" strokeWidth={1.75} />
                </span>
            </div>
            <p className="font-display text-4xl leading-none font-medium tabular-nums">{value}</p>
            {hint && <p className="text-muted-foreground text-xs leading-relaxed">{hint}</p>}
        </Card>
    );
}
