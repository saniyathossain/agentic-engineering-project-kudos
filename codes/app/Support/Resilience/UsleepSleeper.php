<?php

declare(strict_types=1);

namespace App\Support\Resilience;

final class UsleepSleeper implements Sleeper
{
    public function sleepMs(int $milliseconds): void
    {
        if ($milliseconds > 0) {
            usleep($milliseconds * 1000);
        }
    }
}
