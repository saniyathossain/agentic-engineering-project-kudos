<?php

declare(strict_types=1);

namespace App\Enums;

enum Jitter: string
{
    case Full = 'full';
    case Equal = 'equal';
    case None = 'none';
}
