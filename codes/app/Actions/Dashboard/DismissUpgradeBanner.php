<?php

declare(strict_types=1);

namespace App\Actions\Dashboard;

use App\Models\User;

final class DismissUpgradeBanner
{
    public function handle(User $user): void
    {
        $user->forceFill(['banner_dismissed_at' => now()])->save();
    }
}
