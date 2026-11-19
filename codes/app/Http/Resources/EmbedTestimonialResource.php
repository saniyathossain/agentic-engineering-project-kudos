<?php

declare(strict_types=1);

namespace App\Http\Resources;

use App\Models\Testimonial;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;
use Illuminate\Support\Facades\Storage;

/** @mixin Testimonial */
final class EmbedTestimonialResource extends JsonResource
{
    /** @return array<string, mixed> */
    public function toArray(Request $request): array
    {
        return [
            'public_id' => $this->public_id,
            'rating' => $this->rating,
            'body' => $this->body,
            'respondent_name' => $this->respondent_name,
            'company' => $this->company,
            'title' => $this->title,
            'social_link' => $this->social_link,
            'photo_url' => $this->photo_path === null
                ? null
                : Storage::disk('public')->url($this->photo_path),
            'submitted_at' => $this->submitted_at->toIso8601String(),
        ];
    }
}
