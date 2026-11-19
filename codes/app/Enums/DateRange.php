<?php

declare(strict_types=1);

namespace App\Enums;

enum DateRange: int
{
    case Week = 7;
    case Month = 30;
    case Quarter = 90;
}
