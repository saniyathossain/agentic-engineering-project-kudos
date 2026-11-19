<?php

declare(strict_types=1);

namespace Tests\Feature\Logging;

use App\Logging\FiveWFormatter;
use DateTimeImmutable;
use Monolog\Level;
use Monolog\LogRecord;
use RuntimeException;
use Tests\TestCase;

final class FiveWFormatterTest extends TestCase
{
    /**
     * @param  array<string, mixed>  $context
     * @param  array<string, mixed>  $extra
     * @return array<string, mixed>
     */
    private function line(Level $level, string $message, array $context = [], array $extra = []): array
    {
        $record = new LogRecord(new DateTimeImmutable('2026-11-19T09:30:00+06:00'), 'test', $level, $message, $context, $extra);
        $json = (new FiveWFormatter())->format($record);

        $this->assertStringEndsWith("\n", $json, 'one JSON object per line');
        $this->assertSame(1, substr_count($json, "\n"));

        return json_decode($json, true, flags: JSON_THROW_ON_ERROR);
    }

    public function test_a_plain_info_line_has_all_five_groups(): void
    {
        $line = $this->line(Level::Info, 'hello');

        $this->assertSame('INFO', $line['level']);
        $this->assertSame('hello', $line['msg']);
        $this->assertSame('2026-11-19T09:30:00.000+06:00', $line['time']);
        foreach (['who', 'what', 'where', 'when', 'why'] as $group) {
            $this->assertArrayHasKey($group, $line);
        }
        $this->assertSame('process', $line['who']['actor']);
        $this->assertSame('ok', $line['what']['outcome']);
        $this->assertSame('kudos', $line['where']['service']);
    }

    public function test_request_facts_land_in_the_right_groups(): void
    {
        $line = $this->line(Level::Info, 'http', ['event' => 'http.request', 'status' => 200, 'duration_ms' => 12.5], [
            'request_id' => 'abc12345',
            'trace_id' => str_repeat('a', 32),
            'user_id' => 7,
            'ip' => '203.0.113.7',
            'method' => 'GET',
            'path' => '/spaces',
            'client' => ['type' => 'mobile', 'os' => 'iOS'],
        ]);

        $this->assertSame('user', $line['who']['actor']);
        $this->assertSame(7, $line['who']['user_id']);
        $this->assertSame('203.0.113.7', $line['who']['ip']);
        $this->assertSame('http.request', $line['what']['event']);
        $this->assertSame(200, $line['what']['status']);
        $this->assertSame('/spaces', $line['where']['path']);
        $this->assertSame(12.5, $line['when']['duration_ms']);
        $this->assertSame('abc12345', $line['request_id']);
        $this->assertSame(['type' => 'mobile', 'os' => 'iOS'], $line['client']);
    }

    public function test_empty_groups_are_json_objects(): void
    {
        $record = new LogRecord(new DateTimeImmutable(), 'test', Level::Info, 'x');

        $this->assertStringContainsString('"why":{}', (new FiveWFormatter())->format($record));
    }

    public function test_guest_requests_are_marked_as_guests(): void
    {
        $this->assertSame('guest', $this->line(Level::Info, 'x', [], ['request_id' => 'abc12345'])['who']['actor']);
    }

    public function test_outcome_follows_the_level_unless_given(): void
    {
        $this->assertSame('degraded', $this->line(Level::Warning, 'x')['what']['outcome']);
        $this->assertSame('failed', $this->line(Level::Error, 'x')['what']['outcome']);
        $this->assertSame('refused', $this->line(Level::Warning, 'x', ['outcome' => 'refused'])['what']['outcome']);
    }

    public function test_why_carries_reason_and_hint(): void
    {
        $line = $this->line(Level::Warning, 'retrying', ['reason' => 'dependency_unavailable', 'hint' => 'retry shortly']);

        $this->assertSame(['reason' => 'dependency_unavailable', 'hint' => 'retry shortly'], $line['why']);
    }

    public function test_exceptions_are_expanded_with_source_and_bounded_trace(): void
    {
        $line = $this->line(Level::Error, 'boom', ['exception' => new RuntimeException('db down', 12, new RuntimeException('socket'))]);

        $this->assertSame(RuntimeException::class, $line['what']['exception']['class']);
        $this->assertSame('db down', $line['what']['error']);
        $this->assertSame(12, $line['what']['exception']['code']);
        $this->assertStringContainsString('socket', $line['what']['exception']['previous']);
        $this->assertLessThanOrEqual(10, count($line['what']['exception']['trace']));
        $this->assertStringContainsString('FiveWFormatterTest.php', $line['where']['source']);
    }

    public function test_sensitive_context_is_redacted_at_any_depth(): void
    {
        $line = $this->line(Level::Info, 'x', ['password' => 'hunter2', 'nested' => ['stripe_secret' => 'sk_live_1', 'ok' => 'fine'], 'plain' => 'visible']);

        $this->assertSame('[redacted]', $line['context']['password']);
        $this->assertSame('[redacted]', $line['context']['nested']['stripe_secret']);
        $this->assertSame('fine', $line['context']['nested']['ok']);
        $this->assertSame('visible', $line['context']['plain']);
    }

    public function test_long_messages_are_cut(): void
    {
        $line = $this->line(Level::Info, str_repeat('x', 5000));

        $this->assertLessThanOrEqual(2001, mb_strlen($line['msg']));
    }
}
