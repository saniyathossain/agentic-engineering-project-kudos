import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { t } from '@/lib/i18n';
import { cn } from '@/lib/utils';
import { Check } from 'lucide-react';
import { type CSSProperties, type ReactNode } from 'react';

interface PlanCardProps {
    name: string;
    price: string;
    tagline: string;
    features: readonly string[];
    current: boolean;
    highlighted?: boolean;
    index: number;
    action?: ReactNode;
}

export default function PlanCard({ name, price, tagline, features, current, highlighted = false, index, action }: PlanCardProps) {
    return (
        <Card className={cn('rise lift flex flex-col gap-5 p-6', highlighted && 'pane-accent')} style={{ '--i': index } as CSSProperties}>
            <div className="space-y-1">
                <div className="flex items-center justify-between gap-2">
                    <h2 className="font-display text-2xl font-medium">{name}</h2>
                    {current && <Badge>{t('billing.current_plan')}</Badge>}
                </div>
                <p className="text-muted-foreground text-sm">{tagline}</p>
                <p className="font-display pt-2 text-4xl leading-none font-medium">{price}</p>
            </div>
            <ul className="space-y-2.5 text-sm">
                {features.map((feature) => (
                    <li key={feature} className="flex items-center gap-2.5">
                        <span className="icon-chip size-6 rounded-lg">
                            <Check className="size-3.5" strokeWidth={2.25} />
                        </span>
                        {feature}
                    </li>
                ))}
            </ul>
            {action && <div className="mt-auto pt-2">{action}</div>}
        </Card>
    );
}
