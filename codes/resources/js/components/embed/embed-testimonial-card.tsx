import StarRating from '@/components/star-rating';
import { t } from '@/lib/i18n';
import { THEME_CLASSES } from '@/lib/space-theme';
import { cn } from '@/lib/utils';
import { type EmbedTestimonial, type SpaceTheme } from '@/types';

interface EmbedTestimonialCardProps {
    testimonial: EmbedTestimonial;
    theme: SpaceTheme;
}

export default function EmbedTestimonialCard({ testimonial, theme }: EmbedTestimonialCardProps) {
    const classes = THEME_CLASSES[theme];
    const byline =
        testimonial.title && testimonial.company
            ? t('embed.byline', { title: testimonial.title, company: testimonial.company })
            : (testimonial.title ?? testimonial.company);

    return (
        <figure className={cn('flex flex-col gap-4 rounded-2xl border p-5', classes.surface)}>
            {testimonial.rating !== null && <StarRating value={testimonial.rating} className={classes.star} />}
            <blockquote className="font-display text-[1.05rem] leading-relaxed whitespace-pre-line">{testimonial.body}</blockquote>
            <figcaption className="mt-auto flex items-center gap-3">
                {testimonial.photo_url && <img src={testimonial.photo_url} alt="" className="size-10 rounded-full object-cover" loading="lazy" />}
                <div className="text-sm">
                    <div className="font-semibold">{testimonial.respondent_name}</div>
                    {byline && <div className={cn('text-xs', classes.muted)}>{byline}</div>}
                </div>
            </figcaption>
        </figure>
    );
}
