<?php

declare(strict_types=1);

namespace App\Enums;

/** How an event ended, as written in the log's `what.outcome` field. */
enum Outcome: string
{
    case Ok = 'ok';
    case Refused = 'refused';
    case Degraded = 'degraded';
    case Failed = 'failed';

    public static function forStatus(int $status): self
    {
        return match (true) {
            $status >= 500 => self::Failed,
            $status >= 400 => self::Refused,
            default => self::Ok,
        };
    }
}
