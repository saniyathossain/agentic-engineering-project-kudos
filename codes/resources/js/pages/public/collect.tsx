import FlashMessage from '@/components/flash-message';
import TestimonialForm from '@/components/public/testimonial-form';
import CollectionCard from '@/components/spaces/collection-card';
import { THEME_CLASSES } from '@/lib/space-theme';
import { type SharedData, type Space } from '@/types';
import { Head, usePage } from '@inertiajs/react';

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
            <main className="flex min-h-svh flex-col items-center gap-4 bg-neutral-100 px-4 py-10 dark:bg-neutral-950">
                <FlashMessage />
                <CollectionCard space={space}>
                    {thanks && <p className={`mt-6 text-lg font-medium ${theme.text}`}>Thank you! 🙏 Your testimonial means a lot to us.</p>}
                    {!thanks && accepting && <TestimonialForm space={space} />}
                    {!thanks && !accepting && <p className={`mt-6 ${theme.muted}`}>This page is not accepting testimonials right now.</p>}
                </CollectionCard>
            </main>
        </>
    );
}
