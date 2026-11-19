<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Actions\Billing\BuildBillingOverview;
use App\Contracts\BillingGateway;
use App\Enums\Plan;
use App\Exceptions\BillingNotConfigured;
use App\Exceptions\BillingUnavailable;
use App\Models\User;
use App\Services\PlanResolver;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Inertia\Response;

final class BillingController extends Controller
{
    public function show(Request $request, BuildBillingOverview $overview): Response
    {
        return Inertia::render('billing/show', [
            'overview' => $overview->handle($this->user($request))->toArray(),
        ]);
    }

    public function checkout(Request $request, BillingGateway $gateway, PlanResolver $plans): mixed
    {
        $user = $this->user($request);
        if ($plans->for($user) === Plan::Pro) {
            return to_route('billing.show')->with('success', __('billing.already_pro'));
        }

        try {
            $url = $gateway->checkoutUrl($user, route('billing.success'), route('billing.show'));
        } catch (BillingUnavailable $e) {
            return to_route('billing.show')->with('error', $e->getMessage());
        } catch (BillingNotConfigured $e) {
            return to_route('billing.show')->with('error', $e->getMessage());
        }

        return Inertia::location($url);
    }

    /** The redirect alone is never proof of payment: confirm with Stripe, then wait for the webhook-recorded subscription. */
    public function success(Request $request, BillingGateway $gateway, PlanResolver $plans): RedirectResponse
    {
        $user = $this->user($request);
        $sessionId = (string) $request->query('session_id');

        try {
            $confirmed = $sessionId !== '' && $gateway->isCheckoutCompleteFor($user, $sessionId);
        } catch (BillingUnavailable $e) {
            return to_route('billing.show')->with('error', $e->getMessage());
        }

        if (! $confirmed) {
            return to_route('billing.show')->with('error', __('billing.confirm_failed'));
        }

        $message = $plans->for($user) === Plan::Pro ? __('billing.upgrade_active') : __('billing.payment_confirmed');

        return to_route('billing.show')->with('success', $message);
    }

    public function portal(Request $request, BillingGateway $gateway): mixed
    {
        $user = $this->user($request);
        if (! $user->hasStripeId()) {
            return to_route('billing.show')->with('error', __('billing.no_profile'));
        }

        try {
            return Inertia::location($gateway->portalUrl($user, route('billing.show')));
        } catch (BillingUnavailable $e) {
            return to_route('billing.show')->with('error', $e->getMessage());
        }
    }

    private function user(Request $request): User
    {
        /** @var User $user */
        $user = $request->user();

        return $user;
    }
}
