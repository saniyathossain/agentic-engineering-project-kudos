<?php

declare(strict_types=1);

namespace App\Enums;

enum Plan: string
{
    case Free = 'free';
    case Pro = 'pro';

    public function maxSpaces(): ?int
    {
        return match ($this) {
            self::Free => 1,
            self::Pro => null,
        };
    }

    public function maxTestimonialsPerSpace(): ?int
    {
        return match ($this) {
            self::Free => 10,
            self::Pro => null,
        };
    }

    public function label(): string
    {
        return __('enum.plan.'.$this->value);
    }
}
