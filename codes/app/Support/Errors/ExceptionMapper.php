<?php

declare(strict_types=1);

namespace App\Support\Errors;

use App\Enums\Dependency;
use App\Exceptions\BillingNotConfigured;
use App\Exceptions\BillingUnavailable;
use Illuminate\Auth\AuthenticationException;
use Illuminate\Database\LostConnectionException;
use Illuminate\Database\QueryException;
use Illuminate\Http\Exceptions\HttpResponseException;
use Illuminate\Validation\ValidationException;
use PDOException;
use Symfony\Component\HttpKernel\Exception\HttpExceptionInterface;
use Throwable;

/**
 * Decides how a failure is presented. Runs from a render callback, so Laravel has already turned model-not-found,
 * authorization and CSRF failures into HTTP exceptions (404, 403, 419): only those arrive here.
 *
 * Returns null for what the framework already handles well (validation errors, redirects to login, responses an
 * action built itself). Expected failures of things we depend on (database, Stripe) are 503, never a bare 500.
 */
final class ExceptionMapper
{
    private const CONNECTION_MARKERS = ['could not connect', 'connection refused', 'server has gone away', 'server closed the connection', 'no route to host', 'connection timed out', 'terminating connection', 'the database system is', 'name or service not known', 'could not translate host'];

    /** SQLSTATE class 08 (connection exception, except 08P01 protocol violation = a bug), 57P01-03 (shutdown), class 53 (resources). */
    private const DOWN_SQLSTATE = '/SQLSTATE\[(?:08(?!P01)|57P0[123]|53)/';

    public function map(Throwable $e): ?ErrorPage
    {
        return match (true) {
            $e instanceof ValidationException, $e instanceof AuthenticationException, $e instanceof HttpResponseException => null,
            $e instanceof BillingUnavailable => new ErrorPage(503, Dependency::Billing, 5),
            $e instanceof BillingNotConfigured => new ErrorPage(503, Dependency::Billing),
            $this->databaseDown($e) => new ErrorPage(503, Dependency::Database, 5),
            $e instanceof HttpExceptionInterface => new ErrorPage($e->getStatusCode(), retryAfter: $this->retryAfter($e)),
            default => new ErrorPage(500),
        };
    }

    private function databaseDown(Throwable $e): bool
    {
        if ($e instanceof LostConnectionException) {
            return true;
        }
        if (! $e instanceof QueryException && ! $e instanceof PDOException) {
            return false;
        }

        $message = strtolower($e->getMessage().' '.($e->getPrevious()?->getMessage() ?? ''));
        foreach (self::CONNECTION_MARKERS as $marker) {
            if (str_contains($message, $marker)) {
                return true;
            }
        }

        return preg_match(self::DOWN_SQLSTATE, $e->getMessage().' '.($e->getPrevious()?->getMessage() ?? '')) === 1;
    }

    private function retryAfter(HttpExceptionInterface $e): ?int
    {
        $value = $e->getHeaders()['Retry-After'] ?? null;

        return is_numeric($value) ? (int) $value : null;
    }
}
