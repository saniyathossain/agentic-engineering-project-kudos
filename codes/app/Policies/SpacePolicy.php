<?php

declare(strict_types=1);

namespace App\Policies;

use App\Models\Space;
use App\Models\User;

final class SpacePolicy
{
    public function manage(User $user, Space $space): bool
    {
        return $space->user_id === $user->id;
    }
}
