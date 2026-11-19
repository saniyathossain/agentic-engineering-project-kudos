<?php

declare(strict_types=1);

return [
    /*
    | Retry with exponential backoff for outbound calls (Stripe today) and anything else that wraps itself in
    | App\Support\Resilience\Retrier. delay(n) = min(max, base * factor^(n-1)), then jitter is applied.
    | jitter: full (random 0..delay) | equal (half fixed, half random) | none
    | budget_ms caps the total time of all attempts plus the waiting between them (0 = attempts only).
    */
    'retry' => [
        'attempts' => (int) env('RETRY_ATTEMPTS', 3),
        'base_delay_ms' => (int) env('RETRY_BASE_DELAY_MS', 200),
        'max_delay_ms' => (int) env('RETRY_MAX_DELAY_MS', 5000),
        'factor' => (float) env('RETRY_FACTOR', 2),
        'jitter' => env('RETRY_JITTER', 'full'),
        'budget_ms' => (int) env('RETRY_BUDGET_MS', 15000),
    ],

    /*
    | The browser's own backoff while the server is unreachable (outage page and the connection banner).
    */
    'outage' => [
        'first_ms' => (int) env('OUTAGE_FIRST_MS', 4000),
        'longest_ms' => (int) env('OUTAGE_LONGEST_MS', 15000),
    ],
];
