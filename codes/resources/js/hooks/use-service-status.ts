import { useEffect, useState } from 'react';

export type ServiceStatus = 'checking' | 'operational' | 'degraded' | 'unreachable';

const POLL_MS = 60_000;
const TIMEOUT_MS = 4_000;

async function probe(): Promise<ServiceStatus> {
    try {
        const response = await fetch('/readyz', { cache: 'no-store', credentials: 'same-origin', signal: AbortSignal.timeout(TIMEOUT_MS) });

        return response.ok ? 'operational' : 'degraded';
    } catch {
        return 'unreachable';
    }
}

/** Live service status for the footer: checked once on mount, then every minute while the tab is visible. */
export function useServiceStatus(): ServiceStatus {
    const [status, setStatus] = useState<ServiceStatus>('checking');

    useEffect(() => {
        let alive = true;
        const check = async () => {
            if (document.visibilityState === 'hidden') {
                return;
            }
            const next = await probe();
            if (alive) {
                setStatus(next);
            }
        };

        void check();
        const timer = window.setInterval(() => void check(), POLL_MS);
        document.addEventListener('visibilitychange', check);

        return () => {
            alive = false;
            window.clearInterval(timer);
            document.removeEventListener('visibilitychange', check);
        };
    }, []);

    return status;
}
