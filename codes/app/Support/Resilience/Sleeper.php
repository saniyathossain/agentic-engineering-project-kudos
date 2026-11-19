<?php

declare(strict_types=1);

namespace App\Support\Resilience;

interface Sleeper
{
    public function sleepMs(int $milliseconds): void;
}
