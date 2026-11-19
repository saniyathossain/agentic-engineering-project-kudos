<?php

declare(strict_types=1);

namespace Tests\Feature\Errors;

use App\Contracts\BillingGateway;
use App\Enums\Dependency;
use App\Exceptions\BillingUnavailable;
use App\Http\Middleware\HandleInertiaRequests;
use App\Models\User;
use App\Support\Errors\ExceptionMapper;
use Illuminate\Auth\AuthenticationException;
use Illuminate\Database\QueryException;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Session\TokenMismatchException;
use Illuminate\Support\Facades\Route;
use Illuminate\Validation\ValidationException;
use PDOException;
use RuntimeException;
use Symfony\Component\HttpKernel\Exception\AccessDeniedHttpException;
use Symfony\Component\HttpKernel\Exception\NotFoundHttpException;
use Tests\Support\BreaksDatabase;
use Tests\TestCase;

final class ErrorPagesTest extends TestCase
{
    use BreaksDatabase;
    use RefreshDatabase;

    public function test_a_missing_page_is_a_friendly_404_that_shows_the_request_id(): void
    {
        $response = $this->get('/no-such-space')->assertNotFound();

        $id = (string) $response->headers->get('X-Request-ID');
        $response->assertSee(__('status.title.404'))->assertSee($id);
        $response->assertDontSee('Illuminate\\');
    }

    public function test_json_callers_get_a_structured_error_with_the_request_id(): void
    {
        $response = $this->getJson('/no-such-space')->assertNotFound();

        $response->assertJsonStructure(['error', 'code', 'dependency', 'request_id']);
        $this->assertSame($response->headers->get('X-Request-ID'), $response->json('request_id'));
    }

    public function test_a_database_outage_is_a_503_with_retry_after_not_a_500(): void
    {
        $response = $this->withBrokenDatabase(fn () => $this->get('/some-space'))->assertStatus(503);

        $response->assertHeader('Retry-After', '5')->assertSee(__('status.title.503'))->assertSee(__('status.dependency.database'));
        $response->assertSee('data-poll', false);
    }

    public function test_an_unexpected_bug_is_a_friendly_500_page_without_leaking_details(): void
    {
        config(['app.debug' => false]);
        Route::get('/__boom', fn () => throw new RuntimeException('secret internal detail'));

        $response = $this->get('/__boom')->assertStatus(500);

        $response->assertSee(__('status.title.500'))->assertDontSee('secret internal detail');
        $response->assertSee((string) $response->headers->get('X-Request-ID'));
    }

    public function test_in_debug_mode_a_bug_still_shows_its_trace(): void
    {
        config(['app.debug' => true]);
        Route::get('/__boom', fn () => throw new RuntimeException('visible while debugging'));

        $this->get('/__boom')->assertStatus(500)->assertSee('visible while debugging');
    }

    public function test_an_inertia_visit_that_fails_gets_the_react_error_page_without_a_second_request(): void
    {
        $this->withHeaders(['X-Inertia' => 'true', 'X-Inertia-Version' => $this->inertiaVersion()])->get('/no-such-space')
            ->assertStatus(404)->assertHeader('X-Inertia', 'true')
            ->assertJsonPath('component', 'errors/error')->assertJsonPath('props.status', 404)->assertJsonPath('props.copyKey', '404');
    }

    public function test_an_inertia_visit_during_an_outage_is_sent_to_a_full_page_load(): void
    {
        $response = $this->withBrokenDatabase(fn () => $this->withHeaders(['X-Inertia' => 'true', 'X-Inertia-Version' => $this->inertiaVersion()])->get('/some-space'));

        $response->assertStatus(409)->assertHeader('X-Inertia-Location', url('/some-space'))->assertHeader('Retry-After', '5');
    }

    public function test_an_expired_session_is_a_419_page(): void
    {
        Route::post('/__expired', fn () => throw new TokenMismatchException());

        $this->post('/__expired')->assertStatus(419)->assertSee(__('status.title.419'));
    }

