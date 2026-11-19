<?php

declare(strict_types=1);

namespace App\Support\Resilience;

use App\Data\Resilience\RetryPolicy;
use Closure;
use Illuminate\Support\Facades\Log;
use Throwable;

/** Runs an operation, retrying transient failures with exponential backoff and jitter. Every retry is logged. */
final readonly class Retrier
{
    public function __construct(private Sleeper $sleeper)
    {
    }

    /**
     * @template T
     *
     * @param  Closure(): T  $operation
     * @param  Closure(Throwable): bool  $transient  true when the failure is worth retrying
     * @return T
     *
     * @throws Throwable the last failure once attempts or the time budget are used up, or at once if not transient
     */
    public function run(Closure $operation, Closure $transient, string $name, ?RetryPolicy $policy = null): mixed
    {
        $policy ??= RetryPolicy::fromConfig();
        $started = microtime(true);
        $waited = 0;

        for ($attempt = 1; ; $attempt++) {
            try {
                return $operation();
            } catch (Throwable $failure) {
                if (! $transient($failure) || $attempt >= $policy->attempts) {
                    throw $failure;
                }

                $delay = $policy->delayAfter($attempt);
                // the budget covers the time the attempts themselves took as well as the waiting (the larger of the two
                // keeps this deterministic under a fake sleeper)
                $spent = max($waited, (int) ((microtime(true) - $started) * 1000));
                if ($policy->budgetMs > 0 && $spent + $delay > $policy->budgetMs) {
                    throw $failure;
                }
                $waited += $delay;

                Log::warning('retrying after a transient failure', [
                    'event' => 'retry',
                    'outcome' => 'degraded',
                    'operation' => $name,
                    'attempt' => $attempt,
                    'of' => $policy->attempts,
                    'delay_ms' => $delay,
                    'reason' => 'transient_failure',
                    'error' => $failure->getMessage(),
                ]);

                $this->sleeper->sleepMs($delay);
            }
        }
    }
}
