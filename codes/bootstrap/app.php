<?php

declare(strict_types=1);

use App\Http\Controllers\HealthController;
use App\Http\Middleware\CaptureRequestContext;
use App\Http\Middleware\HandleInertiaRequests;
use App\Http\Middleware\LogHttpRequest;
use App\Http\Middleware\SecurityHeaders;
use App\Support\Errors\ErrorResponder;
use Illuminate\Foundation\Application;
use Illuminate\Foundation\Configuration\Exceptions;
use Illuminate\Foundation\Configuration\Middleware;
use Illuminate\Http\Middleware\AddLinkHeadersForPreloadedAssets;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;

return Application::configure(basePath: dirname(__DIR__))
    ->withRouting(
        web: __DIR__.'/../routes/web.php',
        commands: __DIR__.'/../routes/console.php',
        health: '/up',
        then: function (): void {
            // probes live outside the web group: no session, no DB read just to say "alive"
            Route::get('livez', [HealthController::class, 'live']);
            Route::get('readyz', [HealthController::class, 'ready']);
        },
    )
    ->withMiddleware(function (Middleware $middleware) {
        $middleware->preventRequestForgery(except: ['client-logs']);
        $middleware->prepend(CaptureRequestContext::class);
        $middleware->append(SecurityHeaders::class);
        $middleware->append(LogHttpRequest::class);
        $middleware->web(append: [
            HandleInertiaRequests::class,
            AddLinkHeadersForPreloadedAssets::class,
        ]);
    })
    ->withExceptions(function (Exceptions $exceptions) {
        // Every failure reaches the user as a friendly page (or JSON) that carries the request id; expected dependency
        // failures are 503 with Retry-After, never a bare 500.
        $exceptions->render(fn (Throwable $e, Request $request) => app(ErrorResponder::class)->respond($e, $request));
    })->create();
