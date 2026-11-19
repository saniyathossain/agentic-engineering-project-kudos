<?php

declare(strict_types=1);

namespace App\Http\Resources;

use App\Models\Space;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;
use Illuminate\Support\Facades\Storage;

/** @mixin Space */
final class EmbedSpaceResource extends JsonResource
{
    /** @return array<string, mixed> */
    public function toArray(Request $request): array
    {
        return [
            'public_id' => $this->public_id,
            'name' => $this->name,
            'theme' => $this->theme->value,
            'logo_url' => $this->logo_path === null
                ? null
                : Storage::disk('public')->url($this->logo_path),
        ];
    }
}
