<?php

declare(strict_types=1);

namespace App\Http\Middleware;

use App\Services\PlanResolver;
use Illuminate\Foundation\Inspiring;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
use Inertia\Middleware;
use Throwable;

final class HandleInertiaRequests extends Middleware
{
    /**
     * The root template that's loaded on the first page visit.
     *
     * @see https://inertiajs.com/server-side-setup#root-template
     *
     * @var string
     */
    protected $rootView = 'app';

    /**
     * Determines the current asset version.
     *
     * @see https://inertiajs.com/asset-versioning
     */
    public function version(Request $request): ?string
    {
        return parent::version($request);
    }

    /**
     * Define the props that are shared by default.
     *
     * @see https://inertiajs.com/shared-data
     *
     * @return array<string, mixed>
     */
    public function share(Request $request): array
    {
        [$message, $author] = str(Inspiring::quotes()->random())->explode('-');

        return array_merge(parent::share($request), [
            ...parent::share($request),
            'name' => config('app.name'),
            'quote' => ['message' => trim($message), 'author' => trim($author)],
            'auth' => [
                'user' => $request->user(),
            ],
            'locale' => app()->getLocale(),
            'resilience' => config('resilience.outage'),
            'plan' => fn (): ?array => $this->planFor($request),
            'flash' => [
                'success' => fn (): ?string => $request->session()->get('success'),
                'error' => fn (): ?string => $request->session()->get('error'),
            ],
        ]);
    }

    /** @return array{value: string, label: string}|null */
    private function planFor(Request $request): ?array
    {
        $user = $request->user();
        if ($user === null) {
            return null;
        }

        try {
            $plan = app(PlanResolver::class)->for($user);
        } catch (Throwable $e) {
            // a flaky dependency must not take the whole page down just to render a badge, but the outage stays visible
            Log::warning('plan badge unavailable', ['event' => 'plan.lookup', 'outcome' => 'degraded', 'reason' => 'dependency_unavailable', 'error' => $e->getMessage()]);

            return null;
        }

        return ['value' => $plan->value, 'label' => $plan->label()];
    }
}
