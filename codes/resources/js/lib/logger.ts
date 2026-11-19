/**
 * Browser logger. Lines are batched and sent to POST /client-logs, where the server writes them into the same
 * JSON stream as its own logs (source=browser). Device facts it cannot send as headers travel in `device`.
 */
export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogLine {
    level: LogLevel;
    message: string;
    tag?: string;
    url: string;
    data?: Record<string, unknown>;
}

const ENDPOINT = '/client-logs';
const FLUSH_MS = 3000;
const ERROR_FLUSH_MS = 300;
const MAX_BATCH = 20;
const MAX_QUEUE = 100;
const DEDUPE_MS = 5000;

const pageViewId = Math.random().toString(36).slice(2, 12) + Date.now().toString(36);
const queue: LogLine[] = [];
const recent = new Map<string, number>();
let timer: number | undefined;

interface NetworkInformation {
    effectiveType?: string;
}

const device = (): Record<string, string> => {
    const connection = (navigator as Navigator & { connection?: NetworkInformation }).connection;
    const hints = (navigator as Navigator & { userAgentData?: { platform?: string } }).userAgentData;

    return Object.fromEntries(
        Object.entries({
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            screen: `${window.screen.width}x${window.screen.height}`,
            viewport: `${window.innerWidth}x${window.innerHeight}`,
            language: navigator.language,
            connection: connection?.effectiveType,
            platform: hints?.platform,
        }).filter((entry): entry is [string, string] => typeof entry[1] === 'string' && entry[1] !== ''),
    );
};

function flush(): void {
    window.clearTimeout(timer);
    timer = undefined;
    if (queue.length === 0) {
        return;
    }

    const body = JSON.stringify({ lines: queue.splice(0, MAX_BATCH), device: device(), page_view_id: pageViewId });
    const blob = new Blob([body], { type: 'application/json' });

    // sendBeacon survives page unloads; fall back to a keepalive fetch where it is unavailable or refuses
    if (!navigator.sendBeacon?.(ENDPOINT, blob)) {
        void fetch(ENDPOINT, { method: 'POST', body, headers: { 'Content-Type': 'application/json' }, keepalive: true }).catch(() => undefined);
    }
    if (queue.length > 0) {
        timer = window.setTimeout(flush, ERROR_FLUSH_MS);
    }
}

function enqueue(level: LogLevel, message: string, tag?: string, data?: Record<string, unknown>): void {
    const key = `${level}|${tag ?? ''}|${message}`;
    const now = Date.now();
    if (now - (recent.get(key) ?? 0) < DEDUPE_MS) {
        return; // the same failure repeating (a render loop, a flaky poll) must not flood the log
    }
    recent.set(key, now);

    if (queue.length >= MAX_QUEUE) {
        queue.shift();
    }
    queue.push({ level, message: message.slice(0, 500), tag, url: window.location.pathname, data });
    if (timer === undefined) {
        timer = window.setTimeout(flush, level === 'error' ? ERROR_FLUSH_MS : FLUSH_MS);
    }
}

export const log = {
    debug: (message: string, data?: Record<string, unknown>, tag?: string) => enqueue('debug', message, tag, data),
    info: (message: string, data?: Record<string, unknown>, tag?: string) => enqueue('info', message, tag, data),
    warn: (message: string, data?: Record<string, unknown>, tag?: string) => enqueue('warn', message, tag, data),
    error: (message: string, data?: Record<string, unknown>, tag?: string) => enqueue('error', message, tag, data),
};

const describe = (reason: unknown): { message: string; stack?: string } =>
    reason instanceof Error
        ? { message: `${reason.name}: ${reason.message}`, stack: reason.stack?.split('\n').slice(0, 8).join('\n') }
        : { message: String(reason) };

/** Catches what nothing else does: uncaught errors and unhandled promise rejections. Call once at start-up. */
export function installGlobalErrorLogging(): void {
    window.addEventListener('error', (event) => {
        log.error(
            event.message || 'Uncaught error',
            { source: event.filename, line: event.lineno, column: event.colno, ...describe(event.error) },
            'window.onerror',
        );
    });
    window.addEventListener('unhandledrejection', (event) => {
        log.error(describe(event.reason).message, describe(event.reason), 'unhandledrejection');
    });
    // last chance for anything still queued
    window.addEventListener('pagehide', flush);
    document.addEventListener('visibilitychange', () => document.visibilityState === 'hidden' && flush());
}
