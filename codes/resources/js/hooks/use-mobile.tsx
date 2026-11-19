import { useSyncExternalStore } from 'react';

const MOBILE_BREAKPOINT = 768;
const QUERY = `(max-width: ${MOBILE_BREAKPOINT - 1}px)`;

const subscribe = (onChange: () => void): (() => void) => {
    const mql = window.matchMedia(QUERY);
    mql.addEventListener('change', onChange);

    return () => mql.removeEventListener('change', onChange);
};

const getSnapshot = (): boolean => window.matchMedia(QUERY).matches;

const getServerSnapshot = (): boolean => false;

export function useIsMobile(): boolean {
    return useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
}
