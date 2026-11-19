<?php

declare(strict_types=1);

namespace App\Data\Dashboard;

use App\Enums\DateRange;
use App\Enums\Plan;

final readonly class DashboardStatsData
{
    /** @param list<DailyCountData> $series */
    public function __construct(
        public int $totalSpaces,
        public int $totalTestimonials,
        public int $uniqueRespondents,
        public int $collectedInRange,
        public Plan $plan,
        public int $spacesUsed,
        public ?int $maxSpaces,
        public ?int $maxTestimonialsPerSpace,
        public DateRange $range,
        public array $series,
        public bool $showUpgradeBanner,
    ) {
    }

    /** @return array<string, mixed> */
    public function toArray(): array
    {
        return [
            'total_spaces' => $this->totalSpaces,
            'total_testimonials' => $this->totalTestimonials,
            'unique_respondents' => $this->uniqueRespondents,
            'collected_in_range' => $this->collectedInRange,
            'plan' => ['value' => $this->plan->value, 'label' => $this->plan->label()],
            'usage' => [
                'spaces_used' => $this->spacesUsed,
                'max_spaces' => $this->maxSpaces,
                'max_testimonials_per_space' => $this->maxTestimonialsPerSpace,
            ],
            'range' => $this->range->value,
            'series' => array_map(static fn (DailyCountData $d): array => $d->toArray(), $this->series),
            'show_upgrade_banner' => $this->showUpgradeBanner,
        ];
    }
}
