<?php

declare(strict_types=1);

namespace App\Console\Commands;

use Illuminate\Console\Command;
use Illuminate\Support\Facades\File;

/**
 * Writes public/status/lang.json from lang/<locale>.json (only the status.* and outage.* keys), so the static
 * outage page can show its words even when the app is down.
 */
final class ExportStatusLang extends Command
{
    protected $signature = 'lang:export-status';

    protected $description = 'Export the outage/status translations to public/status/lang.json';

    public function handle(): int
    {
        $locale = (string) config('app.locale');
        $source = lang_path($locale.'.json');
        if (! File::exists($source)) {
            $this->error("Missing {$source}");

            return self::FAILURE;
        }

        /** @var array<string, string> $all */
        $all = json_decode((string) File::get($source), true, flags: JSON_THROW_ON_ERROR);
        $subset = array_filter(
            $all,
            static fn (string $key): bool => str_starts_with($key, 'status.') || str_starts_with($key, 'outage.'),
            ARRAY_FILTER_USE_KEY,
        );

        File::ensureDirectoryExists(public_path('status'));
        File::put(public_path('status/lang.json'), json_encode($subset, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT | JSON_THROW_ON_ERROR)."\n");
        $this->info(count($subset).' keys exported for locale '.$locale);

        return self::SUCCESS;
    }
}
