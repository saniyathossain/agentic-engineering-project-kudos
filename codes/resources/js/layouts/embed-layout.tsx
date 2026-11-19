import { type SpaceTheme } from '@/types';
import { type PropsWithChildren } from 'react';

interface EmbedThemeClasses {
    page: string;
    card: string;
}

export const EMBED_THEMES: Record<SpaceTheme, EmbedThemeClasses> = {
    light: { page: 'bg-white text-neutral-900', card: 'border-neutral-200 bg-white' },
    dark: { page: 'bg-neutral-950 text-neutral-50', card: 'border-neutral-800 bg-neutral-900' },
    brand: { page: 'bg-indigo-600 text-white', card: 'border-indigo-400 bg-indigo-500' },
};

interface EmbedLayoutProps {
    theme: SpaceTheme;
}

export default function EmbedLayout({ theme, children }: PropsWithChildren<EmbedLayoutProps>) {
    return <main className={`min-h-screen p-4 ${EMBED_THEMES[theme].page}`}>{children}</main>;
}
