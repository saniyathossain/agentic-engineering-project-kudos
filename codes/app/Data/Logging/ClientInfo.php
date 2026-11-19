<?php

declare(strict_types=1);

namespace App\Data\Logging;

use App\Enums\DeviceType;

/** Everything we can say about the caller's device, from headers only. Never from the request body. */
final readonly class ClientInfo
{
    public function __construct(
        public DeviceType $type = DeviceType::Unknown,
        public ?string $os = null,
        public ?string $osVersion = null,
        public ?string $browser = null,
        public ?string $browserVersion = null,
        public ?string $brand = null,
        public ?string $model = null,
        public ?string $platform = null,
        public ?string $clientVersion = null,
        public ?string $language = null,
        public ?string $timezone = null,
        public ?string $screen = null,
        public ?string $connection = null,
        public ?string $userAgent = null,
    ) {
    }

    /** @return array<string, string> only the fields that are known */
    public function toArray(): array
    {
        return array_filter([
            'type' => $this->type->value,
            'os' => $this->os,
            'os_version' => $this->osVersion,
            'browser' => $this->browser,
            'browser_version' => $this->browserVersion,
            'brand' => $this->brand,
            'model' => $this->model,
            'platform' => $this->platform,
            'client_version' => $this->clientVersion,
            'language' => $this->language,
            'timezone' => $this->timezone,
            'screen' => $this->screen,
            'connection' => $this->connection,
            'user_agent' => $this->userAgent,
        ], static fn (?string $value): bool => $value !== null && $value !== '');
    }
}
