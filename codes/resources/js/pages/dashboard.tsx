import RangeToggle from '@/components/dashboard/range-toggle';
import StatCard from '@/components/dashboard/stat-card';
import SubmissionsChart from '@/components/dashboard/submissions-chart';
import UpgradeBanner from '@/components/dashboard/upgrade-banner';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import AppLayout from '@/layouts/app-layout';
import { type BreadcrumbItem, type DashboardRange, type DashboardStats } from '@/types';
import { Head, router } from '@inertiajs/react';

const breadcrumbs: BreadcrumbItem[] = [
    {
        title: 'Dashboard',
        href: '/dashboard',
    },
];

interface DashboardProps {
    stats: DashboardStats;
}

const limitLabel = (used: number, max: number | null): string => `${used} / ${max ?? 'unlimited'}`;

export default function Dashboard({ stats }: DashboardProps) {
    const changeRange = (range: DashboardRange) =>
        router.get('/dashboard', { range }, { only: ['stats'], preserveState: true, preserveScroll: true, replace: true });

    return (
        <AppLayout breadcrumbs={breadcrumbs}>
            <Head title="Dashboard" />
            <div className="flex h-full flex-1 flex-col gap-4 rounded-xl p-4">
                {stats.show_upgrade_banner && <UpgradeBanner />}
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                    <StatCard label="Spaces" value={stats.total_spaces} />
                    <StatCard label="Testimonials" value={stats.total_testimonials} />
                    <StatCard label="Unique respondents" value={stats.unique_respondents} />
                    <StatCard
                        label="Plan"
                        value={stats.plan.label}
                        hint={`Spaces ${limitLabel(stats.usage.spaces_used, stats.usage.max_spaces)} · ${stats.usage.max_testimonials_per_space ?? 'Unlimited'} testimonials per space`}
                    />
                </div>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between gap-4">
                        <CardTitle>
                            {stats.collected_in_range} collected in the last {stats.range} days
                        </CardTitle>
                        <RangeToggle value={stats.range} onChange={changeRange} />
                    </CardHeader>
                    <CardContent>
                        <SubmissionsChart series={stats.series} />
                    </CardContent>
                </Card>
            </div>
        </AppLayout>
    );
}
