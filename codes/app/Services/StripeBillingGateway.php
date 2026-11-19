<?php

declare(strict_types=1);

namespace App\Services;

use App\Contracts\BillingGateway;
use App\Exceptions\BillingNotConfigured;
use App\Models\User;
use Laravel\Cashier\Cashier;
use Stripe\Exception\ApiErrorException;

/**
 * Talks to Stripe. Every call that creates something carries an idempotency key, so the retries wrapped around
 * it (see ResilientBillingGateway) can never create a second customer or a second checkout session.
 */
final class StripeBillingGateway implements BillingGateway
{
    /** A checkout idempotency key is valid for this many seconds, so a double click reuses one session. */
    private const CHECKOUT_WINDOW_SECONDS = 300;

    public function checkoutUrl(User $user, string $successUrl, string $cancelUrl): string
    {
        $priceId = (string) config('services.stripe.pro_price_id');
        if ($priceId === '') {
            throw BillingNotConfigured::missing('STRIPE_PRO_PRICE_ID');
        }

        $session = Cashier::stripe()->checkout->sessions->create([
            'mode' => 'subscription',
            'customer' => $this->customerId($user),
            'client_reference_id' => (string) $user->id,
            'line_items' => [['price' => $priceId, 'quantity' => 1]],
            'success_url' => $successUrl.'?session_id={CHECKOUT_SESSION_ID}',
            'cancel_url' => $cancelUrl,
            // Cashier's webhook handler names the local subscription from this metadata
            'subscription_data' => ['metadata' => ['type' => PlanResolver::SUBSCRIPTION_TYPE, 'name' => PlanResolver::SUBSCRIPTION_TYPE]],
        ], ['idempotency_key' => sprintf('kudos-checkout-%d-%s-%d', $user->id, substr(sha1($priceId), 0, 8), intdiv(time(), self::CHECKOUT_WINDOW_SECONDS))]);

        return (string) $session->url;
    }

    public function isCheckoutCompleteFor(User $user, string $sessionId): bool
    {
        if ($user->stripe_id === null) {
            return false;
        }

        try {
            $session = Cashier::stripe()->checkout->sessions->retrieve($sessionId);
        } catch (ApiErrorException $e) {
            // an unknown or foreign session id is a "no"; connection and server failures must reach the retrier
            if (($e->getHttpStatus() ?? 0) >= 500 || $e instanceof \Stripe\Exception\ApiConnectionException || $e instanceof \Stripe\Exception\RateLimitException) {
                throw $e;
            }

            return false;
        }

        return $session->status === 'complete' && $session->customer === $user->stripe_id;
    }

    public function portalUrl(User $user, string $returnUrl): string
    {
        return $user->billingPortalUrl($returnUrl);
    }

    private function customerId(User $user): string
    {
        if ($user->hasStripeId()) {
            return (string) $user->stripe_id;
        }

        $customer = Cashier::stripe()->customers->create(
            ['name' => $user->name, 'email' => $user->email, 'metadata' => ['kudos_user_id' => (string) $user->id]],
            ['idempotency_key' => 'kudos-customer-'.$user->id],
        );
        $user->forceFill(['stripe_id' => $customer->id])->save();

        return (string) $customer->id;
    }
}
