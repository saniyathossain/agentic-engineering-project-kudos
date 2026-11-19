<?php

declare(strict_types=1);

namespace App\Contracts;

use App\Models\User;

/** Seam over Stripe so billing flows are testable without network calls. */
interface BillingGateway
{
    /** Hosted checkout URL for the Pro plan; the user is returned to $successUrl / $cancelUrl. */
    public function checkoutUrl(User $user, string $successUrl, string $cancelUrl): string;

    /** True only when Stripe confirms the session is complete AND belongs to this user. */
    public function isCheckoutCompleteFor(User $user, string $sessionId): bool;

    public function portalUrl(User $user, string $returnUrl): string;
}
