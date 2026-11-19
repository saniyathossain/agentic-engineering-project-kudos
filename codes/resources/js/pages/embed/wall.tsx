import EmbedTestimonialCard from '@/components/embed/embed-testimonial-card';
import EmbedLayout, { EMBED_THEMES } from '@/layouts/embed-layout';
import { type EmbedSpace, type EmbedTestimonial } from '@/types';
import { Head } from '@inertiajs/react';

interface WallProps {
    space: EmbedSpace;
    testimonials: EmbedTestimonial[];
}

export default function Wall({ space, testimonials }: WallProps) {
    const theme = EMBED_THEMES[space.theme];

    return (
        <EmbedLayout theme={space.theme}>
            <Head title={`${space.name} - Wall of love`} />
            {testimonials.length === 0 ? (
                <p className="py-12 text-center text-sm opacity-70">No testimonials yet.</p>
            ) : (
                <div className="columns-1 gap-4 space-y-4 sm:columns-2 lg:columns-3">
                    {testimonials.map((testimonial) => (
                        <div key={testimonial.public_id} className="break-inside-avoid">
                            <EmbedTestimonialCard testimonial={testimonial} cardClassName={theme.card} />
                        </div>
                    ))}
                </div>
            )}
        </EmbedLayout>
    );
}
