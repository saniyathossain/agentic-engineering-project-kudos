<?php

declare(strict_types=1);

namespace App\Data\Health;

final readonly class HealthCheck
{
    public function __construct(
        public string $name,
        public bool $critical,
        public bool $up,
    ) {
    }

    /** @return array{name: string, up: bool, critical: bool} */
    public function toArray(): array
    {
        return ['name' => $this->name, 'up' => $this->up, 'critical' => $this->critical];
    }
}
