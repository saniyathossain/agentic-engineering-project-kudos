<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Actions\Testimonials\SubmitTestimonial;
use App\Exceptions\PlanLimitReached;
use App\Http\Requests\Testimonials\SubmitTestimonialRequest;
use App\Http\Resources\SpaceResource;
use App\Models\Space;
use App\Services\PlanResolver;
use Illuminate\Http\RedirectResponse;
use Inertia\Inertia;
use Inertia\Response;

final class PublicSpaceController extends Controller
{
    public function show(Space $space): Response
    {
        return Inertia::render('public/collect', [
            'space' => (new SpaceResource($space))->resolve(),
            'accepting' => app(PlanResolver::class)->acceptsTestimonials($space),
        ]);
    }

    public function store(SubmitTestimonialRequest $request, Space $space, SubmitTestimonial $submit): RedirectResponse
    {
        try {
            $submit->handle($space, $request->toData());
        } catch (PlanLimitReached $e) {
            return back()->with('error', $e->getMessage());
        }

        return back()->with('success', 'Thank you! Your testimonial was sent.');
    }
}
