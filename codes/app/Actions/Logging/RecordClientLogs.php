<?php

declare(strict_types=1);

namespace App\Actions\Logging;

use App\Data\Logging\ClientLogEntry;
use App\Support\Logging\Scrub;
use Illuminate\Support\Facades\Log;

/** Writes browser log lines into the same JSON stream as the server's, marked source=browser. */
final class RecordClientLogs
{
    private const MAX_DATA_BYTES = 2000;

    /**
     * @param  list<ClientLogEntry>  $entries
     * @param  array<string, string>  $device  hints the browser could not send as headers (timezone, screen, ...)
     */
    public function handle(array $entries, array $device, ?string $pageViewId): void
    {
        foreach ($entries as $entry) {
            $encoded = json_encode($entry->data, JSON_UNESCAPED_UNICODE | JSON_PARTIAL_OUTPUT_ON_ERROR);

            Log::log($entry->level->psr(), $entry->message, array_filter([
                'event' => 'client.log',
                'source' => 'browser',
                'tag' => $entry->tag,
                'page_url' => $entry->url === null ? null : Scrub::path($entry->url),
                'page_view_id' => $pageViewId,
                'device' => $device === [] ? null : $device,
                'data' => $encoded !== false && strlen($encoded) > self::MAX_DATA_BYTES ? ['truncated' => true] : Scrub::deep($entry->data),
            ], static fn (mixed $v): bool => $v !== null && $v !== []));
        }
    }
}
