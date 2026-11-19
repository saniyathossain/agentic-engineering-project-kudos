<?php

declare(strict_types=1);

namespace Tests\Support;

use Illuminate\Support\Facades\DB;

trait BreaksDatabase
{
    /**
     * Runs $callback while the default database connection points at a server that refuses connections, then
     * restores it so RefreshDatabase can still roll back its own transaction.
     *
     * @template T
     *
     * @param  callable(): T  $callback
     * @return T
     */
    protected function withBrokenDatabase(callable $callback): mixed
    {
        $original = (string) config('database.default');
        config(['database.connections.broken' => ['driver' => 'pgsql', 'host' => '127.0.0.1', 'port' => 1, 'database' => 'x', 'username' => 'x', 'password' => 'x', 'connect_timeout' => 1]]);
        DB::purge('broken');
        DB::setDefaultConnection('broken');

        try {
            return $callback();
        } finally {
            DB::setDefaultConnection($original);
        }
    }
}
