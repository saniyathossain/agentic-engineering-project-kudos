<?php

declare(strict_types=1);

namespace App\Enums;

enum SpaceTheme: string
{
    case Light = 'light';
    case Dark = 'dark';
    case Brand = 'brand';

    public function label(): string
    {
        return match ($this) {
            self::Light => 'Light',
            self::Dark => 'Dark',
            self::Brand => 'Brand',
        };
    }
}
