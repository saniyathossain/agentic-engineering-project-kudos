<?php

declare(strict_types=1);

use Illuminate\Support\Facades\Route;
use Inertia\Inertia;

Route::get('/', fn () => Inertia::render('welcome'))->name('home');

require __DIR__.'/settings.php';
require __DIR__.'/auth.php';
require __DIR__.'/dashboard.php';
require __DIR__.'/spaces.php';
require __DIR__.'/billing.php';
require __DIR__.'/embed.php';
// public collection pages catch /{slug}: keep this last
require __DIR__.'/public.php';
