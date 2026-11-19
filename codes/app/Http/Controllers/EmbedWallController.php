<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Actions\Embed\ListPublishedTestimonials;
use App\Http\Resources\EmbedSpaceResource;
use App\Http\Resources\EmbedTestimonialResource;
use App\Models\Space;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Inertia\Response;

final class EmbedWallController extends Controller
{
    public function __construct(private readonly ListPublishedTestimonials $published)
    {
    }

    public function show(Request $request, Space $space): Response
    {
        return Inertia::render('embed/wall', [
            'space' => (new EmbedSpaceResource($space))->resolve($request),
            'testimonials' => EmbedTestimonialResource::collection($this->published->handle($space))->resolve($request),
        ]);
    }

    public function json(Request $request, Space $space): JsonResponse
    {
        return EmbedTestimonialResource::collection($this->published->handle($space))
            ->additional(['space' => (new EmbedSpaceResource($space))->resolve($request)])
            ->toResponse($request);
    }
}
