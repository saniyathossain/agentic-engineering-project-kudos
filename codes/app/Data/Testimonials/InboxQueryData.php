<?php

declare(strict_types=1);

namespace App\Data\Testimonials;

use App\Enums\InboxFilter;
use Illuminate\Support\Carbon;

final readonly class InboxQueryData
{
    public function __construct(
        public InboxFilter $filter,
        public ?Carbon $from,
        public ?Carbon $to,
    ) {
    }

    /** @param array<string, mixed> $validated */
    public static function fromValidated(array $validated): self
    {
        return new self(
            filter: InboxFilter::tryFrom((string) ($validated['filter'] ?? '')) ?? InboxFilter::All,
            from: self::day($validated['from'] ?? null)?->startOfDay(),
            to: self::day($validated['to'] ?? null)?->endOfDay(),
        );
    }

    private static function day(mixed $value): ?Carbon
    {
        return is_string($value) && $value !== '' ? Carbon::parse($value, 'UTC') : null;
    }
}
