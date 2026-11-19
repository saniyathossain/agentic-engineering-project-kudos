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
        /** @var Response $response */
        $response = $next($request);

        $response->headers->remove('X-Frame-Options');
        $response->headers->set('Content-Security-Policy', 'frame-ancestors *');

        return $response;
    }
}
