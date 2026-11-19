<?php

declare(strict_types=1);

namespace Tests\Feature\Resilience;

use App\Data\Resilience\RetryPolicy;
use App\Enums\Jitter;
use Tests\TestCase;

final class RetryPolicyTest extends TestCase
{
    private function policy(Jitter $jitter = Jitter::None, int $attempts = 5): RetryPolicy
    {
        return new RetryPolicy($attempts, 200, 1000, 2.0, $jitter, 0);
    }

    public function test_delay_grows_exponentially_and_is_capped(): void
    {
        $policy = $this->policy();

        $this->assertSame([200, 400, 800, 1000, 1000], array_map($policy->delayAfter(...), [1, 2, 3, 4, 5]));
    }

    public function test_full_jitter_picks_between_zero_and_the_ceiling(): void
    {
        $seen = [];
        $this->policy(Jitter::Full)->delayAfter(3, function (int $min, int $max) use (&$seen): int {
            $seen = [$min, $max];

            return $max;
        });

        $this->assertSame([0, 800], $seen);
    }

    public function test_equal_jitter_keeps_half_fixed(): void
    {
        $delay = $this->policy(Jitter::Equal)->delayAfter(2, static fn (int $min, int $max): int => $max);

        $this->assertSame(400, $delay); // 200 fixed + up to 200 random
        $this->assertSame(200, $this->policy(Jitter::Equal)->delayAfter(2, static fn (int $min, int $max): int => $min));
    }

    public function test_it_reads_the_env_driven_config(): void
    {
        config(['resilience.retry' => ['attempts' => 6, 'base_delay_ms' => 50, 'max_delay_ms' => 900, 'factor' => 3, 'jitter' => 'equal', 'budget_ms' => 1234]]);

        $policy = RetryPolicy::fromConfig();

        $this->assertSame(6, $policy->attempts);
        $this->assertSame(50, $policy->baseDelayMs);
        $this->assertSame(900, $policy->maxDelayMs);
        $this->assertSame(3.0, $policy->factor);
        $this->assertSame(Jitter::Equal, $policy->jitter);
        $this->assertSame(1234, $policy->budgetMs);
    }

    public function test_bad_config_falls_back_to_safe_values(): void
    {
        config(['resilience.retry' => ['attempts' => 0, 'base_delay_ms' => -5, 'max_delay_ms' => 10, 'factor' => 0.1, 'jitter' => 'nonsense', 'budget_ms' => -1]]);

        $policy = RetryPolicy::fromConfig();

        $this->assertSame(1, $policy->attempts);
        $this->assertSame(0, $policy->baseDelayMs);
        $this->assertSame(1.0, $policy->factor);
        $this->assertSame(Jitter::Full, $policy->jitter);
    }

    public function test_job_backoff_schedule_in_seconds(): void
    {
        $this->assertSame([1, 1, 1, 1], $this->policy(attempts: 5)->backoffSeconds());
        $this->assertSame([], $this->policy(attempts: 1)->backoffSeconds());
    }
}
