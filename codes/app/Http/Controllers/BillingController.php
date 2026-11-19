<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Actions\Billing\BuildBillingOverview;
use App\Contracts\BillingGateway;
use App\Models\User;
use App\Services\PlanResolver;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Inertia\Response;
use RuntimeException;

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
        if ($plans->for($user)->value === 'pro') {
            return to_route('billing.show')->with('success', 'You are already on the Pro plan.');
        }

        try {
            $url = $gateway->checkoutUrl($user, route('billing.success'), route('billing.show'));
        } catch (RuntimeException $e) {
            return to_route('billing.show')->with('error', 'Billing is not configured yet: '.$e->getMessage());
        }

        return Inertia::location($url);
    }

    /** The redirect alone is never proof of payment: confirm with Stripe, then wait for the webhook-recorded subscription. */
    public function success(Request $request, BillingGateway $gateway, PlanResolver $plans): RedirectResponse
    {
        $user = $this->user($request);
        $sessionId = (string) $request->query('session_id');

        if ($sessionId === '' || ! $gateway->isCheckoutCompleteFor($user, $sessionId)) {
            return to_route('billing.show')->with('error', 'We could not confirm that payment.');
        }

        $message = $plans->for($user)->value === 'pro'
            ? 'Welcome to Pro! Your upgrade is active.'
            : 'Payment confirmed. Your Pro plan activates as soon as Stripe notifies us (usually seconds) - refresh this page.';

        return to_route('billing.show')->with('success', $message);
    }

    public function portal(Request $request, BillingGateway $gateway): mixed
    {
        $user = $this->user($request);
        if (! $user->hasStripeId()) {
            return to_route('billing.show')->with('error', 'No billing profile yet.');
        }

        return Inertia::location($gateway->portalUrl($user, route('billing.show')));
    }

    private function user(Request $request): User
    {
        /** @var User $user */
        $user = $request->user();

        return $user;
    }
}
