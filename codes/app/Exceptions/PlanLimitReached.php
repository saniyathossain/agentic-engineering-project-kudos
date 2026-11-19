<?php

declare(strict_types=1);

namespace App\Exceptions;

use RuntimeException;

final class PlanLimitReached extends RuntimeException
{
    public static function spaces(): self
    {
        return new self('Your Free plan includes 1 space. Upgrade to Pro to create more.');
    }

    public static function testimonials(): self
    {
        return new self('This space is not accepting testimonials right now.');
    }
}
