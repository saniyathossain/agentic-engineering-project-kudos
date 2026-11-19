<?php

declare(strict_types=1);

namespace App\Actions\Dashboard;

use App\Data\Dashboard\DailyCountData;
use App\Data\Dashboard\DashboardStatsData;
use App\Enums\DateRange;
use App\Enums\Plan;
use App\Models\Testimonial;
use App\Models\User;
use App\Services\PlanResolver;
use Carbon\CarbonImmutable;
use Illuminate\Database\Eloquent\Builder;

final class BuildDashboardStats
{
    public function __construct(private readonly PlanResolver $plans)
    {
    }

    public function handle(User $user, DateRange $range): DashboardStatsData
    {
        $plan = $this->plans->for($user);
        $series = $this->series($user, $range);
        $spacesUsed = $user->spaces()->count();

        return new DashboardStatsData(
            totalSpaces: $spacesUsed,
            totalTestimonials: $this->ownedTestimonials($user)->count(),
            uniqueRespondents: $this->uniqueRespondents($user),
            collectedInRange: array_sum(array_map(static fn (DailyCountData $d): int => $d->count, $series)),
            plan: $plan,
            spacesUsed: $spacesUsed,
            maxSpaces: $plan->maxSpaces(),
            maxTestimonialsPerSpace: $plan->maxTestimonialsPerSpace(),
            range: $range,
            series: $series,
            showUpgradeBanner: $plan === Plan::Free && $user->banner_dismissed_at === null,
        );
    }

    /** @return Builder<Testimonial> */
    private function ownedTestimonials(User $user): Builder
    {
        return Testimonial::query()->whereIn('space_id', $user->spaces()->select('id'));
    }

    private function uniqueRespondents(User $user): int
    {
        return (int) $this->ownedTestimonials($user)
            ->selectRaw('COUNT(DISTINCT LOWER(respondent_email)) as total')
            ->value('total');
    }

    /** @return list<DailyCountData> */
    private function series(User $user, DateRange $range): array
    {
        $today = CarbonImmutable::now('UTC')->startOfDay();
        $start = $today->subDays($range->value - 1);

        $counts = $this->ownedTestimonials($user)
            ->where('submitted_at', '>=', $start)
            ->where('submitted_at', '<', $today->addDay())
            ->selectRaw('DATE(submitted_at) as day, COUNT(*) as total')
            ->groupByRaw('DATE(submitted_at)')
            ->pluck('total', 'day');

        $series = [];
        for ($i = 0; $i < $range->value; $i++) {
            $date = $start->addDays($i)->toDateString();
            $series[] = new DailyCountData($date, (int) ($counts[$date] ?? 0));
        }

        return $series;
    }
}
