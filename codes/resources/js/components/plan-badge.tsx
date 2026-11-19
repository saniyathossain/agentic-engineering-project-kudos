import { Badge } from '@/components/ui/badge';
import { type SharedData } from '@/types';
import { Link, usePage } from '@inertiajs/react';
import { Sparkles } from 'lucide-react';

export default function PlanBadge() {
    const { plan } = usePage<SharedData>().props;

    if (plan === null) {
        return null;
    }

    return (
        <Link href="/billing" aria-label={`${plan.label} plan, open billing`}>
            <Badge variant={plan.value === 'pro' ? 'default' : 'secondary'} className="gap-1">
                {plan.value === 'pro' && <Sparkles className="size-3" strokeWidth={1.75} />}
                {plan.label}
            </Badge>
        </Link>
    );
}
