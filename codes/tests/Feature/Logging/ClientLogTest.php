<?php

declare(strict_types=1);

namespace Tests\Feature\Logging;

use Illuminate\Support\Facades\Log;
use Illuminate\Testing\TestResponse;
use Tests\TestCase;

final class ClientLogTest extends TestCase
{
    /** @return array<string, mixed> */
    private function payload(array $overrides = []): array
    {
        return array_merge([
            'lines' => [['level' => 'error', 'message' => 'TypeError: x is undefined', 'tag' => 'window.onerror', 'url' => '/spaces', 'data' => ['line' => 12]]],
            'device' => ['timezone' => 'Asia/Dhaka', 'screen' => '390x844'],
            'page_view_id' => 'pv-123',
        ], $overrides);
    }

    public function test_browser_lines_are_written_to_the_server_log_as_browser_events(): void
    {
        Log::spy();

        $this->browserPost($this->payload())->assertNoContent();

        Log::shouldHaveReceived('log')->withArgs(
            fn (string $level, string $message, array $context): bool => $level === 'error' && $message === 'TypeError: x is undefined'
                && $context['event'] === 'client.log' && $context['source'] === 'browser' && $context['tag'] === 'window.onerror'
                && $context['device']['timezone'] === 'Asia/Dhaka' && $context['page_view_id'] === 'pv-123',
        );
    }

    public function test_warn_is_logged_as_warning(): void
    {
        Log::spy();

        $this->browserPost($this->payload(['lines' => [['level' => 'warn', 'message' => 'slow']]]))->assertNoContent();

        Log::shouldHaveReceived('log')->withArgs(fn (string $level): bool => $level === 'warning');
    }

    public function test_data_that_fits_the_limit_is_kept(): void
    {
        Log::spy();

        $this->browserPost($this->payload(['lines' => [['level' => 'info', 'message' => 'big', 'data' => ['note' => str_repeat('hello world ', 80)]]]]))->assertNoContent();

        Log::shouldHaveReceived('log')->withArgs(fn (string $l, string $m, array $context): bool => ($context['data']['note'] ?? null) === trim(str_repeat('hello world ', 80)));
    }

    public function test_invalid_payloads_are_rejected(): void
    {
        $this->browserPost(['lines' => []])->assertUnprocessable();
        $this->browserPost($this->payload(['lines' => [['level' => 'fatal', 'message' => 'x']]]))->assertUnprocessable();
        $this->browserPost($this->payload(['lines' => array_fill(0, 21, ['level' => 'info', 'message' => 'x'])]))->assertUnprocessable();
    }

    public function test_cross_site_and_non_browser_posts_are_refused(): void
    {
        $this->withHeader('Origin', 'https://evil.example')->postJson('/client-logs', $this->payload())->assertForbidden();
        $this->withHeader('Sec-Fetch-Site', 'cross-site')->postJson('/client-logs', $this->payload())->assertForbidden();
        $this->postJson('/client-logs', $this->payload())->assertForbidden();
    }

    public function test_same_origin_is_accepted_by_either_header(): void
    {
        $this->withHeader('Sec-Fetch-Site', 'same-origin')->postJson('/client-logs', $this->payload())->assertNoContent();
        $this->withHeader('Origin', 'http://localhost')->postJson('/client-logs', $this->payload())->assertNoContent();
    }

    public function test_oversized_data_is_refused_at_validation(): void
    {
        $this->browserPost($this->payload(['lines' => [['level' => 'info', 'message' => 'big', 'data' => ['blob' => str_repeat('x', 5000)]]]]))->assertUnprocessable();
    }

    public function test_the_endpoint_is_throttled(): void
    {
        $statuses = [];
        for ($i = 0; $i < 62; $i++) {
            $statuses[] = $this->browserPost($this->payload())->status();
        }

        $this->assertContains(429, $statuses);
    }

    /** @param  array<string, mixed>  $payload */
    private function browserPost(array $payload): TestResponse
    {
        return $this->withHeader('Origin', 'http://localhost')->postJson('/client-logs', $payload);
    }
}
