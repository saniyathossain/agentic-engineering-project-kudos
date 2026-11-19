<?php

declare(strict_types=1);

namespace App\Support\Logging;

use App\Data\Logging\ClientInfo;

/** Per-request facts every log line should carry. One instance per request/job process (see AppServiceProvider). */
final class RequestContext
{
    public ?string $requestId = null;

    public ?string $traceId = null;

    public ?ClientInfo $client = null;

    public ?string $ip = null;

    public ?string $method = null;

    public ?string $path = null;

    public float $startedAt = 0.0;

    public function active(): bool
    {
        return $this->requestId !== null;
    }

    public function elapsedMs(): float
    {
        return $this->startedAt === 0.0 ? 0.0 : round((microtime(true) - $this->startedAt) * 1000, 1);
    }
}
