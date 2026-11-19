<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Space;
use Illuminate\Support\Str;

final class SlugGenerator
{
    /** Slugs that would collide with application routes. */
    public const RESERVED = ['login', 'register', 'dashboard', 'settings', 'embed', 'billing', 'spaces', 'stripe', 'up', 'livez', 'readyz', 'healthz', 'status', 'outage', 'client-logs', 'forgot-password', 'reset-password', 'verify-email', 'confirm-password', 'logout', 'email', 'testimonials', 'build', 'storage'];

    public function unique(string $name, ?int $ignoreSpaceId = null): string
    {
        $base = Str::slug($name);
        $base = $base === '' ? 'space' : $base;
        $slug = $base;
        $suffix = 2;

        while ($this->taken($slug, $ignoreSpaceId)) {
            $slug = $base.'-'.$suffix++;
        }

        return $slug;
    }

    private function taken(string $slug, ?int $ignoreSpaceId): bool
    {
        if (in_array($slug, self::RESERVED, true)) {
            return true;
        }

        return Space::query()
            ->where('slug', $slug)
            ->when($ignoreSpaceId !== null, static fn ($q) => $q->where('id', '!=', $ignoreSpaceId))
            ->exists();
    }
}
