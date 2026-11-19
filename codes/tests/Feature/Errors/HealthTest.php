<?php

declare(strict_types=1);

namespace Tests\Feature\Errors;

use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\Support\BreaksDatabase;
use Tests\TestCase;

final class HealthTest extends TestCase
{
    use BreaksDatabase;
    use RefreshDatabase;

    public function test_livez_is_always_ok_and_uncached(): void
    {
        $this->getJson('/livez')->assertOk()->assertJson(['status' => 'ok']);
    }

    public function test_readyz_reports_each_check_when_healthy(): void
    {
        $this->getJson('/readyz')->assertOk()->assertJson(['status' => 'ok'])
            ->assertJsonFragment(['name' => 'database', 'up' => true, 'critical' => true]);
    }

    public function test_readyz_is_503_with_retry_after_when_the_database_is_down(): void
    {
        $response = $this->withBrokenDatabase(fn () => $this->getJson('/readyz'));

        $response->assertStatus(503)->assertHeader('Retry-After', '5')
            ->assertJsonFragment(['name' => 'database', 'up' => false, 'critical' => true])
            ->assertJson(['status' => 'unavailable']);
    }

    public function test_probes_have_no_session_so_they_survive_a_database_outage(): void
    {
        $response = $this->withBrokenDatabase(fn () => $this->getJson('/livez'));

        $response->assertOk()->assertCookieMissing((string) config('session.cookie'));
    }
}
