<?php

declare(strict_types=1);

use App\Http\Controllers\DashboardController;
use App\Http\Controllers\DismissUpgradeBannerController;
use Illuminate\Support\Facades\Route;

Route::middleware(['auth'])->group(function (): void {
    Route::get('dashboard', DashboardController::class)->name('dashboard');
    Route::post('dashboard/banner/dismiss', DismissUpgradeBannerController::class)->name('dashboard.banner.dismiss');
});
