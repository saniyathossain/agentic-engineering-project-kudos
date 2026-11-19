<?php

declare(strict_types=1);

namespace App\Policies;

use App\Models\Testimonial;
use App\Models\User;

final class TestimonialPolicy
{
    public function manage(User $user, Testimonial $testimonial): bool
    {
        return $testimonial->space?->user_id === $user->id;
    }
}
