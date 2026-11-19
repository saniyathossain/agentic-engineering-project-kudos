<?php

declare(strict_types=1);

use App\Http\Controllers\EmbedWallController;
use App\Http\Middleware\AllowEmbedding;
use Illuminate\Support\Facades\Route;

Route::middleware([AllowEmbedding::class])->prefix('embed/{space:public_id}')->group(function (): void {
    Route::get('/', [EmbedWallController::class, 'show'])->name('embed.wall');
    Route::get('testimonials.json', [EmbedWallController::class, 'json'])->name('embed.testimonials');
});
