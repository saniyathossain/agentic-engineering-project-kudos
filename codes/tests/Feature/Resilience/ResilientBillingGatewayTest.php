<?php

declare(strict_types=1);

namespace Tests\Feature\Resilience;

use App\Contracts\BillingGateway;
use App\Data\Resilience\RetryPolicy;
use App\Enums\Jitter;
use App\Exceptions\BillingUnavailable;
use App\Models\User;
use App\Services\ResilientBillingGateway;
use App\Support\Resilience\Retrier;
use Stripe\Exception\ApiConnectionException;
use Stripe\Exception\InvalidRequestException;
use Tests\Support\FakeSleeper;
use Tests\TestCase;

final class ResilientBillingGatewayTest extends TestCase
{
    private FakeSleeper $sleeper;

    protected function setUp(): void
    {
        parent::setUp();
        $this->sleeper = new FakeSleeper();
        config(['resilience.retry' => ['attempts' => 3, 'base_delay_ms' => 10, 'max_delay_ms' => 100, 'factor' => 2, 'jitter' => Jitter::None->value, 'budget_ms' => 0]]);
        $this->assertSame(3, RetryPolicy::fromConfig()->attempts);
    }

    private function gateway(BillingGateway $inner): ResilientBillingGateway
    {
        return new ResilientBillingGateway($inner, new Retrier($this->sleeper));
    }

    /** @param  callable(int): string  $onCall */
    private function inner(callable $onCall): BillingGateway
    {
        return new class ($onCall) implements BillingGateway {
            public int $calls = 0;

            /** @param  callable(int): string  $onCall */
            public function __construct(private $onCall)
            {
            }

            public function checkoutUrl(User $user, string $successUrl, string $cancelUrl): string
            {
                return ($this->onCall)(++$this->calls);
            }

            public function isCheckoutCompleteFor(User $user, string $sessionId): bool
            {
                return ($this->onCall)(++$this->calls) === 'yes';
            }

            public function portalUrl(User $user, string $returnUrl): string
            {
                return ($this->onCall)(++$this->calls);
            }
        };
    }

    public function test_it_recovers_when_stripe_comes_back_within_the_attempts(): void
    {
        $inner = $this->inner(function (int $call): string {
            if ($call < 3) {
                throw ApiConnectionException::factory('connection reset');
            }

            return 'https://checkout.stripe.test/ok';
        });

        $url = $this->gateway($inner)->checkoutUrl(new User(), 'https://a.test/ok', 'https://a.test/no');

        $this->assertSame('https://checkout.stripe.test/ok', $url);
        $this->assertSame([10, 20], $this->sleeper->slept);
    }

    public function test_it_gives_up_with_billing_unavailable_after_the_attempts(): void
    {
        $inner = $this->inner(fn (int $call): never => throw ApiConnectionException::factory('down'));

        try {
            $this->gateway($inner)->portalUrl(new User(), 'https://a.test');
            $this->fail('should throw');
        } catch (BillingUnavailable $e) {
            $this->assertSame(__('billing.unavailable'), $e->getMessage());
            $this->assertInstanceOf(ApiConnectionException::class, $e->getPrevious());
        }

        $this->assertSame(2, count($this->sleeper->slept));
    }

    public function test_a_rejected_request_is_not_retried_and_is_not_billing_unavailable(): void
    {
        $inner = $this->inner(fn (int $call): never => throw InvalidRequestException::factory('No such price', 400));

        $this->expectException(InvalidRequestException::class);
        try {
            $this->gateway($inner)->checkoutUrl(new User(), 'https://a.test/ok', 'https://a.test/no');
        } finally {
            $this->assertSame([], $this->sleeper->slept);
        }
    }
}
