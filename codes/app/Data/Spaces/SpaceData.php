<?php

declare(strict_types=1);

namespace App\Data\Spaces;

use App\Enums\OptionalField;
use App\Enums\SpaceTheme;
use Illuminate\Http\UploadedFile;

final readonly class SpaceData
{
    /** @param array<string, FieldConfigData> $fields keyed by OptionalField value */
    public function __construct(
        public string $name,
        public string $headerTitle,
        public string $message,
        public bool $collectRating,
        public SpaceTheme $theme,
        public array $fields,
        public bool $isAccepting,
        public ?UploadedFile $logo = null,
    ) {
    }

    /** @param array<string, mixed> $validated */
    public static function fromValidated(array $validated, ?UploadedFile $logo): self
    {
        $fields = [];
        foreach (OptionalField::cases() as $field) {
            /** @var array{enabled?: bool, required?: bool} $raw */
            $raw = $validated['fields'][$field->value] ?? [];
            $fields[$field->value] = FieldConfigData::fromArray($raw);
        }

        return new self(
            name: (string) $validated['name'],
            headerTitle: (string) $validated['header_title'],
            message: (string) $validated['message'],
            collectRating: (bool) ($validated['collect_rating'] ?? false),
            theme: SpaceTheme::from((string) $validated['theme']),
            fields: $fields,
            isAccepting: (bool) ($validated['is_accepting'] ?? true),
            logo: $logo,
        );
    }

    /** @return array<string, array{enabled: bool, required: bool}> */
    public function fieldsAsArray(): array
    {
        return array_map(static fn (FieldConfigData $c): array => $c->toArray(), $this->fields);
    }
}
