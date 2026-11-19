import { router } from '@inertiajs/react';

interface NetworkInformation {
    effectiveType?: string;
}

/** Adds device facts to every Inertia visit, so the server's access log can say what kind of device asked. */
export function installClientHeaders(): void {
    router.on('before', (event) => {
        const connection = (navigator as Navigator & { connection?: NetworkInformation }).connection;
        const headers: Record<string, string> = {
            'X-Client-Timezone': Intl.DateTimeFormat().resolvedOptions().timeZone,
            'X-Client-Screen': `${window.screen.width}x${window.screen.height}`,
            'X-Client-Language': navigator.language,
        };
        if (connection?.effectiveType) {
            headers['X-Client-Connection'] = connection.effectiveType;
        }

        Object.assign(event.detail.visit.headers, headers);
    });
}
