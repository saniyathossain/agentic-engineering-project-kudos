<?php

declare(strict_types=1);

namespace Tests\Feature\Public;

use App\Enums\TestimonialStatus;
use App\Models\Space;
use App\Models\Testimonial;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Storage;
use Tests\TestCase;

final class CollectTestimonialTest extends TestCase
{
    use RefreshDatabase;

    /** @return array<string, mixed> */
    private function submission(array $overrides = []): array
    {
        return array_merge([
            'name' => 'Adnan Jamil',
            'email' => 'adnan@example.com',
            'body' => 'It was a good course.',
            'rating' => 4,
            'consent' => true,
        ], $overrides);
    }

    public function test_public_page_renders_without_auth_and_never_leaks_owner_data(): void
    {
        $space = Space::factory()->create(['slug' => 'my-course']);

        $this->get('/my-course')->assertOk()->assertInertia(
            fn ($page) => $page->component('public/collect')->where('space.slug', 'my-course')->where('accepting', true)
                ->missing('space.user_id'),
        );
        $this->assertNotNull($space);
    }

    public function test_unknown_slug_is_404(): void
    {
        $this->get('/nope-nope')->assertNotFound();
    }

    public function test_respondent_submits_testimonial_that_starts_pending(): void
    {
        $space = Space::factory()->create(['slug' => 'my-course']);

        $this->post('/my-course', $this->submission())->assertRedirect()->assertSessionHas('success');

        $testimonial = Testimonial::query()->firstOrFail();
        $this->assertSame($space->id, $testimonial->space_id);
        $this->assertSame(TestimonialStatus::Pending, $testimonial->status);
        $this->assertSame('adnan@example.com', $testimonial->respondent_email);
    }

    public function test_consent_is_required(): void
    {
        Space::factory()->create(['slug' => 'my-course']);

        $this->post('/my-course', $this->submission(['consent' => false]))->assertSessionHasErrors('consent');
        $this->assertSame(0, Testimonial::query()->count());
    }

    public function test_html_is_stripped_from_text(): void
    {
        Space::factory()->create(['slug' => 'my-course']);

        $this->post('/my-course', $this->submission(['body' => 'Great <script>alert(1)</script>course', 'name' => '<b>Eve</b>']));

        $testimonial = Testimonial::query()->firstOrFail();
        $this->assertStringNotContainsString('<script>', $testimonial->body);
        $this->assertSame('Eve', $testimonial->respondent_name);
    }

    public function test_rating_required_only_when_collecting_ratings(): void
    {
        Space::factory()->create(['slug' => 'rated', 'collect_rating' => true]);
        Space::factory()->create(['slug' => 'unrated', 'collect_rating' => false]);

        $this->post('/rated', $this->submission(['rating' => null]))->assertSessionHasErrors('rating');
        $this->post('/unrated', $this->submission(['rating' => null]))->assertSessionDoesntHaveErrors();
        $this->post('/unrated', $this->submission(['rating' => 5]))->assertSessionHasErrors('rating');
    }

    public function test_optional_fields_follow_the_space_configuration(): void
    {
        Storage::fake('public');
        Space::factory()->create(['slug' => 'cfg', 'fields' => [
            'company' => ['enabled' => true, 'required' => true],
            'title' => ['enabled' => false, 'required' => false],
            'social_link' => ['enabled' => true, 'required' => false],
            'photo' => ['enabled' => true, 'required' => false],
        ]]);

        $this->post('/cfg', $this->submission())->assertSessionHasErrors('company');
        $this->post('/cfg', $this->submission(['company' => 'FigLab', 'title' => 'CEO']))->assertSessionHasErrors('title');
        $this->post('/cfg', $this->submission(['company' => 'FigLab', 'social_link' => 'javascript:alert(1)']))->assertSessionHasErrors('social_link');
        $this->post('/cfg', $this->submission([
            'company' => 'FigLab',
            'social_link' => 'https://example.com/me',
            'photo' => UploadedFile::fake()->image('me.jpg'),
        ]))->assertSessionDoesntHaveErrors();

        $testimonial = Testimonial::query()->firstOrFail();
        $this->assertSame('FigLab', $testimonial->company);
        Storage::disk('public')->assertExists((string) $testimonial->photo_path);
    }

    public function test_free_plan_space_stops_accepting_at_ten_testimonials(): void
    {
        $space = Space::factory()->create(['slug' => 'full']);
        Testimonial::factory()->for($space)->count(10)->create();

        $this->get('/full')->assertInertia(fn ($page) => $page->where('accepting', false));
        $this->post('/full', $this->submission())->assertSessionHas('error');
        $this->assertSame(10, Testimonial::query()->count());
    }

    public function test_paused_space_does_not_accept(): void
    {
        Space::factory()->create(['slug' => 'paused', 'is_accepting' => false]);

        $this->post('/paused', $this->submission())->assertSessionHas('error');
        $this->assertSame(0, Testimonial::query()->count());
    }

    public function test_submission_is_rate_limited(): void
    {
        Space::factory()->for(User::factory()->create(), 'owner')->create(['slug' => 'busy']);
        $statuses = [];
        for ($i = 0; $i < 22; $i++) {
            $statuses[] = $this->post('/busy', $this->submission(['email' => "u{$i}@example.com"]))->status();
        }

        $this->assertContains(429, $statuses);
    }
}
