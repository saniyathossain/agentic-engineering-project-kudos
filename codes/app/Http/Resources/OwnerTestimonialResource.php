<?php

declare(strict_types=1);

namespace App\Http\Resources;

use App\Models\Testimonial;
use App\Services\PublicFileStorage;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

/** Owner-facing testimonial: includes the respondent email (never use for public output). @mixin Testimonial */
final class OwnerTestimonialResource extends JsonResource
{
    /** @return array<string, mixed> */
    public function toArray(Request $request): array
    {
        /** @var Testimonial $t */
        $t = $this->resource;

        return [
            'public_id' => $t->public_id,
            'rating' => $t->rating,
            'body' => $t->body,
            'respondent_name' => $t->respondent_name,
            'respondent_email' => $t->respondent_email,
            'company' => $t->company,
            'title' => $t->title,
            'social_link' => $t->social_link,
            'photo_url' => app(PublicFileStorage::class)->url($t->photo_path),
            'status' => $t->status->value,
            'is_favorite' => $t->is_favorite,
            'submitted_at' => $t->submitted_at->toIso8601String(),
        ];
    }
}
