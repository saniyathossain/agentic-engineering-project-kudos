import { Button } from '@/components/ui/button';
import { Link, router } from '@inertiajs/react';
import { Sparkles, X } from 'lucide-react';

export default function UpgradeBanner() {
    const dismiss = () => router.post('/dashboard/banner/dismiss', {}, { preserveScroll: true, preserveState: true });

    return (
        <aside className="pane-accent rise flex items-center gap-4 rounded-2xl p-4" aria-label="Upgrade">
            <span className="icon-chip shrink-0">
                <Sparkles className="ico-sparkles-idle no-lift size-[18px]" strokeWidth={1.75} />
            </span>
            <p className="min-w-0 flex-1 text-sm">
                <span className="font-medium">Free plan: 1 space, 10 testimonials per space.</span>{' '}
                <Link href="/billing" className="text-primary font-medium underline underline-offset-4">
                    See Pro
                </Link>
            </p>
            <Button type="button" variant="ghost" size="icon" className="size-8 shrink-0" aria-label="Dismiss" onClick={dismiss}>
                <X strokeWidth={1.75} />
            </Button>
        </aside>
    );
}
