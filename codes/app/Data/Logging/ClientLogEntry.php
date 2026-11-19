<?php

declare(strict_types=1);

namespace App\Data\Logging;

use App\Enums\ClientLogLevel;

/** One line shipped by the browser logger. */
final readonly class ClientLogEntry
{
    /** @param  array<string, mixed>  $data */
    public function __construct(
        public ClientLogLevel $level,
        public string $message,
        public ?string $tag,
        public ?string $url,
        public array $data,
    ) {
    }
}
