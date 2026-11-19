<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Data\Health\HealthCheck;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Storage;
use Throwable;

/** Probes for the edge, the outage page and orchestrators. No session, no auth, no access log. */
final class HealthController extends Controller
{
    public function live(): JsonResponse
    {
        return response()->json(['status' => 'ok'], headers: ['Cache-Control' => 'no-store']);
    }

    public function ready(): JsonResponse
    {
        $checks = [
            $this->check('database', true, static fn () => DB::select('select 1')),
            $this->check('cache', false, static fn () => Cache::get('readyz-probe')),
            $this->check('storage', false, static fn () => Storage::disk('public')->exists('.')),
        ];
        $ready = collect($checks)->every(static fn (HealthCheck $c): bool => $c->up || ! $c->critical);

        return response()->json(
            ['status' => $ready ? 'ok' : 'unavailable', 'checks' => array_map(static fn (HealthCheck $c): array => $c->toArray(), $checks)],
            $ready ? 200 : 503,
            ['Cache-Control' => 'no-store'] + ($ready ? [] : ['Retry-After' => '5']),
        );
    }

    /** @param  callable(): mixed  $probe */
    private function check(string $name, bool $critical, callable $probe): HealthCheck
    {
        try {
            $probe();

            return new HealthCheck($name, $critical, true);
        } catch (Throwable) {
            return new HealthCheck($name, $critical, false);
        }
    }
}
