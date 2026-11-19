import { useSidebar } from '@/components/ui/sidebar';
import { t } from '@/lib/i18n';
import { type SharedData } from '@/types';
import { Link, usePage } from '@inertiajs/react';
import { ArrowRight, Sparkles } from 'lucide-react';

/** A quiet nudge for the Free plan; hidden on Pro and when the sidebar is collapsed to icons. */
export function SidebarUpgradeCard() {
    const { plan } = usePage<SharedData>().props;
    const { state } = useSidebar();

    if (plan === null || plan.value === 'pro' || state === 'collapsed') {
        return null;
    }

    return (
        <Link href="/billing" className="group/upgrade lift pane-accent flex flex-col gap-2 rounded-2xl p-3.5 text-sm">
            <span className="icon-chip size-8 rounded-lg">
                <Sparkles className="ico-sparkles-idle size-4" strokeWidth={1.75} />
            </span>
            <span className="font-display text-[0.95rem] leading-tight font-medium">{t('nav.upgrade.title')}</span>
            <span className="text-muted-foreground text-[0.8rem] leading-snug">{t('nav.upgrade.body')}</span>
            <span className="text-primary mt-0.5 inline-flex items-center gap-1 text-[0.8rem] font-medium">
                {t('nav.upgrade.cta')}
                <ArrowRight className="ico-right size-3.5" strokeWidth={1.75} />
            </span>
        </Link>
    );
}
