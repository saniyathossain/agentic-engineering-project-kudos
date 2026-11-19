<?php

declare(strict_types=1);

namespace Tests\Feature\Embed;

use App\Enums\SpaceTheme;
use App\Models\Space;
use App\Models\Testimonial;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Inertia\Testing\AssertableInertia as Assert;
use Tests\TestCase;

final class EmbedWallTest extends TestCase
{
    use RefreshDatabase;

    public function test_wall_lists_only_published_testimonials(): void
    {
        $space = Space::factory()->create(['theme' => SpaceTheme::Dark]);
        Testimonial::factory()->for($space)->published()->create(['body' => 'Loved it']);
        Testimonial::factory()->for($space)->create(['body' => 'Still pending']);
        Testimonial::factory()->for($space)->create(['body' => 'Hidden one', 'status' => 'hidden']);
        Testimonial::factory()->published()->create(['body' => 'Other space']);

        $this->get("/embed/{$space->public_id}")
            ->assertOk()
            ->assertInertia(fn (Assert $page) => $page
                ->component('embed/wall')
                ->where('space.theme', 'dark')
                ->has('testimonials', 1)
                ->where('testimonials.0.body', 'Loved it'));
    }

    public function test_wall_is_public_and_never_exposes_respondent_email(): void
    {
        $space = Space::factory()->create();
        Testimonial::factory()->for($space)->published()->create(['respondent_email' => 'secret@example.test']);

        $response = $this->get("/embed/{$space->public_id}")->assertOk();

        $this->assertStringNotContainsString('secret@example.test', (string) $response->getContent());
        $this->assertStringNotContainsString('respondent_email', (string) $response->getContent());
    }

    public function test_wall_allows_framing(): void
    {
        $space = Space::factory()->create();

        $response = $this->withHeaders([])->get("/embed/{$space->public_id}")->assertOk();

        $this->assertFalse($response->headers->has('X-Frame-Options'));
        $this->assertSame('frame-ancestors *', $response->headers->get('Content-Security-Policy'));
    }

    public function test_unknown_space_returns_404(): void
    {
        $this->get('/embed/01HZZZZZZZZZZZZZZZZZZZZZZZ')->assertNotFound();
        $this->getJson('/embed/01HZZZZZZZZZZZZZZZZZZZZZZZ/testimonials.json')->assertNotFound();
    }

    public function test_json_feed_has_only_published_and_no_email(): void
    {
        $space = Space::factory()->create();
        Testimonial::factory()->for($space)->published()->create([
            'respondent_email' => 'secret@example.test',
            'photo_path' => 'photos/a.jpg',
        ]);
        Testimonial::factory()->for($space)->create();

        $response = $this->getJson("/embed/{$space->public_id}/testimonials.json")
            ->assertOk()
            ->assertJsonCount(1, 'data')
            ->assertJsonPath('space.public_id', $space->public_id);

        $this->assertStringNotContainsString('secret@example.test', (string) $response->getContent());
        $this->assertStringNotContainsString('respondent_email', (string) $response->getContent());
        $this->assertStringEndsWith('/storage/photos/a.jpg', (string) $response->json('data.0.photo_url'));
        $this->assertSame('frame-ancestors *', $response->headers->get('Content-Security-Policy'));
    }
}
