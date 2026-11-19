<?php

declare(strict_types=1);

namespace App\Actions\Testimonials;

use App\Models\Testimonial;
use App\Services\PublicFileStorage;

final readonly class DeleteTestimonial
{
    public function __construct(private PublicFileStorage $files)
    {
    }

    public function handle(Testimonial $testimonial): void
    {
        $this->files->delete($testimonial->photo_path);
        $testimonial->delete();
    }
}
