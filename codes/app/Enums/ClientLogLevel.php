<?php

declare(strict_types=1);

namespace App\Enums;

enum ClientLogLevel: string
{
    case Debug = 'debug';
    case Info = 'info';
    case Warn = 'warn';
    case Error = 'error';

    /** The PSR-3 level this browser level is logged at. */
    public function psr(): string
    {
        return match ($this) {
            self::Debug => 'debug',
            self::Info => 'info',
            self::Warn => 'warning',
            self::Error => 'error',
        };
    }
}
