import { useCallback, useEffect, useRef, useState } from 'react';

const RESET_DELAY_MS = 2000;

export function useCopyToClipboard(): { copied: boolean; copy: (text: string) => Promise<void> } {
    const [copied, setCopied] = useState(false);
    const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

    useEffect(
        () => () => {
            if (timer.current) clearTimeout(timer.current);
        },
        [],
    );

    const copy = useCallback(async (text: string) => {
        await navigator.clipboard.writeText(text);
        setCopied(true);
        if (timer.current) clearTimeout(timer.current);
        timer.current = setTimeout(() => setCopied(false), RESET_DELAY_MS);
    }, []);

    return { copied, copy };
}
