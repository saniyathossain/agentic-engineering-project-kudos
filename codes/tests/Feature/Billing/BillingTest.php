<?php

declare(strict_types=1);

namespace Tests\Feature\Billing;

use App\Contracts\BillingGateway;
use App\Enums\Plan;
use App\Models\Space;
use App\Models\User;
use App\Services\PlanResolver;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

final class BillingTest extends TestCase
{
    use RefreshDatabase;

    private function fakeGateway(bool $complete = true): void
    {
        $this->app->instance(BillingGateway::class, new class ($complete) implements BillingGateway {
            public function __construct(private readonly bool $complete)
            {
            }

            public function checkoutUrl(User $user, string $successUrl, string $cancelUrl): string
            {
                return 'https://checkout.stripe.test/session';
            }

            public function isCheckoutCompleteFor(User $user, string $sessionId): bool
            {
                return $this->complete;
            }

            public function portalUrl(User $user, string $returnUrl): string
            {
                return 'https://billing.stripe.test/portal';
            }
        });
    }

    private function subscribe(User $user): void
    {
        $user->forceFill(['stripe_id' => 'cus_test'])->save();
        $user->subscriptions()->create([
            'type' => PlanResolver::SUBSCRIPTION_TYPE,
            'stripe_id' => 'sub_test',
            'stripe_status' => 'active',
            'stripe_price' => 'price_test',
            'quantity' => 1,
        ]);
    }

    public function test_billing_page_shows_free_plan_and_usage(): void
    {
        $user = User::factory()->create();
        Space::factory()->for($user, 'owner')->create();

        $this->actingAs($user)->get('/billing')->assertInertia(
            fn ($p) => $p->component('billing/show')->where('overview.plan.value', 'free')
                ->where('overview.spaces_used', 1)->where('overview.spaces_max', 1)
                ->where('overview.testimonials_per_space_max', 10),
        );
    }

    public function test_subscribed_user_is_pro_with_no_limits_and_can_open_portal(): void
    {
        $user = User::factory()->create();
        $this->subscribe($user);
        $this->fakeGateway();

        $this->assertSame(Plan::Pro, app(PlanResolver::class)->for($user));
        $this->actingAs($user)->get('/billing')->assertInertia(
            fn ($p) => $p->where('overview.plan.value', 'pro')->where('overview.spaces_max', null)->where('overview.can_manage_billing', true),
        );
        $this->actingAs($user)->post('/billing/portal')->assertRedirect('https://billing.stripe.test/portal');
    }

    public function test_pro_user_can_create_more_than_one_space(): void
    {
        $user = User::factory()->create();
        $this->subscribe($user);
        Space::factory()->for($user, 'owner')->count(2)->create();

        $this->assertTrue(app(PlanResolver::class)->canCreateSpace($user));
    }

    public function test_checkout_redirects_to_stripe(): void
    {
        $this->fakeGateway();

        $this->actingAs(User::factory()->create())->post('/billing/checkout')
            ->assertRedirect('https://checkout.stripe.test/session');
    }

    public function test_checkout_without_stripe_configuration_degrades_gracefully(): void
    {
        config(['services.stripe.pro_price_id' => '']);

        $this->actingAs(User::factory()->create())->post('/billing/checkout')
            ->assertRedirect('/billing')->assertSessionHas('error');
    }

    public function test_success_redirect_is_not_trusted_without_stripe_confirmation(): void
    {
        $this->fakeGateway(complete: false);
        $user = User::factory()->create();

        $this->actingAs($user)->get('/billing/success?session_id=cs_fake')->assertRedirect('/billing')->assertSessionHas('error');
        $this->assertSame(Plan::Free, app(PlanResolver::class)->for($user), 'redirect alone must not upgrade');
    }

    public function test_confirmed_success_waits_for_webhook_recorded_subscription(): void
    {
        $this->fakeGateway();
        $user = User::factory()->create();

        $this->actingAs($user)->get('/billing/success?session_id=cs_ok')->assertSessionHas('success');
        $this->assertSame(Plan::Free, app(PlanResolver::class)->for($user), 'only the webhook creates the subscription');

        $this->subscribe($user);
        $this->actingAs($user->refresh())->get('/billing/success?session_id=cs_ok')
            ->assertSessionHas('success', 'You are on Pro now. Your upgrade is active.');
    }

    public function test_downgrade_never_deletes_data_but_stops_new_spaces(): void
    {
        $user = User::factory()->create();
        Space::factory()->for($user, 'owner')->count(2)->create();

        $this->assertFalse(app(PlanResolver::class)->canCreateSpace($user));
        $this->assertSame(2, $user->spaces()->count());
    }

    public function test_stripe_webhook_route_exists_and_rejects_bad_signatures(): void
    {
        config(['cashier.webhook.secret' => 'whsec_test']);

        $this->postJson('/stripe/webhook', ['type' => 'customer.subscription.created'], ['Stripe-Signature' => 't=1,v1=bad'])
            ->assertForbidden();
    }
}
