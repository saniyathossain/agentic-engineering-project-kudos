<?php

declare(strict_types=1);

namespace App\Http\Middleware;

use App\Support\Logging\RequestContext;
use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
use Symfony\Component\HttpFoundation\Response;

/** The access log: one line per request, written after the response is sent (terminable). */
final readonly class LogHttpRequest
{
    public function __construct(private RequestContext $context)
    {
    }

    public function handle(Request $request, Closure $next): Response
    {
        return $next($request);
    }

    public function terminate(Request $request, Response $response): void
    {
        $mode = (string) config('observability.access.mode');
        if ($mode === 'off' || $request->is(...(array) config('observability.access.skip'))) {
            return;
        }

        $status = $response->getStatusCode();
        $duration = $this->context->elapsedMs();
        $slow = $duration >= (int) config('observability.access.slow_ms');

        if ($mode === 'errors' && $status < 400 && ! $slow) {
            return;
        }

        $context = array_filter([
            'event' => 'http.request',
            'status' => $status,
            'outcome' => $this->outcome($status),
            'duration_ms' => $duration,
            'reason' => $slow ? 'slow' : null,
            'bytes' => strlen((string) $response->getContent()) ?: null,
            'query_keys' => $request->query() === [] ? null : array_keys($request->query()),
            'referer' => $request->headers->get('referer') === null ? null : mb_substr((string) $request->headers->get('referer'), 0, 200),
        ], static fn (mixed $v): bool => $v !== null);

        Log::log($this->level($status, $slow), 'http', $context);
    }

    private function outcome(int $status): string
    {
        return match (true) {
            $status >= 500 => 'failed',
            $status >= 400 => 'refused',
            default => 'ok',
        };
    }

    private function level(int $status, bool $slow): string
    {
        return match (true) {
            $status >= 500 => 'error',
            $status === 404 || $status === 401 => 'info',
            $status >= 400 || $slow => 'warning',
            default => 'info',
        };
    }
}
