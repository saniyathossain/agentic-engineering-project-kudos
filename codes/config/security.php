<?php

declare(strict_types=1);

return [
    /*
    | Content-Security-Policy. On by default in production only (the dev server loads scripts from the Vite origin).
    | CSP_REPORT_ONLY=true sends the header as Content-Security-Policy-Report-Only so a policy can be trialled.
    */
    'csp' => [
        'enabled' => (bool) env('CSP_ENABLED', env('APP_ENV') === 'production'),
        'report_only' => (bool) env('CSP_REPORT_ONLY', false),
        'style_sources' => ['https://fonts.bunny.net'],
        'font_sources' => ['https://fonts.bunny.net'],
    ],
];
