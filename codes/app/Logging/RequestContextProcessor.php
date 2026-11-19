<?php

declare(strict_types=1);

namespace App\Logging;

use App\Support\Logging\RequestContext;
use App\Support\Logging\Scrub;
use Illuminate\Support\Facades\Auth;
use Monolog\LogRecord;
use Monolog\Processor\ProcessorInterface;

/** Copies the request facts onto every record's `extra`. Never resolves the user (no session or DB read while logging). */
final readonly class RequestContextProcessor implements ProcessorInterface
{
    public function __construct(private RequestContext $context)
    {
    }

    public function __invoke(LogRecord $record): LogRecord
    {
        if (! $this->context->active()) {
            return $record;
        }

        $extra = $record->extra + [
            'request_id' => $this->context->requestId,
            'trace_id' => $this->context->traceId,
            'ip' => $this->context->ip,
            'method' => $this->context->method,
            'path' => $this->context->path === null ? null : Scrub::path($this->context->path),
            'client' => $this->context->client?->toArray(),
            'duration_ms' => $this->context->elapsedMs(),
        ];

        if (Auth::hasUser()) {
            $extra['user_id'] = Auth::id();
        }

        return $record->with(extra: $extra);
    }
}
