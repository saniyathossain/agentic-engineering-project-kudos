<?php

declare(strict_types=1);

namespace Tests\Feature\Dashboard;

use App\Models\Space;
use App\Models\Testimonial;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Inertia\Testing\AssertableInertia as Assert;
use Tests\TestCase;

final class DashboardStatsTest extends TestCase
{
    use RefreshDatabase;

    public function test_stats_only_count_the_owners_data(): void
    {
        $owner = User::factory()->create();
        $space = Space::factory()->for($owner, 'owner')->create();
        Testimonial::factory()->for($space)->count(2)->create(['respondent_email' => 'a@x.test']);
        Testimonial::factory()->for($space)->create(['respondent_email' => 'b@x.test']);

        $stranger = Space::factory()->create();
        Testimonial::factory()->for($stranger)->count(5)->create();

        $this->actingAs($owner)->get('/dashboard')
            ->assertOk()
            ->assertInertia(fn (Assert $page) => $page
                ->component('dashboard')
                ->where('stats.total_spaces', 1)
                ->where('stats.total_testimonials', 3)
                ->where('stats.unique_respondents', 2)
                ->where('stats.collected_in_range', 3)
                ->where('stats.plan.value', 'free')
                ->where('stats.usage.spaces_used', 1)
                ->where('stats.usage.max_spaces', 1)
                ->where('stats.usage.max_testimonials_per_space', 10));
    }

    public function test_series_is_zero_filled_for_each_range(): void
    {
        $owner = User::factory()->create();
        $space = Space::factory()->for($owner, 'owner')->create();
        Testimonial::factory()->for($space)->create(['submitted_at' => now('UTC')->subDays(2)]);
        Testimonial::factory()->for($space)->create(['submitted_at' => now('UTC')->subDays(40)]);

        foreach ([7, 30, 90] as $range) {
            $this->actingAs($owner)->get("/dashboard?range={$range}")
                ->assertInertia(fn (Assert $page) => $page
                    ->where('stats.range', $range)
                    ->has('stats.series', $range)
                    ->where('stats.series.'.($range - 3).'.count', 1)
                    ->where('stats.series.'.($range - 1).'.count', 0)
                    ->where('stats.collected_in_range', $range === 90 ? 2 : 1));
        }
    }

    public function test_range_defaults_to_30_and_rejects_invalid_values(): void
    {
        $owner = User::factory()->create();

        $this->actingAs($owner)->get('/dashboard')
            ->assertInertia(fn (Assert $page) => $page->has('stats.series', 30));

        $this->actingAs($owner)->get('/dashboard?range=12')->assertSessionHasErrors('range');
    }
}
