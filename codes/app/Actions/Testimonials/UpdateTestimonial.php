<?php

declare(strict_types=1);

namespace App\Actions\Testimonials;

use App\Enums\TestimonialStatus;
use App\Models\Testimonial;

final class UpdateTestimonial
{
    public function editBody(Testimonial $testimonial, string $body): Testimonial
    {
        $testimonial->body = strip_tags($body);
        $testimonial->save();

        return $testimonial;
    }

    public function setStatus(Testimonial $testimonial, TestimonialStatus $status): Testimonial
    {
        $testimonial->status = $status;
        $testimonial->save();

        return $testimonial;
    }

    public function toggleFavorite(Testimonial $testimonial): Testimonial
    {
        $testimonial->is_favorite = ! $testimonial->is_favorite;
        $testimonial->save();

        return $testimonial;
    }
}
