import FlashMessage from '@/components/flash-message';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import AppLayout from '@/layouts/app-layout';
import { type BreadcrumbItem, type PlanInfo } from '@/types';
import { Head, router } from '@inertiajs/react';

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

const UNLIMITED = 'Unlimited';

const limit = (max: number | null): string => (max === null ? UNLIMITED : String(max));

export default function Show({ overview }: { overview: Overview }) {
    const isPro = overview.plan.value === 'pro';

    return (
        <AppLayout breadcrumbs={breadcrumbs}>
            <Head title="Billing" />
            <div className="flex max-w-3xl flex-col gap-4 p-4">
                <FlashMessage />
                <h1 className="text-2xl font-semibold">Billing</h1>

                <div className="grid gap-4 md:grid-cols-2">
                    <Card className={isPro ? undefined : 'border-primary'}>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                Free {!isPro && <Badge>Current plan</Badge>}
                            </CardTitle>
                            <CardDescription>$0 / month</CardDescription>
                        </CardHeader>
                        <CardContent className="text-sm">
                            <ul className="list-disc space-y-1 pl-5">
                                <li>1 space</li>
                                <li>10 testimonials per space</li>
                                <li>Embeddable wall</li>
                            </ul>
                        </CardContent>
                    </Card>

                    <Card className={isPro ? 'border-primary' : undefined}>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                Pro {isPro && <Badge>Current plan</Badge>}
                            </CardTitle>
                            <CardDescription>Everything unlimited</CardDescription>
                        </CardHeader>
                        <CardContent className="text-sm">
                            <ul className="list-disc space-y-1 pl-5">
                                <li>Unlimited spaces</li>
                                <li>Unlimited testimonials</li>
                                <li>Embeddable wall</li>
                            </ul>
                        </CardContent>
                        <CardFooter>
                            {isPro ? (
                                overview.can_manage_billing && (
                                    <Button variant="outline" onClick={() => router.post(route('billing.portal'))}>
                                        Manage billing
                                    </Button>
                                )
                            ) : (
                                <Button onClick={() => router.post(route('billing.checkout'))} disabled={!overview.billing_configured}>
                                    Upgrade to Pro
                                </Button>
                            )}
                        </CardFooter>
                    </Card>
                </div>

                {!overview.billing_configured && !isPro && <p className="text-muted-foreground text-sm">Stripe is not configured in this environment (set STRIPE_KEY, STRIPE_SECRET, STRIPE_PRO_PRICE_ID).</p>}

                <Card>
                    <CardHeader>
                        <CardTitle>Usage</CardTitle>
                        <CardDescription>Subscription status: {overview.subscription_status}</CardDescription>
                    </CardHeader>
                    <CardContent className="text-sm">
                        <p>
                            Spaces: {overview.spaces_used} / {limit(overview.spaces_max)}
                        </p>
                        <p>Testimonials per space: up to {limit(overview.testimonials_per_space_max)}</p>
                    </CardContent>
                </Card>
            </div>
        </AppLayout>
    );
}
