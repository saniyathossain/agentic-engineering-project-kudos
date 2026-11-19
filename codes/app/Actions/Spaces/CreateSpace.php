<?php

declare(strict_types=1);

namespace App\Actions\Spaces;

use App\Data\Spaces\SpaceData;
use App\Exceptions\PlanLimitReached;
use App\Models\Space;
use App\Models\User;
use App\Services\PlanResolver;
use App\Services\PublicFileStorage;
use App\Services\SlugGenerator;

final readonly class CreateSpace
{
    public function __construct(
        private PlanResolver $plans,
        private SlugGenerator $slugs,
        private PublicFileStorage $files,
    ) {
    }

    public function handle(User $owner, SpaceData $data): Space
    {
        if (! $this->plans->canCreateSpace($owner)) {
            throw PlanLimitReached::spaces();
        }

        $space = new Space([
            'name' => $data->name,
            'slug' => $this->slugs->unique($data->name),
            'header_title' => $data->headerTitle,
            'message' => $data->message,
            'collect_rating' => $data->collectRating,
            'theme' => $data->theme,
            'fields' => $data->fieldsAsArray(),
            'is_accepting' => $data->isAccepting,
            'logo_path' => $data->logo === null ? null : $this->files->store($data->logo, 'logos'),
        ]);
        $space->owner()->associate($owner);
        $space->save();

        return $space;
    }
}
