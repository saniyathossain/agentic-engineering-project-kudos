<?php

declare(strict_types=1);

namespace App\Support\Errors;

use App\Support\Logging\RequestContext;
use Illuminate\Http\Request;
use Illuminate\Http\Response;
use Inertia\Inertia;
use Symfony\Component\HttpFoundation\Response as SymfonyResponse;
use Throwable;

/** Turns a failure into the response the caller can use: JSON for APIs, a friendly page for browsers. */
final readonly class ErrorResponder
{
    public function __construct(
        private ExceptionMapper $mapper,
        private RequestContext $context,
    ) {
    }

    public function respond(Throwable $e, Request $request): ?SymfonyResponse
    {
        $page = $this->mapper->map($e);
        // in debug an unexpected bug should show its trace, not the friendly page
        if ($page === null || ($page->status === 500 && config('app.debug'))) {
            return null;
        }

        $headers = $this->headers($page);

        if ($request->header('X-Inertia')) {
            return $this->forInertia($page, $request, $headers);
        }

        if ($request->expectsJson()) {
            return response()->json([
                'error' => $page->status === 503 ? __('errors.unavailable') : __('errors.generic'),
                'code' => $page->dependency === null ? 'error' : 'unavailable',
                'dependency' => $page->dependency?->value,
                'request_id' => $this->context->requestId,
            ], $page->status, $headers);
        }

        return response()->view('errors.status', ['page' => $page, 'requestId' => $this->context->requestId], $page->status, $headers);
    }

    /**
     * An outage needs the database-free HTML page, so the browser is sent to the URL for a full-page load. Every
     * other failure is shown in place by the React error page (no second request, no second log line).
     *
     * @param  array<string, string>  $headers
     */
    private function forInertia(ErrorPage $page, Request $request, array $headers): SymfonyResponse
    {
        if ($page->polls()) {
            return new Response('', 409, $headers + ['X-Inertia-Location' => $request->isMethodSafe() ? $request->fullUrl() : url('/')]);
        }

        $response = Inertia::render('errors/error', [
            'status' => $page->status,
            'copyKey' => $page->copyKey(),
            'retryAfter' => $page->retryAfterSeconds(),
            'requestId' => $this->context->requestId,
        ])->toResponse($request);
        $response->setStatusCode($page->status);
        $response->headers->add($headers);

        return $response;
    }

    /** @return array<string, string> */
    private function headers(ErrorPage $page): array
    {
        $headers = ['Cache-Control' => 'no-store'];
        if ($page->retryAfterSeconds() !== null) {
            $headers['Retry-After'] = (string) $page->retryAfterSeconds();
        }
        if ($this->context->requestId !== null) {
            $headers[(string) config('observability.request_id_header')] = $this->context->requestId;
        }

        return $headers;
    }
}
