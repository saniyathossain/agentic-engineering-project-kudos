<?php

declare(strict_types=1);

namespace App\Support\Logging;

use App\Data\Logging\ClientInfo;
use App\Enums\DeviceType;
use Illuminate\Http\Request;

/** Builds {@see ClientInfo} from the User-Agent, UA client hints and the optional X-Client-* / X-Device-* headers. */
final class ClientInfoFactory
{
    private const MAX_VALUE = 200;

    private const BOT_PATTERN = '/bot|crawl|spider|slurp|headless|curl|wget|python-requests|httpclient|monitor|uptime|preview/i';

    /** @var list<array{0: string, 1: string}> */
    private const OS_PATTERNS = [
        ['/Windows NT ([\d.]+)/', 'Windows'],
        ['/Android ([\d.]+)/', 'Android'],
        ['/(?:iPhone|iPad|iPod).*? OS ([\d_]+)/', 'iOS'],
        ['/Mac OS X ([\d_.]+)/', 'macOS'],
        ['/CrOS [\w]+ ([\d.]+)/', 'ChromeOS'],
        ['/Linux/', 'Linux'],
    ];

    /** @var list<array{0: string, 1: string}> order matters: Edge and Opera also say Chrome */
    private const BROWSER_PATTERNS = [
        ['/Edg(?:e|A|iOS)?\/([\d.]+)/', 'Edge'],
        ['/OPR\/([\d.]+)/', 'Opera'],
        ['/(?:Chrome|CriOS)\/([\d.]+)/', 'Chrome'],
        ['/(?:Firefox|FxiOS)\/([\d.]+)/', 'Firefox'],
        ['/Version\/([\d.]+).*Safari/', 'Safari'],
    ];

    public function fromRequest(Request $request): ClientInfo
    {
        $userAgent = $this->clean($request->userAgent());
        $os = $this->detect(self::OS_PATTERNS, (string) $userAgent);
        $browser = $this->detect(self::BROWSER_PATTERNS, (string) $userAgent);
        $hintedPlatform = $this->hint($request, 'Sec-CH-UA-Platform');

        return new ClientInfo(
            type: $this->type($request, (string) $userAgent),
            os: $this->header($request, 'X-Device-OS') ?? $hintedPlatform ?? $os['name'],
            osVersion: $this->header($request, 'X-Device-OS-Version') ?? $os['version'],
            browser: $browser['name'],
            browserVersion: $browser['version'],
            brand: $this->header($request, 'X-Device-Brand'),
            model: $this->header($request, 'X-Device-Model') ?? $this->hint($request, 'Sec-CH-UA-Model'),
            platform: $this->header($request, 'X-Client-Platform'),
            clientVersion: $this->header($request, 'X-Client-Version'),
            language: $this->header($request, 'X-Client-Language') ?? $this->primaryLanguage($request),
            timezone: $this->header($request, 'X-Client-Timezone') ?? $this->header($request, 'X-Timezone'),
            screen: $this->header($request, 'X-Client-Screen'),
            connection: $this->header($request, 'X-Client-Connection') ?? $this->header($request, 'X-Connection-Type'),
            userAgent: $userAgent,
        );
    }

    private function type(Request $request, string $userAgent): DeviceType
    {
        if ($userAgent === '' || preg_match(self::BOT_PATTERN, $userAgent) === 1) {
            return $userAgent === '' ? DeviceType::Unknown : DeviceType::Bot;
        }
        if (preg_match('/iPad|Tablet|Android(?!.*Mobile)/i', $userAgent) === 1) {
            return DeviceType::Tablet;
        }
        if ($this->hint($request, 'Sec-CH-UA-Mobile') === '?1' || preg_match('/Mobi|iPhone|iPod|Android/i', $userAgent) === 1) {
            return DeviceType::Mobile;
        }

        return DeviceType::Desktop;
    }

    /**
     * @param  list<array{0: string, 1: string}>  $patterns
     * @return array{name: ?string, version: ?string}
     */
    private function detect(array $patterns, string $userAgent): array
    {
        foreach ($patterns as [$pattern, $name]) {
            if (preg_match($pattern, $userAgent, $match) === 1) {
                return ['name' => $name, 'version' => isset($match[1]) ? str_replace('_', '.', $match[1]) : null];
            }
        }

        return ['name' => null, 'version' => null];
    }

    private function primaryLanguage(Request $request): ?string
    {
        $header = $this->header($request, 'Accept-Language');

        return $header === null ? null : trim(explode(',', explode(';', $header)[0])[0]);
    }

    /** UA client hints arrive quoted, e.g. "macOS". */
    private function hint(Request $request, string $name): ?string
    {
        $value = $this->header($request, $name);

        return $value === null ? null : trim($value, '"');
    }

    private function header(Request $request, string $name): ?string
    {
        return $this->clean($request->headers->get($name));
    }

    private function clean(?string $value): ?string
    {
        if ($value === null) {
            return null;
        }
        // headers are attacker-controlled: strip control characters and bound the length
        $value = trim((string) preg_replace('/[\x00-\x1F\x7F]/', '', $value));

        return $value === '' ? null : mb_substr($value, 0, self::MAX_VALUE);
    }
}
