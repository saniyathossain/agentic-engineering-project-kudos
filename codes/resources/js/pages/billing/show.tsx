import PlanCard from '@/components/billing/plan-card';
import FlashMessage from '@/components/flash-message';
import PageHeader from '@/components/page-header';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import AppLayout from '@/layouts/app-layout';
import { t } from '@/lib/i18n';
import { type BreadcrumbItem, type PlanInfo } from '@/types';
import { Head, router } from '@inertiajs/react';
import { ExternalLink, Sparkles } from 'lucide-react';

interface Overview {
    plan: PlanInfo;
    spaces_used: number;
    spaces_max: number | null;
    testimonials_per_space_max: number | null;
    subscription_status: string;
    can_manage_billing: boolean;
    billing_configured: boolean;
}

const FREE_FEATURES = ['billing.free.feature_spaces', 'billing.free.feature_testimonials', 'billing.feature_wall'] as const;
const PRO_FEATURES = ['billing.pro.feature_spaces', 'billing.pro.feature_testimonials', 'billing.feature_wall'] as const;

const limit = (max: number | null): string => (max === null ? t('billing.usage.unlimited') : String(max));

export default function Show({ overview }: { overview: Overview }) {
    const breadcrumbs: BreadcrumbItem[] = [{ title: t('billing.title'), href: '/billing' }];
    const isPro = overview.plan.value === 'pro';

    const proAction = isPro ? (
        overview.can_manage_billing && (
            <Button variant="outline" onClick={() => router.post(route('billing.portal'))}>
                <ExternalLink strokeWidth={1.75} /> {t('billing.manage')}
            </Button>
        )
    ) : (
        <Button onClick={() => router.post(route('billing.checkout'))} disabled={!overview.billing_configured}>
            <Sparkles strokeWidth={1.75} className="ico-sparkles" /> {t('billing.upgrade')}
        </Button>
    );

    return (
        <AppLayout breadcrumbs={breadcrumbs}>
            <Head title={t('billing.title')} />
            <div className="mx-auto flex w-full max-w-4xl flex-col gap-6 p-4 sm:p-6">
                <FlashMessage />
                <PageHeader title={t('billing.title')} description={t('billing.description')} />

                <div className="grid gap-4 md:grid-cols-2">
                    <PlanCard
                        index={1}
                        name={t('billing.free.name')}
                        price={t('billing.free.price')}
                        tagline={t('billing.free.tagline')}
                        features={FREE_FEATURES.map((key) => t(key))}
                        current={!isPro}
                    />
                    <PlanCard
                        index={2}
                        name={t('billing.pro.name')}
                        price={t('billing.pro.price')}
                        tagline={t('billing.pro.tagline')}
                        features={PRO_FEATURES.map((key) => t(key))}
                        current={isPro}
                        highlighted
                        action={proAction}
                    />
                </div>

                {!overview.billing_configured && !isPro && <p className="text-muted-foreground text-sm">{t('billing.stripe_missing')}</p>}

                <Card className="rise p-5" style={{ '--i': 3 } as React.CSSProperties}>
                    <h2 className="font-display text-xl font-medium">{t('billing.usage.title')}</h2>
                    <dl className="mt-3 grid gap-3 text-sm sm:grid-cols-3">
                        <div>
                            <dt className="text-muted-foreground">{t('billing.usage.spaces')}</dt>
                            <dd className="font-display text-2xl tabular-nums">
                                {overview.spaces_used} / {limit(overview.spaces_max)}
                            </dd>
                        </div>
                        <div>
                            <dt className="text-muted-foreground">{t('billing.usage.testimonials')}</dt>
                            <dd className="font-display text-2xl">{t('billing.usage.up_to', { max: limit(overview.testimonials_per_space_max) })}</dd>
                        </div>
                        <div>
                            <dt className="text-muted-foreground">{t('billing.usage.subscription')}</dt>
                            <dd className="font-display text-2xl capitalize">{overview.subscription_status}</dd>
                        </div>
                    </dl>
                </Card>
            </div>
        </AppLayout>
    );
}
