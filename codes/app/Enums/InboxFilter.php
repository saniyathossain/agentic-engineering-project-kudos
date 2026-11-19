<?php

declare(strict_types=1);

namespace App\Enums;

enum InboxFilter: string
{
    case All = 'all';
    case Favorite = 'favorite';
    case Pending = 'pending';
    case Published = 'published';
    case Hidden = 'hidden';
}
