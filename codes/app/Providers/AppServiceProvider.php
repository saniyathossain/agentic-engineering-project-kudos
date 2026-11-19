<?php

declare(strict_types=1);

namespace App\Providers;

use App\Contracts\BillingGateway;
use App\Services\ResilientBillingGateway;
use App\Services\StripeBillingGateway;
use App\Support\Logging\RequestContext;
use App\Support\Resilience\Retrier;
use App\Support\Resilience\Sleeper;
use App\Support\Resilience\UsleepSleeper;
use Illuminate\Support\ServiceProvider;
use Stripe\HttpClient\CurlClient;
use Stripe\Stripe;

final class AppServiceProvider extends ServiceProvider
{
    /**
     * Register any application services.
     */
    public function register(): void
    {
        $this->app->bind(Sleeper::class, UsleepSleeper::class);
        $this->app->bind(
            BillingGateway::class,
            fn ($app): BillingGateway => new ResilientBillingGateway($app->make(StripeBillingGateway::class), $app->make(Retrier::class)),
        );
        // one context per request; scoped so queue workers and Octane get a fresh one per job/request
        $this->app->scoped(RequestContext::class);
    }

    /**
     * Bootstrap any application services.
     */
    public function boot(): void
    {
        // Stripe calls fail fast (so the Retrier and the edge's 60 s limit stay in charge) and are never retried by the SDK
        Stripe::setMaxNetworkRetries(0);
        CurlClient::instance()
            ->setTimeout((int) config('services.stripe.timeout_s'))
            ->setConnectTimeout((int) config('services.stripe.connect_timeout_s'));
    }
}
