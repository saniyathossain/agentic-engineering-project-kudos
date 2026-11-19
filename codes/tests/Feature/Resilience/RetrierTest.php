<?php

declare(strict_types=1);

namespace Tests\Feature\Resilience;

use App\Data\Resilience\RetryPolicy;
use App\Enums\Jitter;
use App\Support\Resilience\Retrier;
use Illuminate\Support\Facades\Log;
use RuntimeException;
use Tests\Support\FakeSleeper;
use Tests\TestCase;

final class RetrierTest extends TestCase
{
    private FakeSleeper $sleeper;

    private Retrier $retrier;

    protected function setUp(): void
    {
        parent::setUp();
        $this->sleeper = new FakeSleeper();
        $this->retrier = new Retrier($this->sleeper);
    }

    private function policy(int $attempts = 4, int $budget = 0): RetryPolicy
    {
        return new RetryPolicy($attempts, 100, 1000, 2.0, Jitter::None, $budget);
    }

    public function test_a_first_time_success_never_sleeps(): void
    {
        $result = $this->retrier->run(fn (): string => 'ok', fn (): bool => true, 'test', $this->policy());

        $this->assertSame('ok', $result);
        $this->assertSame([], $this->sleeper->slept);
    }

    public function test_transient_failures_are_retried_with_growing_delays_until_success(): void
    {
        Log::spy();
        $calls = 0;

        $result = $this->retrier->run(function () use (&$calls): string {
            if (++$calls < 3) {
                throw new RuntimeException('flaky');
            }

            return 'done';
        }, fn (): bool => true, 'stripe.test', $this->policy());

        $this->assertSame('done', $result);
        $this->assertSame(3, $calls);
        $this->assertSame([100, 200], $this->sleeper->slept);
        Log::shouldHaveReceived('warning')->twice()->withArgs(
            fn (string $message, array $context): bool => $context['event'] === 'retry' && $context['operation'] === 'stripe.test' && $context['outcome'] === 'degraded',
        );
    }

    public function test_the_last_failure_is_thrown_when_attempts_run_out(): void
    {
        $calls = 0;

        try {
            $this->retrier->run(function () use (&$calls): never {
                throw new RuntimeException('attempt '.++$calls);
            }, fn (): bool => true, 'test', $this->policy(attempts: 3));
            $this->fail('should have thrown');
        } catch (RuntimeException $e) {
            $this->assertSame('attempt 3', $e->getMessage());
        }

        $this->assertSame(3, $calls);
        $this->assertCount(2, $this->sleeper->slept);
    }

    public function test_non_transient_failures_are_not_retried(): void
    {
        $calls = 0;

        $this->expectException(RuntimeException::class);
        try {
            $this->retrier->run(function () use (&$calls): never {
                ++$calls;
                throw new RuntimeException('bad request');
            }, fn (): bool => false, 'test', $this->policy());
        } finally {
            $this->assertSame(1, $calls);
            $this->assertSame([], $this->sleeper->slept);
        }
    }

    public function test_the_time_budget_stops_retrying_early(): void
    {
        $calls = 0;

        try {
            $this->retrier->run(function () use (&$calls): never {
                ++$calls;
                throw new RuntimeException('slow');
            }, fn (): bool => true, 'test', $this->policy(attempts: 10, budget: 250));
        } catch (RuntimeException) {
            // expected
        }

        // delays 100 + 200 would exceed the 250 ms budget at the second wait
        $this->assertSame(2, $calls);
        $this->assertSame([100], $this->sleeper->slept);
    }
}
