<?php

declare(strict_types=1);

namespace App\Enums;

enum TestimonialStatus: string
{
    case Pending = 'pending';
    case Published = 'published';
    case Hidden = 'hidden';
}
