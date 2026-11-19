<?php

declare(strict_types=1);

namespace Database\Factories;

use App\Enums\TestimonialStatus;
use App\Models\Space;
use App\Models\Testimonial;
use Illuminate\Database\Eloquent\Factories\Factory;

/** @extends Factory<Testimonial> */
final class TestimonialFactory extends Factory
{
    protected $model = Testimonial::class;

    /** @return array<string, mixed> */
    public function definition(): array
    {
        return [
            'space_id' => Space::factory(),
            'rating' => fake()->numberBetween(3, 5),
            'body' => fake()->paragraph(),
            'respondent_name' => fake()->name(),
            'respondent_email' => fake()->unique()->safeEmail(),
            'consent' => true,
            'status' => TestimonialStatus::Pending,
            'is_favorite' => false,
            'submitted_at' => now(),
        ];
    }

    public function published(): self
    {
        return $this->state(['status' => TestimonialStatus::Published]);
    }
}
