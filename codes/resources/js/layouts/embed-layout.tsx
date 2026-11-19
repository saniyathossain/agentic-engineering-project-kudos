import { THEME_CLASSES } from '@/lib/space-theme';
import { cn } from '@/lib/utils';
import { type SpaceTheme } from '@/types';
import { type PropsWithChildren } from 'react';

interface EmbedLayoutProps {
    theme: SpaceTheme;
}

export default function EmbedLayout({ theme, children }: PropsWithChildren<EmbedLayoutProps>) {
    return <main className={cn('min-h-screen p-4 sm:p-6', THEME_CLASSES[theme].page, THEME_CLASSES[theme].text)}>{children}</main>;
}
