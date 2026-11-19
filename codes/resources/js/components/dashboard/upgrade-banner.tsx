import { Button } from '@/components/ui/button';
import { t } from '@/lib/i18n';
import { Link, router } from '@inertiajs/react';
import { Sparkles, X } from 'lucide-react';

export default function UpgradeBanner() {
    const dismiss = () => router.post('/dashboard/banner/dismiss', {}, { preserveScroll: true, preserveState: true });

    return (
        <aside className="pane-accent rise flex items-center gap-4 rounded-2xl p-4" aria-label={t('dashboard.upgrade.label')}>
            <span className="icon-chip shrink-0">
                <Sparkles className="ico-sparkles-idle no-lift size-[18px]" strokeWidth={1.75} />
            </span>
            <p className="min-w-0 flex-1 text-sm">
                <span className="font-medium">{t('dashboard.upgrade.message')}</span>{' '}
                <Link href="/billing" className="text-primary hover:text-foreground font-medium transition-colors">
                    {t('dashboard.upgrade.see_pro')}
                </Link>
            </p>
            <Button
                type="button"
                variant="ghost"
                size="icon"
                className="size-8 shrink-0"
                aria-label={t('dashboard.upgrade.dismiss')}
                onClick={dismiss}
            >
                <X strokeWidth={1.75} />
            </Button>
        </aside>
    );
}
