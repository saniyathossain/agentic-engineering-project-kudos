import PlanCard from '@/components/billing/plan-card';
import FlashMessage from '@/components/flash-message';
import PageHeader from '@/components/page-header';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import AppLayout from '@/layouts/app-layout';
import { type BreadcrumbItem, type PlanInfo } from '@/types';
import { Head, router } from '@inertiajs/react';
import { ExternalLink, Sparkles } from 'lucide-react';

const breadcrumbs: BreadcrumbItem[] = [{ title: 'Billing', href: '/billing' }];

interface Overview {
    plan: PlanInfo;
    spaces_used: number;
    spaces_max: number | null;
    testimonials_per_space_max: number | null;
    subscription_status: string;
    can_manage_billing: boolean;
    billing_configured: boolean;
}

const FREE_FEATURES = ['1 space', '10 testimonials per space', 'Embeddable wall of love'] as const;
const PRO_FEATURES = ['Unlimited spaces', 'Unlimited testimonials', 'Embeddable wall of love'] as const;

const limit = (max: number | null): string => (max === null ? 'Unlimited' : String(max));

export default function Show({ overview }: { overview: Overview }) {
    const isPro = overview.plan.value === 'pro';

    const proAction = isPro ? (
        overview.can_manage_billing && (
            <Button variant="outline" onClick={() => router.post(route('billing.portal'))}>
                <ExternalLink strokeWidth={1.75} /> Manage billing
            </Button>
        )
    ) : (
        <Button onClick={() => router.post(route('billing.checkout'))} disabled={!overview.billing_configured}>
            <Sparkles strokeWidth={1.75} /> Upgrade to Pro
        </Button>
    );

    return (
        <AppLayout breadcrumbs={breadcrumbs}>
            <Head title="Billing" />
            <div className="mx-auto flex w-full max-w-4xl flex-col gap-6 p-4 sm:p-6">
                <FlashMessage />
                <PageHeader title="Billing" description="Start free. Move to Pro when you need more room." />

                <div className="grid gap-4 md:grid-cols-2">
                    <PlanCard index={1} name="Free" price="$0" tagline="For trying it out" features={FREE_FEATURES} current={!isPro} />
                    <PlanCard
                        index={2}
                        name="Pro"
                        price="Paid"
                        tagline="For growing teams"
                        features={PRO_FEATURES}
                        current={isPro}
                        highlighted
                        action={proAction}
                    />
                </div>

                {!overview.billing_configured && !isPro && (
                    <p className="text-muted-foreground text-sm">
                        Stripe is not configured here. Set STRIPE_KEY, STRIPE_SECRET and STRIPE_PRO_PRICE_ID to enable upgrades.
                    </p>
                )}

                <Card className="rise p-5" style={{ '--i': 3 } as React.CSSProperties}>
                    <h2 className="font-display text-xl font-medium">Usage</h2>
                    <dl className="mt-3 grid gap-3 text-sm sm:grid-cols-3">
                        <div>
                            <dt className="text-muted-foreground">Spaces</dt>
                            <dd className="font-display text-2xl tabular-nums">
                                {overview.spaces_used} / {limit(overview.spaces_max)}
                            </dd>
                        </div>
                        <div>
                            <dt className="text-muted-foreground">Testimonials per space</dt>
                            <dd className="font-display text-2xl">Up to {limit(overview.testimonials_per_space_max)}</dd>
                        </div>
                        <div>
                            <dt className="text-muted-foreground">Subscription</dt>
                            <dd className="font-display text-2xl capitalize">{overview.subscription_status}</dd>
                        </div>
                    </dl>
                </Card>
            </div>
        </AppLayout>
    );
}
