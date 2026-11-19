<?php

declare(strict_types=1);

namespace App\Actions\Testimonials;

use App\Data\Testimonials\SubmissionData;
use App\Enums\TestimonialStatus;
use App\Exceptions\PlanLimitReached;
use App\Models\Space;
use App\Models\Testimonial;
use App\Services\PlanResolver;
use App\Services\PublicFileStorage;

final readonly class SubmitTestimonial
{
    public function __construct(
        private PlanResolver $plans,
        private PublicFileStorage $files,
    ) {
    }

    public function handle(Space $space, SubmissionData $data): Testimonial
    {
        if (! $this->plans->acceptsTestimonials($space)) {
            throw PlanLimitReached::testimonials();
        }

        $testimonial = new Testimonial([
            'rating' => $space->collect_rating ? $data->rating : null,
            'body' => strip_tags($data->body),
            'respondent_name' => strip_tags($data->name),
            'respondent_email' => $data->email,
            'company' => $data->company === null ? null : strip_tags($data->company),
            'title' => $data->title === null ? null : strip_tags($data->title),
            'social_link' => $data->socialLink,
            'photo_path' => $data->photo === null ? null : $this->files->store($data->photo, 'photos'),
            'consent' => $data->consent,
            'status' => TestimonialStatus::Pending,
            'is_favorite' => false,
            'submitted_at' => now(),
        ]);
        $testimonial->space()->associate($space);
        $testimonial->save();

        return $testimonial;
    }
}
