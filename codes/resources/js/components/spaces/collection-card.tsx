import MarkdownText from '@/components/markdown-text';
import { t } from '@/lib/i18n';
import { THEME_CLASSES } from '@/lib/space-theme';
import { cn } from '@/lib/utils';
import { type FieldsConfig, type SpaceTheme } from '@/types';
import { type ReactNode } from 'react';

export interface CollectionCardSpace {
    logo_url: string | null;
    header_title: string;
    message: string;
    theme: SpaceTheme;
    collect_rating: boolean;
    fields: FieldsConfig;
}

interface CollectionCardProps {
    space: CollectionCardSpace;
    children?: ReactNode;
}

/** The themed card respondents see; also the live preview in the space form. */
export default function CollectionCard({ space, children }: CollectionCardProps) {
    const theme = THEME_CLASSES[space.theme];

    return (
        <section className={cn('rise w-full max-w-xl rounded-3xl border p-6 sm:p-8', theme.surface, theme.text)}>
            {space.logo_url && <img src={space.logo_url} alt="" className="mb-5 size-14 rounded-2xl object-cover" />}
            <h2 className="font-display text-3xl leading-tight font-medium">{space.header_title || t('spaces.card.header_placeholder')}</h2>
            <MarkdownText className={cn('mt-3 space-y-2 text-[0.95rem] leading-relaxed', theme.muted)}>
                {space.message || t('spaces.card.message_placeholder')}
            </MarkdownText>
            {children}
        </section>
    );
}
