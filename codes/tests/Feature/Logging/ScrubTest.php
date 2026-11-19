<?php

declare(strict_types=1);

namespace Tests\Feature\Logging;

use App\Logging\FiveWFormatter;
use App\Support\Logging\Scrub;
use DateTimeImmutable;
use Illuminate\Database\QueryException;
use Monolog\Level;
use Monolog\LogRecord;
use PDOException;
use Tests\TestCase;

final class ScrubTest extends TestCase
{
    public function test_emails_hashes_keys_and_tokens_are_masked_in_text(): void
    {
        $text = 'user a.b+c@example.com hash $2y$12$'.str_repeat('a', 53).' key sk_live_abcdefgh12345 auth Bearer abc.def-123 token '.str_repeat('f', 64);

        $clean = Scrub::text($text);

        foreach (['a.b+c@example.com', '$2y$12$', 'sk_live_abcdefgh12345', 'abc.def-123', str_repeat('f', 64)] as $secret) {
            $this->assertStringNotContainsString($secret, $clean);
        }
        $this->assertStringContainsString('[email]', $clean);
    }

    public function test_normal_text_is_untouched(): void
    {
        $this->assertSame('Connection refused on port 5432', Scrub::text('Connection refused on port 5432'));
    }

    public function test_paths_lose_query_and_token_segments_but_keep_ids(): void
    {
        $token = str_repeat('a', 64);

        $this->assertSame('/reset-password/[redacted]', Scrub::path("/reset-password/$token?email=a@b.com"));
        $this->assertSame('/verify-email/7/[redacted]', Scrub::path('/verify-email/7/'.str_repeat('b', 40).'?expires=1&signature=zzz'));
        $this->assertSame('/spaces/01m7rwbzaxxfdr5bv56yc0b5ae', Scrub::path('/spaces/01m7rwbzaxxfdr5bv56yc0b5ae'));
        $this->assertSame('/embed/abc', Scrub::path('https://app.test/embed/abc?x=1#top'));
    }

    public function test_deep_scrubs_nested_strings(): void
    {
        $this->assertSame(['a' => ['b' => 'mail [email]']], Scrub::deep(['a' => ['b' => 'mail x@y.com']]));
    }

    public function test_a_query_exception_is_logged_without_its_sql_bindings(): void
    {
        $sql = 'insert into "users" ("email", "password") values (?, ?)';
        $exception = new QueryException('pgsql', $sql, ['victim@example.com', '$2y$12$'.str_repeat('x', 53)], new PDOException('SQLSTATE[23505]: Unique violation: duplicate key value (victim@example.com)'));

        $json = (new FiveWFormatter())->format(new LogRecord(new DateTimeImmutable(), 'test', Level::Error, 'failed', ['exception' => $exception]));

        $this->assertStringNotContainsString('victim@example.com', $json);
        $this->assertStringNotContainsString('$2y$', $json);
        $this->assertStringNotContainsString('insert into', $json);
        $this->assertStringContainsString('SQLSTATE[23505]', $json);
    }

    public function test_the_access_log_never_contains_a_reset_token_in_path_or_referer(): void
    {
        $token = str_repeat('c', 64);
        $logged = [];
        \Illuminate\Support\Facades\Log::swap(new class ($logged) {
            public function __construct(public array &$lines)
            {
            }

            public function log(string $level, string $message, array $context = []): void
            {
                $this->lines[] = $context;
            }

            public function __call(string $name, array $arguments): void
            {
            }
        });

        $this->withHeader('Referer', "https://app.test/reset-password/$token?email=a@b.com")->get("/reset-password/$token?email=a@b.com");

        $this->assertNotEmpty($logged);
        $this->assertStringNotContainsString($token, (string) json_encode($logged));
        $this->assertStringNotContainsString('a@b.com', (string) json_encode($logged));
    }
}
