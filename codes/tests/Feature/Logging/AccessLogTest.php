<?php

declare(strict_types=1);

namespace Tests\Feature\Logging;

use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Log;
use Tests\TestCase;

final class AccessLogTest extends TestCase
{
    use RefreshDatabase;

    public function test_a_request_writes_one_access_line(): void
    {
        Log::spy();

        $this->get('/login')->assertOk();

        Log::shouldHaveReceived('log')->once()->withArgs(
            fn (string $level, string $message, array $context): bool => $level === 'info' && $message === 'http'
                && $context['event'] === 'http.request' && $context['status'] === 200 && $context['outcome'] === 'ok',
        );
    }

    public function test_unknown_pages_are_logged_as_refused(): void
    {
        Log::spy();

        $this->get('/nope-nope')->assertNotFound();

        Log::shouldHaveReceived('log')->withArgs(
            fn (string $level, string $message, array $context): bool => $level === 'info' && $context['status'] === 404 && $context['outcome'] === 'refused',
        );
    }

    public function test_health_checks_are_not_logged(): void
    {
        Log::spy();

        $this->get('/up');

        Log::shouldNotHaveReceived('log');
    }

    public function test_errors_mode_skips_successful_fast_requests(): void
    {
        config(['observability.access.mode' => 'errors']);
        Log::spy();

        $this->get('/login')->assertOk();

        Log::shouldNotHaveReceived('log');
    }

    public function test_off_mode_logs_nothing(): void
    {
        config(['observability.access.mode' => 'off']);
        Log::spy();

        $this->get('/nope-nope');

        Log::shouldNotHaveReceived('log');
    }

    public function test_query_values_are_never_logged_only_their_keys(): void
    {
        Log::spy();

        $this->get('/login?token=secret123&a=1')->assertOk();

        Log::shouldHaveReceived('log')->withArgs(
            fn (string $level, string $message, array $context): bool => $context['query_keys'] === ['token', 'a'] && ! str_contains((string) json_encode($context), 'secret123'),
        );
    }
}
