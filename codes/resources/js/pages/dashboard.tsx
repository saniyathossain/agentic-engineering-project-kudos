import RangeToggle from '@/components/dashboard/range-toggle';
import StatCard from '@/components/dashboard/stat-card';
import SubmissionsChart from '@/components/dashboard/submissions-chart';
import UpgradeBanner from '@/components/dashboard/upgrade-banner';
import PageHeader from '@/components/page-header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import AppLayout from '@/layouts/app-layout';
import { type BreadcrumbItem, type DashboardRange, type DashboardStats } from '@/types';
import { Head, router } from '@inertiajs/react';
import { CreditCard, LayoutGrid, MessageSquareQuote, Users } from 'lucide-react';
import { type CSSProperties } from 'react';

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
            <div className="mx-auto flex w-full max-w-6xl flex-1 flex-col gap-6 p-4 sm:p-6">
                <PageHeader title="Overview" description="How your testimonials are coming in." />
                {stats.show_upgrade_banner && <UpgradeBanner />}
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                    <StatCard index={1} icon={LayoutGrid} label="Spaces" value={stats.total_spaces} />
                    <StatCard index={2} icon={MessageSquareQuote} label="Testimonials" value={stats.total_testimonials} />
                    <StatCard index={3} icon={Users} label="Unique respondents" value={stats.unique_respondents} />
                    <StatCard
                        index={4}
                        icon={CreditCard}
                        label="Plan"
                        value={stats.plan.label}
                        hint={`Spaces ${limitLabel(stats.usage.spaces_used, stats.usage.max_spaces)} · ${stats.usage.max_testimonials_per_space ?? 'Unlimited'} testimonials per space`}
                    />
                </div>
                <Card className="rise" style={{ '--i': 5 } as CSSProperties}>
                    <CardHeader className="flex flex-row flex-wrap items-center justify-between gap-4">
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
