<?php

declare(strict_types=1);

use App\Http\Controllers\PublicSpaceController;
use Illuminate\Support\Facades\Route;

Route::prefix('{space:slug}')->where(['space' => '[a-z0-9-]+'])->group(function (): void {
    Route::get('/', [PublicSpaceController::class, 'show'])->name('public.space');
    Route::post('/', [PublicSpaceController::class, 'store'])->middleware('throttle:20,1')->name('public.submit');
});
