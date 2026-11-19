<?php

declare(strict_types=1);

namespace App\Support\Logging;

/**
 * Last line of defence against secrets and personal data reaching the logs. Context KEYS are redacted by the
 * formatter; this scrubs VALUES: free text (exception messages can embed SQL bindings, emails, keys) and URL paths
 * (reset and verification links carry tokens in the path).
 */
final class Scrub
{
    private const TOKEN_LENGTH = 32;

    /** @var array<string, string> pattern => replacement */
    private const TEXT_RULES = [
        '/[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}/' => '[email]',
        '/\$2[aby]\$\d{2}\$[.\/A-Za-z0-9]{53}/' => '[hash]',
        '/\$argon2[a-z]*\$[^\s\'"]+/' => '[hash]',
        '/\b(?:sk|pk|rk|whsec)_(?:live_|test_)?[A-Za-z0-9]{8,}\b/' => '[key]',
        '/Bearer\s+[A-Za-z0-9._\-]+/i' => 'Bearer [token]',
        '/\b[A-Za-z0-9_\-]{40,}\b/' => '[token]',
    ];

    public static function text(string $text): string
    {
        return (string) preg_replace(array_keys(self::TEXT_RULES), array_values(self::TEXT_RULES), $text);
    }

    /** A URL or path without its query string or fragment, and with long token-like segments masked. */
    public static function path(string $url): string
    {
        $path = (string) strtok($url, '?#');
        $parts = parse_url($path);
        $onlyPath = is_array($parts) && isset($parts['path']) ? $parts['path'] : $path;

        return implode('/', array_map(
            static fn (string $segment): string => preg_match('/^[A-Za-z0-9_\-]{'.self::TOKEN_LENGTH.',}$/', $segment) === 1 ? '[redacted]' : $segment,
            explode('/', $onlyPath),
        ));
    }

    /**
     * @param  array<array-key, mixed>  $data
     * @return array<array-key, mixed>
     */
    public static function deep(array $data): array
    {
        return array_map(static fn (mixed $value): mixed => match (true) {
            is_string($value) => self::text($value),
            is_array($value) => self::deep($value),
            default => $value,
        }, $data);
    }
}
