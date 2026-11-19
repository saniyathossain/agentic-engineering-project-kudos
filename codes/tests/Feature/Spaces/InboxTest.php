<?php

declare(strict_types=1);

namespace Tests\Feature\Spaces;

use App\Enums\TestimonialStatus;
use App\Models\Space;
use App\Models\Testimonial;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

final class InboxTest extends TestCase
{
    use RefreshDatabase;

    private User $owner;

    private Space $space;

    protected function setUp(): void
    {
        parent::setUp();
        $this->owner = User::factory()->create();
        $this->space = Space::factory()->for($this->owner, 'owner')->create();
    }

    public function test_inbox_filters_by_status_and_favorite(): void
    {
        Testimonial::factory()->for($this->space)->create();
        Testimonial::factory()->for($this->space)->published()->create();
        Testimonial::factory()->for($this->space)->create(['is_favorite' => true]);

        $this->actingAs($this->owner)->get("/spaces/{$this->space->public_id}?filter=published")
            ->assertInertia(fn ($p) => $p->has('testimonials.data', 1)->where('counts.all', 3)->where('counts.favorite', 1));
        $this->actingAs($this->owner)->get("/spaces/{$this->space->public_id}?filter=favorite")
            ->assertInertia(fn ($p) => $p->has('testimonials.data', 1));
        $this->actingAs($this->owner)->get("/spaces/{$this->space->public_id}")
            ->assertInertia(fn ($p) => $p->has('testimonials.data', 3));
    }

    public function test_owner_publishes_hides_favorites_edits_and_deletes(): void
    {
        $testimonial = Testimonial::factory()->for($this->space)->create();
        $base = "/testimonials/{$testimonial->public_id}";

        $this->actingAs($this->owner)->patch("$base/status", ['status' => 'published'])->assertRedirect();
        $this->assertSame(TestimonialStatus::Published, $testimonial->refresh()->status);

        $this->actingAs($this->owner)->patch("$base/status", ['status' => 'hidden'])->assertRedirect();
        $this->assertSame(TestimonialStatus::Hidden, $testimonial->refresh()->status);

        $this->actingAs($this->owner)->patch("$base/favorite")->assertRedirect();
        $this->assertTrue($testimonial->refresh()->is_favorite);

        $this->actingAs($this->owner)->patch($base, ['body' => 'Edited <b>text</b>'])->assertRedirect();
        $this->assertSame('Edited text', $testimonial->refresh()->body);

        $this->actingAs($this->owner)->delete($base)->assertRedirect();
        $this->assertModelMissing($testimonial);
    }

    public function test_status_must_be_a_known_value(): void
    {
        $testimonial = Testimonial::factory()->for($this->space)->create();

        $this->actingAs($this->owner)->patch("/testimonials/{$testimonial->public_id}/status", ['status' => 'bogus'])
            ->assertSessionHasErrors('status');
    }

    public function test_other_owners_cannot_touch_testimonials(): void
    {
        $testimonial = Testimonial::factory()->for($this->space)->create();
        $intruder = User::factory()->create();
        $base = "/testimonials/{$testimonial->public_id}";

        $this->actingAs($intruder)->patch("$base/status", ['status' => 'published'])->assertForbidden();
        $this->actingAs($intruder)->patch("$base/favorite")->assertForbidden();
        $this->actingAs($intruder)->patch($base, ['body' => 'hacked'])->assertForbidden();
        $this->actingAs($intruder)->delete($base)->assertForbidden();
        $this->assertSame(TestimonialStatus::Pending, $testimonial->refresh()->status);
    }

    public function test_inbox_filters_by_date_range_inclusive(): void
    {
        Testimonial::factory()->for($this->space)->create(['submitted_at' => '2026-11-01 09:00:00']);
        Testimonial::factory()->for($this->space)->create(['submitted_at' => '2026-11-10 23:30:00']);
        Testimonial::factory()->for($this->space)->create(['submitted_at' => '2026-11-20 08:00:00']);
        $url = "/spaces/{$this->space->public_id}";

        $this->actingAs($this->owner)->get("$url?from=2026-11-05&to=2026-11-10")
            ->assertInertia(fn ($p) => $p->has('testimonials.data', 1)->where('range.from', '2026-11-05')->where('range.to', '2026-11-10'));
        $this->actingAs($this->owner)->get("$url?from=2026-11-10")
            ->assertInertia(fn ($p) => $p->has('testimonials.data', 2));
        $this->actingAs($this->owner)->get("$url?to=2026-11-01")
            ->assertInertia(fn ($p) => $p->has('testimonials.data', 1));
    }

    public function test_invalid_date_range_is_rejected(): void
    {
        $url = "/spaces/{$this->space->public_id}";

        $this->actingAs($this->owner)->get("$url?from=not-a-date")->assertSessionHasErrors('from');
        $this->actingAs($this->owner)->get("$url?from=2026-11-10&to=2026-11-01")->assertSessionHasErrors('to');
    }
}
