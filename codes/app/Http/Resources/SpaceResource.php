<?php

declare(strict_types=1);

namespace App\Http\Resources;

use App\Models\Space;
use App\Services\PublicFileStorage;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

/** @mixin Space */
final class SpaceResource extends JsonResource
{
    /** @return array<string, mixed> */
    public function toArray(Request $request): array
    {
        /** @var Space $space */
        $space = $this->resource;

        return [
            'public_id' => $space->public_id,
            'name' => $space->name,
            'slug' => $space->slug,
            'logo_url' => app(PublicFileStorage::class)->url($space->logo_path),
            'header_title' => $space->header_title,
            'message' => $space->message,
            'collect_rating' => $space->collect_rating,
            'theme' => $space->theme->value,
            'fields' => $space->fields,
            'is_accepting' => $space->is_accepting,
            'testimonials_count' => $this->whenCounted('testimonials'),
        ];
    }
}
