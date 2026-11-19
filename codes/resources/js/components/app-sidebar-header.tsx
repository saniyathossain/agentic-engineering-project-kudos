import { Breadcrumbs } from '@/components/breadcrumbs';
import PlanBadge from '@/components/plan-badge';
import { Button } from '@/components/ui/button';
import { SidebarTrigger } from '@/components/ui/sidebar';
import { t } from '@/lib/i18n';
import { type BreadcrumbItem as BreadcrumbItemType } from '@/types';
import { Link } from '@inertiajs/react';
import { Plus } from 'lucide-react';

export function AppSidebarHeader({ breadcrumbs = [] }: { breadcrumbs?: BreadcrumbItemType[] }) {
    return (
        <header className="sticky top-0 z-20 px-3 pt-3 md:px-4">
            <div className="frost flex h-14 items-center justify-between gap-3 rounded-2xl px-3">
                <div className="flex min-w-0 items-center gap-2">
                    <SidebarTrigger className="size-9 rounded-xl" />
                    <span aria-hidden className="bg-border mx-1 hidden h-5 w-px sm:block" />
                    <Breadcrumbs breadcrumbs={breadcrumbs} />
                </div>
                <div className="flex shrink-0 items-center gap-2">
                    <PlanBadge />
                    <Button asChild size="sm" className="rounded-xl">
                        <Link href="/spaces/create" prefetch>
                            <Plus className="ico-plus size-4" strokeWidth={2} />
                            <span className="hidden md:inline">{t('nav.new_space')}</span>
                        </Link>
                    </Button>
                </div>
            </div>
        </header>
    );
}
