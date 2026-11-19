<?php

declare(strict_types=1);

namespace App\Services;

use App\Contracts\BillingGateway;
use App\Models\User;
use Laravel\Cashier\Cashier;
use RuntimeException;
use Stripe\Exception\ApiErrorException;

final class StripeBillingGateway implements BillingGateway
{
    public function checkoutUrl(User $user, string $successUrl, string $cancelUrl): string
    {
        $priceId = (string) config('services.stripe.pro_price_id');
        if ($priceId === '') {
            throw new RuntimeException('STRIPE_PRO_PRICE_ID is not configured.');
        }

        $checkout = $user
            ->newSubscription(PlanResolver::SUBSCRIPTION_TYPE, $priceId)
            ->checkout([
                'success_url' => $successUrl.'?session_id={CHECKOUT_SESSION_ID}',
                'cancel_url' => $cancelUrl,
            ]);

        return (string) $checkout->asStripeCheckoutSession()->url;
    }

    public function isCheckoutCompleteFor(User $user, string $sessionId): bool
    {
        if ($user->stripe_id === null) {
            return false;
        }

        try {
            $session = Cashier::stripe()->checkout->sessions->retrieve($sessionId);
        } catch (ApiErrorException) {
            return false;
        }

        return $session->status === 'complete' && $session->customer === $user->stripe_id;
    }

    public function portalUrl(User $user, string $returnUrl): string
    {
        return $user->billingPortalUrl($returnUrl);
    }
}
