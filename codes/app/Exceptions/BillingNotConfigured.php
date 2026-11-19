<?php

declare(strict_types=1);

namespace App\Exceptions;

use RuntimeException;

/** Stripe is not set up in this environment. The user gets a generic message; the missing setting is only logged. */
final class BillingNotConfigured extends RuntimeException
{
    public static function missing(string $setting): self
    {
        report(new self("{$setting} is not configured."));

        return new self(__('billing.not_configured'));
    }
}
