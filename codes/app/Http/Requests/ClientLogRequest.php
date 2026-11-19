<?php

declare(strict_types=1);

namespace App\Http\Requests;

use App\Data\Logging\ClientLogEntry;
use App\Enums\ClientLogLevel;
use Closure;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

final class ClientLogRequest extends FormRequest
{
    private const MAX_DATA_BYTES = 4000;

    /**
     * Same-origin browsers only. The endpoint is open (a beacon cannot carry a CSRF token), so it must not take
     * cross-site posts, and scripts that send neither header are refused too.
     */
    public function authorize(): bool
    {
        $site = $this->headers->get('Sec-Fetch-Site');
        if ($site !== null) {
            return in_array($site, ['same-origin', 'none'], true);
        }

        $origin = $this->headers->get('Origin');

        return $origin !== null && parse_url($origin, PHP_URL_HOST) === $this->getHost();
    }

    /** @return array<string, list<string|object>> */
    public function rules(): array
    {
        return [
            'lines' => ['required', 'array', 'min:1', 'max:20'],
            'lines.*.level' => ['required', Rule::enum(ClientLogLevel::class)],
            'lines.*.message' => ['required', 'string', 'max:500'],
            'lines.*.tag' => ['nullable', 'string', 'max:60'],
            'lines.*.url' => ['nullable', 'string', 'max:300'],
            'lines.*.data' => ['nullable', 'array', static function (string $attribute, mixed $value, Closure $fail): void {
                if (strlen((string) json_encode($value)) > self::MAX_DATA_BYTES) {
                    $fail(__('validation.max.string', ['attribute' => $attribute, 'max' => self::MAX_DATA_BYTES]));
                }
            }],
            'device' => ['nullable', 'array'],
            'device.*' => ['nullable', 'string', 'max:100'],
            'page_view_id' => ['nullable', 'string', 'max:40'],
        ];
    }

    /** @return list<ClientLogEntry> */
    public function entries(): array
    {
        /** @var list<array{level: string, message: string, tag?: ?string, url?: ?string, data?: ?array<string, mixed>}> $lines */
        $lines = $this->validated('lines');

        return array_map(static fn (array $line): ClientLogEntry => new ClientLogEntry(
            level: ClientLogLevel::from($line['level']),
            message: $line['message'],
            tag: $line['tag'] ?? null,
            url: $line['url'] ?? null,
            data: $line['data'] ?? [],
        ), $lines);
    }

    /** @return array<string, string> */
    public function device(): array
    {
        /** @var array<string, string> $device */
        $device = array_filter((array) $this->validated('device', []), static fn (mixed $v): bool => is_string($v) && $v !== '');

        return $device;
    }

    public function pageViewId(): ?string
    {
        $id = $this->validated('page_view_id');

        return is_string($id) ? $id : null;
    }
}
