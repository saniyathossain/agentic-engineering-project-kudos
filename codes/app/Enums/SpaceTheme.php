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
            self::Light => __('enum.theme.light'),
            self::Dark => __('enum.theme.dark'),
            self::Brand => __('enum.theme.brand'),
        };
    }
}
