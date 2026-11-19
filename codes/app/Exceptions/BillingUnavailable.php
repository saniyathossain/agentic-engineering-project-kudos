<?php

declare(strict_types=1);

namespace App\Exceptions;

use RuntimeException;
use Throwable;

/** Stripe could not be reached (or kept failing) even after retries. Nothing was charged. */
final class BillingUnavailable extends RuntimeException
{
    public static function after(Throwable $previous): self
    {
        return new self(__('billing.unavailable'), 0, $previous);
    }
}
