<?php

declare(strict_types=1);

namespace App\Data\Spaces;

final readonly class FieldConfigData
{
    public function __construct(
        public bool $enabled,
        public bool $required,
    ) {
    }

    /** @param array{enabled?: bool, required?: bool} $raw */
    public static function fromArray(array $raw): self
    {
        $enabled = (bool) ($raw['enabled'] ?? false);

        return new self($enabled, $enabled && (bool) ($raw['required'] ?? false));
    }

    /** @return array{enabled: bool, required: bool} */
    public function toArray(): array
    {
        return ['enabled' => $this->enabled, 'required' => $this->required];
    }
}
