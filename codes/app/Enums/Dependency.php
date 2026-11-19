<?php

declare(strict_types=1);

namespace App\Enums;

/** Things the app depends on whose outage is reported to the user as a 503. */
enum Dependency: string
{
    case Database = 'database';
    case Billing = 'billing';
}
