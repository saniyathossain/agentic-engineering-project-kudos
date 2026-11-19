<?php

declare(strict_types=1);

namespace App\Data\Resilience;

use App\Enums\Jitter;
use Closure;

/** How hard to retry: attempts (including the first), exponential delay bounds, jitter and a total time budget. */
final readonly class RetryPolicy
{
    public function __construct(
        public int $attempts,
        public int $baseDelayMs,
        public int $maxDelayMs,
        public float $factor,
        public Jitter $jitter,
        public int $budgetMs,
    ) {
    }

    public static function fromConfig(): self
    {
        /** @var array{attempts: int, base_delay_ms: int, max_delay_ms: int, factor: float, jitter: string, budget_ms: int} $retry */
        $retry = config('resilience.retry');

        return new self(
            attempts: max(1, $retry['attempts']),
            baseDelayMs: max(0, $retry['base_delay_ms']),
            maxDelayMs: max(0, $retry['max_delay_ms']),
            factor: max(1.0, $retry['factor']),
            jitter: Jitter::tryFrom($retry['jitter']) ?? Jitter::Full,
            budgetMs: max(0, $retry['budget_ms']),
        );
    }

    /**
     * Milliseconds to wait after failed attempt number $attempt (1-based).
     *
     * @param  (Closure(int, int): int)|null  $random  returns an int in [min, max]; injectable for tests
     */
    public function delayAfter(int $attempt, ?Closure $random = null): int
    {
        $random ??= static fn (int $min, int $max): int => random_int($min, $max);
        $ceiling = (int) min($this->maxDelayMs, $this->baseDelayMs * ($this->factor ** max(0, $attempt - 1)));

        return match ($this->jitter) {
            Jitter::None => $ceiling,
            Jitter::Equal => intdiv($ceiling, 2) + $random(0, intdiv($ceiling, 2)),
            Jitter::Full => $random(0, $ceiling),
        };
    }

    /**
     * Backoff schedule in seconds for queue jobs (`public function backoff(): array`).
     *
     * @return list<int>
     */
    public function backoffSeconds(): array
    {
        $schedule = [];
        for ($attempt = 1; $attempt < $this->attempts; $attempt++) {
            $schedule[] = (int) ceil(min($this->maxDelayMs, $this->baseDelayMs * ($this->factor ** ($attempt - 1))) / 1000);
        }

        return $schedule;
    }
}
