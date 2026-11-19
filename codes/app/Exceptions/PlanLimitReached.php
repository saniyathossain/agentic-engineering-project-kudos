<?php

declare(strict_types=1);

namespace App\Exceptions;

use RuntimeException;

final class PlanLimitReached extends RuntimeException
{
    public static function spaces(): self
    {
        return new self(__('limits.spaces'));
    }

    public static function testimonials(): self
    {
        return new self(__('limits.testimonials'));
    }
}
