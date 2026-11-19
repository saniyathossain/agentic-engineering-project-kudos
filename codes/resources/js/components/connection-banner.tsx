import { createBackoff } from '@/lib/backoff';
import { t } from '@/lib/i18n';
import { log } from '@/lib/logger';
import { router } from '@inertiajs/react';
import { CircleCheck, WifiOff } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

interface ConnectionBannerProps {
    firstMs: number;
    longestMs: number;
}

type State = 'ok' | 'offline' | 'unreachable' | 'back';

const BACK_VISIBLE_MS = 2500;

/**
 * Shown when the browser is offline or a visit failed because the server did not answer. Checks /livez with
 * exponential backoff and clears itself (reloading the page's data) as soon as the server is back.
 */
export default function ConnectionBanner({ firstMs, longestMs }: ConnectionBannerProps) {
    const [state, setState] = useState<State>(() => (navigator.onLine ? 'ok' : 'offline'));
    const [seconds, setSeconds] = useState(0);
    const [checking, setChecking] = useState(false);
    const retryNow = useRef<() => void>(() => undefined);

    useEffect(() => {
        const goOffline = () => setState('offline');
        const goOnline = () => retryNow.current();
        const stop = router.on('networkError', () => {
            log.warn('Request failed: server unreachable', undefined, 'connection');
            setState((current) => (current === 'offline' ? current : 'unreachable'));
        });
        window.addEventListener('offline', goOffline);
        window.addEventListener('online', goOnline);

        return () => {
            stop();
            window.removeEventListener('offline', goOffline);
            window.removeEventListener('online', goOnline);
        };
    }, []);

    useEffect(() => {
        if (state !== 'unreachable' && state !== 'offline') {
            return;
        }

        const backoff = createBackoff(firstMs, longestMs);
        let timer: number | undefined;
        let nextAt = 0;
        let alive = true;

        function schedule(): void {
            const pause = backoff.next();
            nextAt = Date.now() + pause;
            timer = window.setTimeout(() => void attempt(), pause);
        }

        async function attempt(): Promise<void> {
            window.clearTimeout(timer);
            setChecking(true);
            try {
                const response = await fetch('/livez', { cache: 'no-store', credentials: 'same-origin' });
                if (response.ok && alive) {
                    setState('back');
                    router.reload();
                    window.setTimeout(() => setState('ok'), BACK_VISIBLE_MS);

                    return;
                }
            } catch {
                // still unreachable: wait for the next check
            }
            if (alive) {
                setChecking(false);
                schedule();
            }
        }

        retryNow.current = () => void attempt();
        schedule();
        const tick = window.setInterval(() => setSeconds(Math.max(0, Math.ceil((nextAt - Date.now()) / 1000))), 500);

        return () => {
            alive = false;
            window.clearTimeout(timer);
            window.clearInterval(tick);
        };
    }, [state, firstMs, longestMs]);

    if (state === 'ok') {
        return null;
    }

    const recovered = state === 'back';

    return (
        <div
            role="status"
            aria-live="polite"
            className="frost animate-pop fixed inset-x-4 bottom-4 z-50 mx-auto flex max-w-md items-center gap-3 rounded-2xl p-3 pl-4 text-sm"
        >
            {recovered ? (
                <CircleCheck className="text-success size-5 shrink-0" strokeWidth={1.75} />
            ) : (
                <WifiOff className="text-destructive size-5 shrink-0" strokeWidth={1.75} />
            )}
            <div className="min-w-0 flex-1">
                <p className="font-medium">
                    {recovered ? t('connection.back') : state === 'offline' ? t('connection.offline') : t('connection.unreachable')}
                </p>
                {!recovered && <p className="text-ink-3 text-xs">{checking ? t('connection.checking') : t('connection.retry_in', { seconds })}</p>}
            </div>
            {!recovered && (
                <button type="button" onClick={() => retryNow.current()} className="hover:bg-accent rounded-lg px-3 py-1.5 text-xs font-medium">
                    {t('connection.retry_now')}
                </button>
            )}
        </div>
    );
}
