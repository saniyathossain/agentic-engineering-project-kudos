import EmbedTestimonialCard from '@/components/embed/embed-testimonial-card';
import EmbedLayout from '@/layouts/embed-layout';
import { t } from '@/lib/i18n';
import { type EmbedSpace, type EmbedTestimonial } from '@/types';
import { Head } from '@inertiajs/react';
import { type CSSProperties } from 'react';

interface WallProps {
    space: EmbedSpace;
    testimonials: EmbedTestimonial[];
}

export default function Wall({ space, testimonials }: WallProps) {
    return (
        <EmbedLayout theme={space.theme}>
            <Head title={t('embed.wall_title', { name: space.name })} />
            {testimonials.length === 0 ? (
                <p className="py-12 text-center text-sm opacity-70">{t('embed.empty')}</p>
            ) : (
                <div className="columns-1 gap-4 space-y-4 sm:columns-2 lg:columns-3">
                    {testimonials.map((testimonial, index) => (
                        <div key={testimonial.public_id} className="rise break-inside-avoid" style={{ '--i': index } as CSSProperties}>
                            <EmbedTestimonialCard testimonial={testimonial} theme={space.theme} />
                        </div>
                    ))}
                </div>
            )}
        </EmbedLayout>
    );
}
