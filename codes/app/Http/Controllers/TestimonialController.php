<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Actions\Testimonials\DeleteTestimonial;
use App\Actions\Testimonials\UpdateTestimonial;
use App\Http\Requests\Testimonials\EditTestimonialRequest;
use App\Http\Requests\Testimonials\SetStatusRequest;
use App\Models\Testimonial;
use Illuminate\Http\RedirectResponse;
use Illuminate\Support\Facades\Gate;

final class TestimonialController extends Controller
{
    public function update(EditTestimonialRequest $request, Testimonial $testimonial, UpdateTestimonial $actions): RedirectResponse
    {
        Gate::authorize('manage', $testimonial);
        $actions->editBody($testimonial, $request->body());

        return back()->with('success', 'Testimonial updated.');
    }

    public function status(SetStatusRequest $request, Testimonial $testimonial, UpdateTestimonial $actions): RedirectResponse
    {
        Gate::authorize('manage', $testimonial);
        $actions->setStatus($testimonial, $request->status());

        return back()->with('success', 'Status changed to '.$request->status()->value.'.');
    }

    public function favorite(Testimonial $testimonial, UpdateTestimonial $actions): RedirectResponse
    {
        Gate::authorize('manage', $testimonial);
        $actions->toggleFavorite($testimonial);

        return back();
    }

    public function destroy(Testimonial $testimonial, DeleteTestimonial $delete): RedirectResponse
    {
        Gate::authorize('manage', $testimonial);
        $delete->handle($testimonial);

        return back()->with('success', 'Testimonial deleted.');
    }
}
