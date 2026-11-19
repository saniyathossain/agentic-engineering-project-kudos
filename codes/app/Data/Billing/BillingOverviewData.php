<?php

declare(strict_types=1);

namespace App\Data\Billing;

use App\Enums\Plan;

final readonly class BillingOverviewData
{
    public function __construct(
        public Plan $plan,
        public int $spacesUsed,
        public ?int $spacesMax,
        public ?int $testimonialsPerSpaceMax,
        public string $subscriptionStatus,
        public bool $canManageBilling,
        public bool $billingConfigured,
    ) {
    }

    /** @return array<string, mixed> */
    public function toArray(): array
    {
        return [
            'plan' => ['value' => $this->plan->value, 'label' => $this->plan->label()],
            'spaces_used' => $this->spacesUsed,
            'spaces_max' => $this->spacesMax,
            'testimonials_per_space_max' => $this->testimonialsPerSpaceMax,
            'subscription_status' => $this->subscriptionStatus,
            'can_manage_billing' => $this->canManageBilling,
            'billing_configured' => $this->billingConfigured,
        ];
    }
}
