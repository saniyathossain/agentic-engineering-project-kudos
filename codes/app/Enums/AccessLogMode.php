<?php

declare(strict_types=1);

namespace App\Enums;

enum AccessLogMode: string
{
    case All = 'all';
    case Errors = 'errors';
    case Off = 'off';

    public static function fromConfig(): self
    {
        return self::tryFrom((string) config('observability.access.mode')) ?? self::All;
    }
}
