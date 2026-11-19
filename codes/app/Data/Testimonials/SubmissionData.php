<?php

declare(strict_types=1);

namespace App\Data\Testimonials;

use Illuminate\Http\UploadedFile;

final readonly class SubmissionData
{
    public function __construct(
        public string $name,
        public string $email,
        public string $body,
        public ?int $rating,
        public ?string $company,
        public ?string $title,
        public ?string $socialLink,
        public ?UploadedFile $photo,
        public bool $consent,
    ) {
    }

    /** @param array<string, mixed> $validated */
    public static function fromValidated(array $validated, ?UploadedFile $photo): self
    {
        return new self(
            name: (string) $validated['name'],
            email: (string) $validated['email'],
            body: (string) $validated['body'],
            rating: isset($validated['rating']) ? (int) $validated['rating'] : null,
            company: self::nullableString($validated['company'] ?? null),
            title: self::nullableString($validated['title'] ?? null),
            socialLink: self::nullableString($validated['social_link'] ?? null),
            photo: $photo,
            consent: (bool) $validated['consent'],
        );
    }

    private static function nullableString(mixed $value): ?string
    {
        return is_string($value) && $value !== '' ? $value : null;
    }
}
