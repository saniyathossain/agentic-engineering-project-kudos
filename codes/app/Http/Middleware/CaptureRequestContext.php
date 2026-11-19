<?php

declare(strict_types=1);

namespace App\Http\Middleware;

use App\Support\Logging\ClientInfoFactory;
use App\Support\Logging\RequestContext;
use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Str;
use Symfony\Component\HttpFoundation\Response;

/**
 * Gives every request an id (accepted from the edge/client or generated), collects device info and echoes the id
 * on the response so a user can quote it. Runs first, so even errors raised later carry the id.
 */
final readonly class CaptureRequestContext
{
    private const VALID_ID = '/^[A-Za-z0-9._-]{8,64}$/';

    public function __construct(
        private RequestContext $context,
        private ClientInfoFactory $clients,
    ) {
    }

    public function handle(Request $request, Closure $next): Response
    {
        $header = (string) config('observability.request_id_header');

        $this->context->requestId = $this->acceptedId($request->headers->get($header));
        $this->context->traceId = $this->traceId($request->headers->get('traceparent'));
        $this->context->client = $this->clients->fromRequest($request);
        $this->context->ip = $request->ip();
        $this->context->method = $request->method();
        $this->context->path = '/'.ltrim($request->path(), '/');
        $this->context->startedAt = defined('LARAVEL_START') ? (float) LARAVEL_START : microtime(true);

        $request->attributes->set('request_id', $this->context->requestId);

        $response = $next($request);
        $response->headers->set($header, (string) $this->context->requestId);

        return $response;
    }

    private function acceptedId(?string $incoming): string
    {
        if ($incoming !== null && preg_match(self::VALID_ID, $incoming) === 1) {
            return $incoming;
        }

        return Str::lower(Str::random(16));
    }

    /** W3C trace context: version-traceid-spanid-flags. */
    private function traceId(?string $traceparent): ?string
    {
        if ($traceparent !== null && preg_match('/^[0-9a-f]{2}-([0-9a-f]{32})-[0-9a-f]{16}-[0-9a-f]{2}$/', $traceparent, $match) === 1) {
            return $match[1];
        }

        return null;
    }
}
