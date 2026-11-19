import { useCallback, useState } from 'react';

const RESET_AFTER_MS = 2000;

export function useClipboard(): { copied: boolean; copy: (text: string) => Promise<void> } {
    const [copied, setCopied] = useState(false);

    const copy = useCallback(async (text: string): Promise<void> => {
        await navigator.clipboard.writeText(text);
        setCopied(true);
        window.setTimeout(() => setCopied(false), RESET_AFTER_MS);
    }, []);

    return { copied, copy };
}
