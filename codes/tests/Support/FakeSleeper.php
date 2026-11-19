<?php

declare(strict_types=1);

namespace Tests\Support;

use App\Support\Resilience\Sleeper;

final class FakeSleeper implements Sleeper
{
    /** @var list<int> */
    public array $slept = [];

    public function sleepMs(int $milliseconds): void
    {
        $this->slept[] = $milliseconds;
    }
}
