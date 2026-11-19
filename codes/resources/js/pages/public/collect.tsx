import FlashMessage from '@/components/flash-message';
import TestimonialForm from '@/components/public/testimonial-form';
import CollectionCard from '@/components/spaces/collection-card';
import { THEME_CLASSES } from '@/lib/space-theme';
import { cn } from '@/lib/utils';
import { type SharedData, type Space } from '@/types';
import { Head, usePage } from '@inertiajs/react';
import { CircleCheck } from 'lucide-react';

interface CollectProps {
    space: Space;
    accepting: boolean;
}

export default function Collect({ space, accepting }: CollectProps) {
    const { flash } = usePage<SharedData>().props;
    const thanks = flash.success !== null;
    const theme = THEME_CLASSES[space.theme];

    return (
        <>
            <Head title={space.header_title} />
            <main className={cn('flex min-h-svh flex-col items-center gap-4 px-4 py-10 sm:py-16', theme.page)}>
                <FlashMessage />
                <CollectionCard space={space}>
                    {thanks && (
                        <div className="animate-pop mt-8 flex items-start gap-3" role="status">
                            <CircleCheck className={cn('mt-0.5 size-6 shrink-0', theme.star)} strokeWidth={1.75} />
                            <p className="font-display text-xl leading-snug">Thank you. Your words are on their way to the team.</p>
                        </div>
                    )}
                    {!thanks && accepting && <TestimonialForm space={space} />}
                    {!thanks && !accepting && <p className={`mt-6 ${theme.muted}`}>This page is not accepting testimonials right now.</p>}
                </CollectionCard>
                <p className={cn('mt-auto pt-8 text-xs', theme.muted)}>Collected with Kudos</p>
            </main>
        </>
    );
}
