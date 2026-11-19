<?php

declare(strict_types=1);

namespace App\Actions\Spaces;

use App\Data\Spaces\SpaceData;
use App\Models\Space;
use App\Services\PublicFileStorage;

final readonly class UpdateSpace
{
    public function __construct(private PublicFileStorage $files)
    {
    }

    /** The slug is stable after creation so shared links keep working. */
    public function handle(Space $space, SpaceData $data): Space
    {
        $space->fill([
            'name' => $data->name,
            'header_title' => $data->headerTitle,
            'message' => $data->message,
            'collect_rating' => $data->collectRating,
            'theme' => $data->theme,
            'fields' => $data->fieldsAsArray(),
            'is_accepting' => $data->isAccepting,
        ]);

        if ($data->logo !== null) {
            $space->logo_path = $this->files->replace($space->logo_path, $data->logo, 'logos');
        }

        $space->save();

        return $space;
    }
}
