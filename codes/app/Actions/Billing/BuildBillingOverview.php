<?php

declare(strict_types=1);

namespace App\Actions\Billing;

use App\Data\Billing\BillingOverviewData;
use App\Enums\Plan;
use App\Models\User;
use App\Services\PlanResolver;

final readonly class BuildBillingOverview
{
    public function __construct(private PlanResolver $plans)
    {
    }

    public function handle(User $user): BillingOverviewData
    {
        $plan = $this->plans->for($user);
        $subscription = $user->subscription(PlanResolver::SUBSCRIPTION_TYPE);

        return new BillingOverviewData(
            plan: $plan,
            spacesUsed: $user->spaces()->count(),
            spacesMax: $plan->maxSpaces(),
            testimonialsPerSpaceMax: $plan->maxTestimonialsPerSpace(),
            subscriptionStatus: $subscription === null ? 'none' : (string) $subscription->stripe_status,
            canManageBilling: $plan === Plan::Pro && $user->hasStripeId(),
            billingConfigured: (string) config('services.stripe.pro_price_id') !== '' && (string) config('cashier.secret') !== '',
        );
    }
}
