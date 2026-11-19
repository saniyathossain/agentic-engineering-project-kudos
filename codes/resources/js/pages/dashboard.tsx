import RangeToggle from '@/components/dashboard/range-toggle';
import StatCard from '@/components/dashboard/stat-card';
import SubmissionsChart from '@/components/dashboard/submissions-chart';
import UpgradeBanner from '@/components/dashboard/upgrade-banner';
import PageHeader from '@/components/page-header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import AppLayout from '@/layouts/app-layout';
import { t } from '@/lib/i18n';
import { type BreadcrumbItem, type DashboardRange, type DashboardStats } from '@/types';
import { Head, router } from '@inertiajs/react';
import { CreditCard, LayoutGrid, MessageSquareQuote, Users } from 'lucide-react';
import { type CSSProperties, useState } from 'react';

interface DashboardProps {
    stats: DashboardStats;
}

const limitLabel = (used: number, max: number | null): string => t('dashboard.limit', { used, max: max ?? t('dashboard.unlimited') });

export default function Dashboard({ stats }: DashboardProps) {
    const breadcrumbs: BreadcrumbItem[] = [{ title: t('dashboard.breadcrumb'), href: '/dashboard' }];
    const [loading, setLoading] = useState(false);
    const changeRange = (range: DashboardRange) =>
        router.get(
            '/dashboard',
            { range },
            {
                only: ['stats'],
                preserveState: true,
                preserveScroll: true,
                replace: true,
                onStart: () => setLoading(true),
                onFinish: () => setLoading(false),
            },
        );

    return (
        <AppLayout breadcrumbs={breadcrumbs}>
            <Head title={t('dashboard.breadcrumb')} />
            <div className="mx-auto flex w-full max-w-6xl flex-1 flex-col gap-6 p-4 sm:p-6">
                <PageHeader title={t('dashboard.title')} description={t('dashboard.description')} />
                {stats.show_upgrade_banner && <UpgradeBanner />}
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                    <StatCard index={1} icon={LayoutGrid} label={t('dashboard.stat.spaces')} value={stats.total_spaces} />
                    <StatCard index={2} icon={MessageSquareQuote} label={t('dashboard.stat.testimonials')} value={stats.total_testimonials} />
                    <StatCard index={3} icon={Users} label={t('dashboard.stat.respondents')} value={stats.unique_respondents} />
                    <StatCard
                        index={4}
                        icon={CreditCard}
                        label={t('dashboard.stat.plan')}
                        value={stats.plan.label}
                        hint={t('dashboard.stat.plan_hint', {
                            spaces: limitLabel(stats.usage.spaces_used, stats.usage.max_spaces),
                            testimonials: stats.usage.max_testimonials_per_space ?? t('dashboard.unlimited_cap'),
                        })}
                    />
                </div>
                <Card className="rise" style={{ '--i': 5 } as CSSProperties}>
                    <CardHeader className="flex flex-row flex-wrap items-center justify-between gap-4">
                        <CardTitle>{t('dashboard.chart.title', { count: stats.collected_in_range, days: stats.range })}</CardTitle>
                        <RangeToggle value={stats.range} onChange={changeRange} />
                    </CardHeader>
                    <CardContent>{loading ? <Skeleton className="h-64 w-full" /> : <SubmissionsChart series={stats.series} />}</CardContent>
                </Card>
            </div>
        </AppLayout>
    );
}
