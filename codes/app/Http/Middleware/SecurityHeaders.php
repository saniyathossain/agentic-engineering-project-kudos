<?php

declare(strict_types=1);

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Vite;
use Symfony\Component\HttpFoundation\Response;

/**
 * Browser security headers owned by the application: a nonce-based Content-Security-Policy, Permissions-Policy,
 * Cross-Origin-Opener-Policy and HSTS over HTTPS. (nginx adds nosniff, referrer and frame headers at the edge.)
 * Only the embed pages may be framed by other sites.
 */
final class SecurityHeaders
{
    public const EMBEDDABLE = 'embeddable';

    public function handle(Request $request, Closure $next): Response
    {
        // the nonce goes to every script tag Vite and Ziggy print for this request
        $nonce = Vite::useCspNonce();

        $response = $next($request);

        $headers = $response->headers;
        $headers->set('Permissions-Policy', 'camera=(), microphone=(), geolocation=(), payment=(), usb=(), interest-cohort=()');
        $headers->set('Cross-Origin-Opener-Policy', 'same-origin');
        if ($request->isSecure()) {
            $headers->set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
        }

        if (config('security.csp.enabled')) {
            $name = config('security.csp.report_only') ? 'Content-Security-Policy-Report-Only' : 'Content-Security-Policy';
            $headers->set($name, $this->policy($nonce, $request->attributes->getBoolean(self::EMBEDDABLE), $request->isSecure()));
        }

        return $response;
    }

    private function policy(string $nonce, bool $embeddable, bool $secure): string
    {
        /** @var list<string> $styles */
        $styles = config('security.csp.style_sources', []);
        /** @var list<string> $fonts */
        $fonts = config('security.csp.font_sources', []);

        $directives = [
            "default-src 'self'",
            "script-src 'self' 'nonce-{$nonce}'",
            // React sets inline style attributes (charts, positioning), so inline styles stay allowed; scripts do not
            "style-src 'self' 'unsafe-inline' ".implode(' ', $styles),
            "font-src 'self' data: ".implode(' ', $fonts),
            "img-src 'self' data: blob:",
            "connect-src 'self'",
            "frame-src 'none'",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            'frame-ancestors '.($embeddable ? '*' : "'self'"),
        ];
        if ($secure) {
            $directives[] = 'upgrade-insecure-requests';
        }

        return implode('; ', array_map('trim', $directives));
    }
}
