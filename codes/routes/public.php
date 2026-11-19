<?php

declare(strict_types=1);

use App\Http\Controllers\PublicSpaceController;
use App\Services\SlugGenerator;
use Illuminate\Support\Facades\Route;

// a slug is lowercase words and hyphens, and never one of the names the application owns
$slug = '^(?!(?:'.implode('|', array_map('preg_quote', SlugGenerator::RESERVED)).')$)[a-z0-9-]+$';

Route::prefix('{space:slug}')->where(['space' => $slug])->group(function (): void {
    Route::get('/', [PublicSpaceController::class, 'show'])->name('public.space');
    Route::post('/', [PublicSpaceController::class, 'store'])->middleware('throttle:20,1')->name('public.submit');
});
