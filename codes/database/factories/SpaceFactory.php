<?php

declare(strict_types=1);

namespace Database\Factories;

use App\Enums\SpaceTheme;
use App\Models\Space;
use App\Models\User;
use Illuminate\Database\Eloquent\Factories\Factory;
use Illuminate\Support\Str;

/** @extends Factory<Space> */
final class SpaceFactory extends Factory
{
    protected $model = Space::class;

    /** @return array<string, mixed> */
    public function definition(): array
    {
        $name = fake()->unique()->company();

        return [
            'user_id' => User::factory(),
            'name' => $name,
            'slug' => Str::slug($name).'-'.fake()->unique()->numberBetween(1, 99999),
            'header_title' => 'Would you recommend us?',
            'message' => 'Tell us about your **experience**.',
            'collect_rating' => true,
            'theme' => SpaceTheme::Light,
            'fields' => [
                'company' => ['enabled' => false, 'required' => false],
                'title' => ['enabled' => false, 'required' => false],
                'social_link' => ['enabled' => false, 'required' => false],
                'photo' => ['enabled' => false, 'required' => false],
            ],
            'is_accepting' => true,
        ];
    }
}
