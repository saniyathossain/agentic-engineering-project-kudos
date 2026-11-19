<?php

declare(strict_types=1);

namespace Tests\Feature\Spaces;

use App\Models\Space;
use App\Models\Testimonial;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Storage;
use Tests\TestCase;

final class SpaceCrudTest extends TestCase
{
    use RefreshDatabase;

    /** @return array<string, mixed> */
    private function payload(array $overrides = []): array
    {
        return array_replace_recursive([
            'name' => 'Agentic Engineering Course',
            'header_title' => 'Would you recommend the course?',
            'message' => 'Write your **experience**.',
            'collect_rating' => true,
            'theme' => 'brand',
            'is_accepting' => true,
            'fields' => [
                'company' => ['enabled' => true, 'required' => true],
                'title' => ['enabled' => false, 'required' => true],
            ],
        ], $overrides);
    }

    public function test_guests_cannot_manage_spaces(): void
    {
        $this->get('/spaces')->assertRedirect('/login');
        $this->post('/spaces', $this->payload())->assertRedirect('/login');
    }

    public function test_owner_creates_space_with_generated_unique_slug_and_field_config(): void
    {
        Storage::fake('public');
        $user = User::factory()->create();

        $this->actingAs($user)->post('/spaces', $this->payload(['logo' => UploadedFile::fake()->image('logo.png')]))
            ->assertRedirect();

        $space = Space::query()->firstOrFail();
        $this->assertSame('agentic-engineering-course', $space->slug);
        $this->assertSame($user->id, $space->user_id);
        $this->assertTrue($space->fields['company']['required']);
        $this->assertFalse($space->fields['title']['required'], 'disabled fields can never be required');
        $this->assertNotNull($space->logo_path);
        Storage::disk('public')->assertExists((string) $space->logo_path);
    }

    public function test_free_plan_is_limited_to_one_space(): void
    {
        $user = User::factory()->create();
        Space::factory()->for($user, 'owner')->create();

        $this->actingAs($user)->post('/spaces', $this->payload())->assertRedirect('/billing');

        $this->assertSame(1, Space::query()->count());
    }

    public function test_slug_never_collides_with_reserved_routes(): void
    {
        $user = User::factory()->create();

        $this->actingAs($user)->post('/spaces', $this->payload(['name' => 'Dashboard']))->assertRedirect();

        $this->assertSame('dashboard-2', Space::query()->firstOrFail()->slug);
    }

    public function test_validation_rejects_bad_input(): void
    {
        $this->actingAs(User::factory()->create())
            ->post('/spaces', $this->payload(['theme' => 'neon', 'name' => '']))
            ->assertSessionHasErrors(['theme', 'name']);
    }

    public function test_owner_updates_but_slug_is_stable(): void
    {
        $user = User::factory()->create();
        $space = Space::factory()->for($user, 'owner')->create(['slug' => 'keep-me']);

        $this->actingAs($user)->put("/spaces/{$space->public_id}", $this->payload(['name' => 'Renamed']))->assertRedirect();

        $space->refresh();
        $this->assertSame('Renamed', $space->name);
        $this->assertSame('keep-me', $space->slug);
    }

    public function test_other_users_cannot_view_edit_update_or_delete(): void
    {
        $space = Space::factory()->create();
        $intruder = User::factory()->create();

        $this->actingAs($intruder)->get("/spaces/{$space->public_id}")->assertForbidden();
        $this->actingAs($intruder)->get("/spaces/{$space->public_id}/edit")->assertForbidden();
        $this->actingAs($intruder)->put("/spaces/{$space->public_id}", $this->payload())->assertForbidden();
        $this->actingAs($intruder)->delete("/spaces/{$space->public_id}")->assertForbidden();
    }

    public function test_deleting_a_space_cascades_to_testimonials(): void
    {
        $user = User::factory()->create();
        $space = Space::factory()->for($user, 'owner')->create();
        Testimonial::factory()->for($space)->count(2)->create();

        $this->actingAs($user)->delete("/spaces/{$space->public_id}")->assertRedirect('/spaces');

        $this->assertSame(0, Space::query()->count());
        $this->assertSame(0, Testimonial::query()->count());
    }

    public function test_index_lists_only_own_spaces(): void
    {
        $user = User::factory()->create();
        Space::factory()->for($user, 'owner')->create(['name' => 'Mine']);
        Space::factory()->create(['name' => 'Theirs']);

        $this->actingAs($user)->get('/spaces')->assertInertia(
            fn ($page) => $page->component('spaces/index')->has('spaces', 1)->where('spaces.0.name', 'Mine'),
        );
    }
}
