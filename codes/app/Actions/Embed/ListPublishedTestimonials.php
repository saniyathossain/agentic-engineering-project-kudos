<?php

declare(strict_types=1);

namespace App\Actions\Embed;

use App\Models\Space;
use App\Models\Testimonial;
use Illuminate\Database\Eloquent\Collection;

final class ListPublishedTestimonials
{
    /** @return Collection<int, Testimonial> */
    public function handle(Space $space): Collection
    {
        return $space->publishedTestimonials()
            ->select([
                'id', 'public_id', 'space_id', 'rating', 'body', 'respondent_name',
                'company', 'title', 'social_link', 'photo_path', 'status', 'submitted_at',
            ])
            ->orderByDesc('submitted_at')
            ->get();
    }
}
