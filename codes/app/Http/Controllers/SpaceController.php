<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Actions\Spaces\CreateSpace;
use App\Actions\Spaces\DeleteSpace;
use App\Actions\Spaces\UpdateSpace;
use App\Enums\InboxFilter;
use App\Enums\OptionalField;
use App\Enums\SpaceTheme;
use App\Exceptions\PlanLimitReached;
use App\Http\Requests\Spaces\InboxRequest;
use App\Http\Requests\Spaces\SpaceRequest;
use App\Http\Resources\OwnerTestimonialResource;
use App\Http\Resources\SpaceResource;
use App\Models\Space;
use App\Models\User;
use App\Services\PlanResolver;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Gate;
use Inertia\Inertia;
use Inertia\Response;

final class SpaceController extends Controller
{
    public function index(Request $request): Response
    {
        $user = $this->user($request);
        $spaces = $user->spaces()->withCount('testimonials')->latest()->get();

        return Inertia::render('spaces/index', [
            'spaces' => SpaceResource::collection($spaces)->resolve(),
            'canCreate' => app(PlanResolver::class)->canCreateSpace($user),
        ]);
    }

    public function create(Request $request): Response|RedirectResponse
    {
        if (! app(PlanResolver::class)->canCreateSpace($this->user($request))) {
            return to_route('billing.show')->with('error', PlanLimitReached::spaces()->getMessage());
        }

        return Inertia::render('spaces/form', [
            'space' => null,
            'themes' => $this->themes(),
            'optionalFields' => OptionalField::values(),
        ]);
    }

    public function store(SpaceRequest $request, CreateSpace $createSpace): RedirectResponse
    {
        try {
            $space = $createSpace->handle($this->user($request), $request->toData());
        } catch (PlanLimitReached $e) {
            return to_route('billing.show')->with('error', $e->getMessage());
        }

        return to_route('spaces.show', $space)->with('success', __('flash.space.created'));
    }

    public function show(InboxRequest $request, Space $space): Response
    {
        Gate::authorize('manage', $space);

        $inbox = $request->toData();
        $query = $space->testimonials()->latest('submitted_at');
        match ($inbox->filter) {
            InboxFilter::All => null,
            InboxFilter::Favorite => $query->where('is_favorite', true),
            default => $query->where('status', $inbox->filter->value),
        };
        $query->when($inbox->from !== null, static fn ($q) => $q->where('submitted_at', '>=', $inbox->from));
        $query->when($inbox->to !== null, static fn ($q) => $q->where('submitted_at', '<=', $inbox->to));

        return Inertia::render('spaces/show', [
            'space' => (new SpaceResource($space))->resolve(),
            'testimonials' => OwnerTestimonialResource::collection($query->paginate(15)->withQueryString()),
            'filter' => $inbox->filter->value,
            'range' => ['from' => $inbox->from?->toDateString(), 'to' => $inbox->to?->toDateString()],
            'counts' => $this->counts($space),
            'publicUrl' => url('/'.$space->slug),
        ]);
    }

    public function edit(Space $space): Response
    {
        Gate::authorize('manage', $space);

        return Inertia::render('spaces/form', [
            'space' => (new SpaceResource($space))->resolve(),
            'themes' => $this->themes(),
            'optionalFields' => OptionalField::values(),
        ]);
    }

    public function update(SpaceRequest $request, Space $space, UpdateSpace $updateSpace): RedirectResponse
    {
        Gate::authorize('manage', $space);
        $updateSpace->handle($space, $request->toData());

        return to_route('spaces.show', $space)->with('success', __('flash.space.updated'));
    }

    public function destroy(Space $space, DeleteSpace $deleteSpace): RedirectResponse
    {
        Gate::authorize('manage', $space);
        $deleteSpace->handle($space);

        return to_route('spaces.index')->with('success', __('flash.space.deleted'));
    }

    /** @return array<string, int> */
    private function counts(Space $space): array
    {
        $byStatus = $space->testimonials()->selectRaw('status, count(*) as total')->groupBy('status')->pluck('total', 'status');

        return [
            InboxFilter::All->value => (int) $byStatus->sum(),
            InboxFilter::Favorite->value => $space->testimonials()->where('is_favorite', true)->count(),
            InboxFilter::Pending->value => (int) ($byStatus['pending'] ?? 0),
            InboxFilter::Published->value => (int) ($byStatus['published'] ?? 0),
            InboxFilter::Hidden->value => (int) ($byStatus['hidden'] ?? 0),
        ];
    }

    /** @return list<array{value: string, label: string}> */
    private function themes(): array
    {
        return array_map(
            static fn (SpaceTheme $t): array => ['value' => $t->value, 'label' => $t->label()],
            SpaceTheme::cases(),
        );
    }

    private function user(Request $request): User
    {
        /** @var User $user */
        $user = $request->user();

        return $user;
    }
}
