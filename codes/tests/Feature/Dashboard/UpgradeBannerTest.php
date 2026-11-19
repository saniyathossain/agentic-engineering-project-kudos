<?php

declare(strict_types=1);

namespace Tests\Feature\Dashboard;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Inertia\Testing\AssertableInertia as Assert;
use Tests\TestCase;

final class UpgradeBannerTest extends TestCase
{
    use RefreshDatabase;

    public function test_free_user_sees_banner_until_dismissed(): void
    {
        $user = User::factory()->create();

        $this->actingAs($user)->get('/dashboard')
            ->assertInertia(fn (Assert $page) => $page->where('stats.show_upgrade_banner', true));

        $this->actingAs($user)->post('/dashboard/banner/dismiss')->assertRedirect();

        $this->assertNotNull($user->fresh()?->banner_dismissed_at);
        $this->actingAs($user)->get('/dashboard')
            ->assertInertia(fn (Assert $page) => $page->where('stats.show_upgrade_banner', false));
    }

    public function test_guests_cannot_dismiss(): void
    {
        $this->post('/dashboard/banner/dismiss')->assertRedirect('/login');
    }
}
