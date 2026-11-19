<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Actions\Dashboard\DismissUpgradeBanner;
use App\Models\User;
use Illuminate\Auth\AuthenticationException;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;

final class DismissUpgradeBannerController extends Controller
{
    public function __invoke(Request $request, DismissUpgradeBanner $dismiss): RedirectResponse
    {
        $user = $request->user();
        if (! $user instanceof User) {
            throw new AuthenticationException();
        }

        $dismiss->handle($user);

        return back();
    }
}
