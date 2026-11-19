<?php

declare(strict_types=1);

namespace App\Logging;

use Monolog\Formatter\FormatterInterface;
use Monolog\Level;
use Monolog\LogRecord;
use Throwable;

/**
 * One JSON object per line, grouped by the five W questions (same shape as Shell Console):
 *   who   - actor, user id, ip
 *   what  - event, outcome (ok | refused | degraded | failed), status, error / exception
 *   where - service, role, host, route, path, and the source line for warnings and errors
 *   when  - timestamp and request duration
 *   why   - reason and hint
 * plus request_id / trace_id, the caller's device ("client") and any remaining context.
 *
 * Context keys the formatter understands: event, outcome, status, reason, hint, duration_ms, exception.
 */
final readonly class FiveWFormatter implements FormatterInterface
{
    private const REDACTED = '[redacted]';

    private const CONSUMED = ['event', 'outcome', 'status', 'reason', 'hint', 'duration_ms', 'exception', 'error', 'bytes'];

    public function format(LogRecord $record): string
    {
        $context = $this->redact($record->context);
        $extra = $record->extra;
        $exception = $record->context['exception'] ?? null;
        $failed = $record->level->value >= Level::Error->value;

        $line = [
            'time' => $record->datetime->format('Y-m-d\TH:i:s.vP'),
            'level' => $record->level->getName(),
            'msg' => $this->limit((string) $record->message),
            'who' => $this->who($extra),
            'what' => $this->what($record, $context, $exception instanceof Throwable ? $exception : null),
            'where' => $this->where($record, $extra, $exception instanceof Throwable ? $exception : null, $failed),
            'when' => $this->group(['duration_ms' => $context['duration_ms'] ?? $extra['duration_ms'] ?? null]),
            'why' => $this->group(['reason' => $context['reason'] ?? null, 'hint' => $context['hint'] ?? null]),
        ];

        foreach (['request_id', 'trace_id'] as $key) {
            if (isset($extra[$key])) {
                $line[$key] = $extra[$key];
            }
        }
        if (isset($extra['client']) && $extra['client'] !== []) {
            $line['client'] = $extra['client'];
        }

        $rest = array_diff_key($context, array_flip(self::CONSUMED));
        if ($rest !== []) {
            $line['context'] = $rest;
        }

        return json_encode($line, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_INVALID_UTF8_SUBSTITUTE | JSON_PARTIAL_OUTPUT_ON_ERROR)."\n";
    }

    /**
     * Drop nulls; an empty group stays a JSON object ({}), never an array ([]).
     *
     * @param  array<string, mixed>  $values
     */
    private function group(array $values): object
    {
        return (object) array_filter($values, static fn (mixed $v): bool => $v !== null);
    }

    /** @param  array<int, LogRecord>  $records */
    public function formatBatch(array $records): string
    {
        return implode('', array_map($this->format(...), $records));
    }

    /**
     * @param  array<string, mixed>  $extra
     * @return array<string, mixed>
     */
    private function who(array $extra): array
    {
        $actor = isset($extra['user_id']) ? 'user' : (isset($extra['request_id']) ? 'guest' : 'process');

        return array_filter([
            'actor' => $actor,
            'user_id' => $extra['user_id'] ?? null,
            'ip' => $extra['ip'] ?? null,
        ], static fn (mixed $v): bool => $v !== null);
    }

    /**
     * @param  array<int|string, mixed>  $context
     * @return array<string, mixed>
     */
    private function what(LogRecord $record, array $context, ?Throwable $exception): array
    {
        $outcome = $context['outcome'] ?? match (true) {
            $record->level->value >= Level::Error->value => 'failed',
            $record->level->value >= Level::Warning->value => 'degraded',
            default => 'ok',
        };

        return array_filter([
            'event' => $context['event'] ?? null,
            'outcome' => $outcome,
            'status' => $context['status'] ?? null,
            'bytes' => $context['bytes'] ?? null,
            'error' => isset($context['error']) ? $this->limit((string) $context['error']) : ($exception?->getMessage() === null ? null : $this->limit($exception->getMessage())),
            'exception' => $exception === null ? null : $this->exception($exception),
        ], static fn (mixed $v): bool => $v !== null);
    }

    /**
     * @param  array<string, mixed>  $extra
     * @return array<string, mixed>
     */
    private function where(LogRecord $record, array $extra, ?Throwable $exception, bool $failed): array
    {
        $where = [
            'service' => config('observability.service'),
            'role' => config('observability.role'),
            'version' => config('observability.version'),
            'env' => config('app.env'),
            'host' => gethostname() ?: null,
            'pid' => getmypid(),
            'method' => $extra['method'] ?? null,
            'path' => $extra['path'] ?? null,
            'route' => $this->route(),
        ];

        if ($exception !== null) {
            $where['source'] = $this->relative($exception->getFile()).':'.$exception->getLine();
        } elseif ($record->level->value >= Level::Warning->value && isset($extra['file'], $extra['line'])) {
            $where['source'] = $this->relative((string) $extra['file']).':'.$extra['line'];
            $where['func'] = ($extra['class'] ?? '').($extra['callType'] ?? '').($extra['function'] ?? '');
        }

        return array_filter($where, static fn (mixed $v): bool => $v !== null && $v !== '');
    }

    private function route(): ?string
    {
        if (! app()->bound('request')) {
            return null;
        }

        return request()->route()?->uri();
    }

    /** @return array<string, mixed> */
    private function exception(Throwable $e): array
    {
        $limit = (int) config('observability.trace_limit', 10);
        $trace = array_map(
            fn (array $frame): string => $this->relative((string) ($frame['file'] ?? '[internal]')).':'.($frame['line'] ?? 0).' '.($frame['class'] ?? '').($frame['type'] ?? '').$frame['function'],
            array_slice($e->getTrace(), 0, $limit),
        );

        $previous = $e->getPrevious();

        return array_filter([
            'class' => $e::class,
            'message' => $this->limit($e->getMessage()),
            'code' => $e->getCode() === 0 ? null : $e->getCode(),
            'file' => $this->relative($e->getFile()).':'.$e->getLine(),
            'previous' => $previous === null ? null : $previous::class.': '.$this->limit($previous->getMessage()),
            'trace' => $trace,
        ], static fn (mixed $v): bool => $v !== null);
    }

    /**
     * @param  array<string|int, mixed>  $data
     * @return array<string|int, mixed>
     */
    private function redact(array $data): array
    {
        $fragments = (array) config('observability.redact', []);
        $out = [];
        foreach ($data as $key => $value) {
            if ($value instanceof Throwable) {
                $out[$key] = $value;

                continue;
            }
            if (is_string($key) && $this->sensitive($key, $fragments)) {
                $out[$key] = self::REDACTED;

                continue;
            }
            $out[$key] = is_array($value) ? $this->redact($value) : $value;
        }

        return $out;
    }

    /** @param  array<int|string, mixed>  $fragments */
    private function sensitive(string $key, array $fragments): bool
    {
        $lower = strtolower($key);
        foreach ($fragments as $fragment) {
            if (str_contains($lower, (string) $fragment)) {
                return true;
            }
        }

        return false;
    }

    private function relative(string $path): string
    {
        return str_starts_with($path, base_path()) ? ltrim(substr($path, strlen(base_path())), '/') : $path;
    }

    private function limit(string $text): string
    {
        $max = (int) config('observability.message_limit', 2000);

        return mb_strlen($text) > $max ? mb_substr($text, 0, $max).'…' : $text;
    }
}
