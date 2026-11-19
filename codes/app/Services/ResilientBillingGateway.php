<?php

declare(strict_types=1);

namespace App\Services;

use App\Contracts\BillingGateway;
use App\Exceptions\BillingUnavailable;
use App\Models\User;
use App\Support\Resilience\Retrier;
use Stripe\Exception\ApiConnectionException;
use Stripe\Exception\ApiErrorException;
use Stripe\Exception\RateLimitException;
use Throwable;

/** Wraps the Stripe gateway: transient failures retry with exponential backoff, then become BillingUnavailable. */
final readonly class ResilientBillingGateway implements BillingGateway
{
    public function __construct(
        private BillingGateway $inner,
        private Retrier $retrier,
    ) {
    }

    public function checkoutUrl(User $user, string $successUrl, string $cancelUrl): string
    {
        return $this->guard('stripe.checkout', fn (): string => $this->inner->checkoutUrl($user, $successUrl, $cancelUrl));
    }

    public function isCheckoutCompleteFor(User $user, string $sessionId): bool
    {
        return $this->guard('stripe.session', fn (): bool => $this->inner->isCheckoutCompleteFor($user, $sessionId));
    }

    public function portalUrl(User $user, string $returnUrl): string
    {
        return $this->guard('stripe.portal', fn (): string => $this->inner->portalUrl($user, $returnUrl));
    }

    /**
     * @template T
     *
     * @param  \Closure(): T  $call
     * @return T
     */
    private function guard(string $name, \Closure $call): mixed
    {
        try {
            return $this->retrier->run($call, $this->transient(...), $name);
        } catch (ApiErrorException $failure) {
            if ($this->transient($failure)) {
                throw BillingUnavailable::after($failure);
            }

            throw $failure;
        }
    }

    /** Network trouble, rate limits and Stripe-side 5xx are worth retrying; a rejected request is not. */
    private function transient(Throwable $failure): bool
    {
        if ($failure instanceof ApiConnectionException || $failure instanceof RateLimitException) {
            return true;
        }

        return $failure instanceof ApiErrorException && ($failure->getHttpStatus() ?? 0) >= 500;
    }
}
