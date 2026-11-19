<?php

declare(strict_types=1);

namespace App\Services;

use App\Enums\Plan;
use App\Models\Space;
use App\Models\User;

final class PlanResolver
{
    public const SUBSCRIPTION_TYPE = 'default';

    public function for(User $user): Plan
    {
        return $user->subscribed(self::SUBSCRIPTION_TYPE) ? Plan::Pro : Plan::Free;
    }

    public function canCreateSpace(User $user): bool
    {
        $max = $this->for($user)->maxSpaces();

        return $max === null || $user->spaces()->count() < $max;
    }

    public function acceptsTestimonials(Space $space): bool
    {
        if (! $space->is_accepting) {
            return false;
        }

        $owner = $space->owner;
        if ($owner === null) {
            return false;
        }

        $max = $this->for($owner)->maxTestimonialsPerSpace();

        return $max === null || $space->testimonials()->count() < $max;
    }
}
