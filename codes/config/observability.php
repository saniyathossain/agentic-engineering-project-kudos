<?php

declare(strict_types=1);

return [
    /*
    | Identity of this process in every log line (the "where.service" / "where.role" fields).
    */
    'service' => env('LOG_SERVICE', 'kudos'),
    'role' => env('APP_ROLE', 'web'),
    'version' => env('APP_VERSION', 'dev'),
    'commit' => env('APP_COMMIT', ''),

    /*
    | Correlation: accepted from the edge/client when valid, otherwise generated, and echoed on the response.
    */
    'request_id_header' => env('LOG_REQUEST_ID_HEADER', 'X-Request-ID'),

    /*
    | Access log: one line per request. all | errors (4xx, 5xx and slow only) | off.
    */
    'access' => [
        'mode' => env('LOG_ACCESS', 'all'),
        'slow_ms' => (int) env('LOG_ACCESS_SLOW_MS', 1000),
        'skip' => ['up', 'livez', 'readyz', 'healthz', 'favicon.ico', 'build/*', 'client-logs'],
    ],

    /*
    | Exception traces keep this many frames; message text is cut at this many characters.
    */
    'trace_limit' => (int) env('LOG_TRACE_LIMIT', 10),
    'message_limit' => (int) env('LOG_MESSAGE_LIMIT', 2000),

    /*
    | Any context key containing one of these fragments is replaced by [redacted].
    */
    'redact' => ['password', 'passwd', 'secret', 'token', 'authorization', 'cookie', 'card', 'cvc', 'api_key', 'apikey', 'signature'],
];