    public function test_a_throttled_page_is_a_429_with_retry_after_and_does_not_poll(): void
    {
        Route::get('/__slow', fn () => 'ok')->middleware('throttle:1,1');
        $this->get('/__slow')->assertOk();

        $response = $this->get('/__slow')->assertStatus(429);

        $response->assertSee(__('status.title.429'))->assertHeader('Retry-After');
        $response->assertDontSee('data-poll', false);
    }

    public function test_other_client_errors_get_neutral_words(): void
    {
        Route::post('/__only-post', fn () => 'ok');

        $this->get('/__only-post')->assertStatus(405)->assertSee(__('status.title.4xx'));
    }

    public function test_a_database_outage_as_json_is_a_503_with_the_dependency(): void
    {
        $response = $this->withBrokenDatabase(fn () => $this->getJson('/some-space'));

        $response->assertStatus(503)->assertHeader('Retry-After', '5')->assertJson(['code' => 'unavailable', 'dependency' => 'database']);
        $this->assertSame($response->headers->get('X-Request-ID'), $response->json('request_id'));
    }

    private function inertiaVersion(): string
    {
        return (string) (new HandleInertiaRequests())->version(request());
    }

    public function test_billing_being_down_is_flashed_on_the_billing_page_not_a_500(): void
    {
        $this->app->instance(BillingGateway::class, new class () implements BillingGateway {
            public function checkoutUrl(User $user, string $successUrl, string $cancelUrl): string
            {
                throw BillingUnavailable::after(new RuntimeException('stripe down'));
            }

            public function isCheckoutCompleteFor(User $user, string $sessionId): bool
            {
                throw BillingUnavailable::after(new RuntimeException('stripe down'));
            }

            public function portalUrl(User $user, string $returnUrl): string
            {
                throw BillingUnavailable::after(new RuntimeException('stripe down'));
            }
        });
        $user = User::factory()->create(['stripe_id' => 'cus_x']);

        $this->actingAs($user)->post('/billing/checkout')->assertRedirect('/billing')->assertSessionHas('error', __('billing.unavailable'));
        $this->actingAs($user)->get('/billing/success?session_id=cs_x')->assertRedirect('/billing')->assertSessionHas('error', __('billing.unavailable'));
        $this->actingAs($user)->post('/billing/portal')->assertRedirect('/billing')->assertSessionHas('error', __('billing.unavailable'));
    }

    public function test_the_mapper_classifies_failures(): void
    {
        $mapper = new ExceptionMapper();

        $this->assertNull($mapper->map(ValidationException::withMessages(['a' => 'b'])));
        $this->assertNull($mapper->map(new AuthenticationException()));
        $this->assertSame(404, $mapper->map(new NotFoundHttpException())?->status);
        $this->assertSame(403, $mapper->map(new AccessDeniedHttpException())?->status);
        $this->assertSame(500, $mapper->map(new RuntimeException('bug'))?->status);

        $down = $mapper->map(new QueryException('pgsql', 'select 1', [], new PDOException('SQLSTATE[08006] [7] connection refused')));
        $this->assertSame(503, $down?->status);
        $this->assertSame(Dependency::Database, $down->dependency);

        $this->assertSame(503, $mapper->map(BillingUnavailable::after(new RuntimeException()))?->status);
        $this->assertSame(500, $mapper->map(new QueryException('pgsql', 'select', [], new PDOException('SQLSTATE[42P01] relation missing')))?->status, 'a bad query is a bug, not an outage');
        $this->assertSame(500, $mapper->map(new QueryException('pgsql', 'select', [], new PDOException('SQLSTATE[08P01] protocol violation')))?->status, '08P01 is a protocol bug');
        $this->assertSame(503, $mapper->map(new QueryException('pgsql', 'select', [], new PDOException('SQLSTATE[57P01] admin shutdown')))?->status);
    }
}
