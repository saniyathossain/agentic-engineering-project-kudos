<?php

declare(strict_types=1);

namespace App\Actions\Spaces;

use App\Models\Space;
use App\Services\PublicFileStorage;

final readonly class DeleteSpace
{
    public function __construct(private PublicFileStorage $files)
    {
    }

    public function handle(Space $space): void
    {
        $this->files->delete($space->logo_path);
        $space->testimonials()->pluck('photo_path')->each(
            fn (?string $path) => $this->files->delete($path),
        );
        $space->delete();
    }
}
