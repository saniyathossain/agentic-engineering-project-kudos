<?php

declare(strict_types=1);

namespace App\Support\Errors;

use App\Enums\Dependency;

/** What the user is told about a failure. Keys point into lang/en.json (status.title.*, status.why.*). */
final readonly class ErrorPage
{
    /** Statuses that have their own words; other 4xx read as "that request did not work", other 5xx as a server error. */
    private const OWN_COPY = [403, 404, 419, 429, 503];

    public function __construct(
        public int $status,
        public ?Dependency $dependency = null,
        public ?int $retryAfter = null,
    ) {
    }

    /** True when waiting helps (drives the calm "checking" look). */
    public function transient(): bool
    {
        return $this->status === 503 || $this->status === 429;
    }

    /** Only an outage is polled and reloaded automatically: reloading a throttled URL would extend the throttle. */
    public function polls(): bool
    {
        return $this->status === 503;
    }

    public function copyKey(): string
    {
        return match (true) {
            in_array($this->status, self::OWN_COPY, true) => (string) $this->status,
            $this->status >= 400 && $this->status < 500 => '4xx',
            default => '500',
        };
    }

    /** Seconds the client should wait; an outage defaults to 5. */
    public function retryAfterSeconds(): ?int
    {
        return $this->retryAfter ?? ($this->status === 503 ? 5 : null);
    }
}
