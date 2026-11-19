<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Actions\Dashboard\BuildDashboardStats;
use App\Http\Requests\Dashboard\DashboardRequest;
use App\Models\User;
use Illuminate\Auth\AuthenticationException;
use Inertia\Inertia;
use Inertia\Response;

final class DashboardController extends Controller
{
    public function __invoke(DashboardRequest $request, BuildDashboardStats $stats): Response
    {
        $user = $request->user();
        if (! $user instanceof User) {
            throw new AuthenticationException();
        }

        return Inertia::render('dashboard', [
            'stats' => $stats->handle($user, $request->range())->toArray(),
        ]);
    }
}
