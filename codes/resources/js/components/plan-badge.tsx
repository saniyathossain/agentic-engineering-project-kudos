import { Chip } from '@/components/ui/chip';
import { t } from '@/lib/i18n';
import { type SharedData } from '@/types';
import { Link, usePage } from '@inertiajs/react';
import { Sparkles } from 'lucide-react';

export default function PlanBadge() {
    const { plan } = usePage<SharedData>().props;

    if (plan === null) {
        return null;
    }

    return (
        <Link href="/billing" aria-label={t('layout.plan_badge', { plan: plan.label })}>
            <Chip tone={plan.value === 'pro' ? 'accent' : 'neutral'} interactive>
                {plan.value === 'pro' && <Sparkles className="ico-sparkles-idle size-3" strokeWidth={1.75} />}
                {plan.label}
            </Chip>
        </Link>
    );
}
