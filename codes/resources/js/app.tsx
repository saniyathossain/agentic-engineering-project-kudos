import '../css/app.css';

import { createInertiaApp, router } from '@inertiajs/react';
import { createRoot } from 'react-dom/client';
import { route as routeFn } from 'ziggy-js';
import AppErrorBoundary from './components/app-error-boundary';
import ConnectionBanner from './components/connection-banner';
import { initializeTheme } from './hooks/use-appearance';
import { installClientHeaders } from './lib/client-headers';
import { setLocale } from './lib/i18n';
import { installGlobalErrorLogging } from './lib/logger';

declare global {
    const route: typeof routeFn;
}

interface BootProps {
    locale?: string;
    name?: string;
    resilience?: { first_ms: number; longest_ms: number };
}

const appName = import.meta.env.VITE_APP_NAME || 'Kudos';

installGlobalErrorLogging();
installClientHeaders();
initializeTheme();

// Content dims slightly while the next page loads (see app.css)
router.on('start', () => document.documentElement.setAttribute('data-navigating', 'true'));
router.on('finish', () => document.documentElement.removeAttribute('data-navigating'));

void createInertiaApp({
    title: (title) => `${title} - ${appName}`,
    resolve: async (name) => {
        const pages = import.meta.glob<{ default: React.ComponentType }>('./pages/**/*.tsx');
        const page = pages[`./pages/${name}.tsx`];
        if (page === undefined) {
            throw new Error(`Page not found: ${name}`);
        }

        return (await page()).default;
    },
    async setup({ el, App, props }) {
        const shared = props.initialPage.props as BootProps;
        await setLocale(shared.locale ?? document.documentElement.lang.slice(0, 2));

        createRoot(el).render(
            <AppErrorBoundary>
                <App {...props} />
                <ConnectionBanner firstMs={shared.resilience?.first_ms ?? 4000} longestMs={shared.resilience?.longest_ms ?? 15000} />
            </AppErrorBoundary>,
        );
    },
    progress: {
        color: 'oklch(0.54 0.18 35)',
    },
});
