<?php

declare(strict_types=1);

use App\Http\Controllers\BillingController;
use Illuminate\Support\Facades\Route;

Route::middleware(['auth', 'verified'])->prefix('billing')->name('billing.')->group(function (): void {
    Route::get('/', [BillingController::class, 'show'])->name('show');
    Route::post('checkout', [BillingController::class, 'checkout'])->name('checkout');
    Route::get('success', [BillingController::class, 'success'])->name('success');
    Route::post('portal', [BillingController::class, 'portal'])->name('portal');
});
