<?php

declare(strict_types=1);

namespace App\Providers;

use App\Contracts\BillingGateway;
use App\Services\StripeBillingGateway;
use App\Support\Logging\RequestContext;
use Illuminate\Support\ServiceProvider;

final class AppServiceProvider extends ServiceProvider
{
    /**
     * Register any application services.
     */
    public function register(): void
    {
        $this->app->bind(BillingGateway::class, StripeBillingGateway::class);
        // one context per request; scoped so queue workers and Octane get a fresh one per job/request
        $this->app->scoped(RequestContext::class);
    }

    /**
     * Bootstrap any application services.
     */
    public function boot(): void
    {
        //
    }
}
