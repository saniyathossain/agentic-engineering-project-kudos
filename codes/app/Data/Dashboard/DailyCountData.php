<?php

declare(strict_types=1);

namespace App\Data\Dashboard;

final readonly class DailyCountData
{
    public function __construct(
        public string $date,
        public int $count,
    ) {
    }

    /** @return array{date: string, count: int} */
    public function toArray(): array
    {
        return ['date' => $this->date, 'count' => $this->count];
    }
}
