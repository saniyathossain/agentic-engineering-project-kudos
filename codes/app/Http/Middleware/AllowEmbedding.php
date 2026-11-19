<?php

declare(strict_types=1);

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

final class AllowEmbedding
{
    public function handle(Request $request, Closure $next): Response
    {
        // SecurityHeaders (global) turns this flag into `frame-ancestors *` in the one Content-Security-Policy
        $request->attributes->set(SecurityHeaders::EMBEDDABLE, true);

        $response = $next($request);
        $response->headers->remove('X-Frame-Options');

        return $response;
    }
}
