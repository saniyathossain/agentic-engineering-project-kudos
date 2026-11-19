<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Models\Space;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

final class SecurityHeadersTest extends TestCase
{
    use RefreshDatabase;

    public function test_baseline_headers_are_always_sent(): void
    {
        $this->get('/login')->assertHeader('Permissions-Policy')->assertHeader('Cross-Origin-Opener-Policy', 'same-origin');
    }

    public function test_csp_is_off_unless_enabled(): void
    {
        $this->get('/login')->assertHeaderMissing('Content-Security-Policy');
    }

    public function test_csp_uses_a_per_request_nonce_that_matches_the_inline_scripts(): void
    {
        config(['security.csp.enabled' => true]);

        $first = $this->get('/login');
        $policy = (string) $first->headers->get('Content-Security-Policy');

        $this->assertMatchesRegularExpression("/script-src 'self' 'nonce-([A-Za-z0-9+\\/=_-]+)'/", $policy);
        preg_match("/'nonce-([^']+)'/", $policy, $match);
        $first->assertSee('nonce="'.$match[1].'"', false);
        $this->assertStringContainsString("frame-ancestors 'self'", $policy);
        $this->assertStringContainsString("object-src 'none'", $policy);
        $this->assertStringNotContainsString("'unsafe-eval'", $policy);

        $second = (string) $this->get('/login')->headers->get('Content-Security-Policy');
        $this->assertNotSame($policy, $second, 'a new nonce for every request');
    }

    public function test_only_embed_pages_may_be_framed_by_other_sites(): void
    {
        config(['security.csp.enabled' => true]);
        $space = Space::factory()->create();

        $embed = (string) $this->get("/embed/{$space->public_id}")->assertOk()->headers->get('Content-Security-Policy');
        $page = (string) $this->get('/login')->headers->get('Content-Security-Policy');

        $this->assertStringContainsString('frame-ancestors *', $embed);
        $this->assertStringContainsString("script-src 'self' 'nonce-", $embed, 'the embed page keeps the full policy, not just frame-ancestors');
        $this->assertStringContainsString("frame-ancestors 'self'", $page);
    }

    public function test_report_only_mode_changes_the_header_name(): void
    {
        config(['security.csp.enabled' => true, 'security.csp.report_only' => true]);

        $this->get('/login')->assertHeader('Content-Security-Policy-Report-Only')->assertHeaderMissing('Content-Security-Policy');
    }

    public function test_hsts_only_over_https(): void
    {
        $this->get('/login')->assertHeaderMissing('Strict-Transport-Security');
        $this->get('https://localhost/login')->assertHeader('Strict-Transport-Security');
    }
}
