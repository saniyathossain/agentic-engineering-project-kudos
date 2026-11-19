<?php

declare(strict_types=1);

use App\Http\Controllers\SpaceController;
use App\Http\Controllers\TestimonialController;
use Illuminate\Support\Facades\Route;

Route::middleware(['auth', 'verified'])->group(function (): void {
    Route::resource('spaces', SpaceController::class)->parameters(['spaces' => 'space']);

    Route::prefix('testimonials/{testimonial}')->name('testimonials.')->group(function (): void {
        Route::patch('/', [TestimonialController::class, 'update'])->name('update');
        Route::patch('status', [TestimonialController::class, 'status'])->name('status');
        Route::patch('favorite', [TestimonialController::class, 'favorite'])->name('favorite');
        Route::delete('/', [TestimonialController::class, 'destroy'])->name('destroy');
    });
});
