import StarRating from '@/components/embed/star-rating';
import { type EmbedTestimonial } from '@/types';

interface EmbedTestimonialCardProps {
    testimonial: EmbedTestimonial;
    cardClassName: string;
}

export default function EmbedTestimonialCard({ testimonial, cardClassName }: EmbedTestimonialCardProps) {
    const byline = [testimonial.title, testimonial.company].filter(Boolean).join(' at ');

    return (
        <figure className={`flex flex-col gap-3 rounded-xl border p-5 ${cardClassName}`}>
            {testimonial.rating !== null && <StarRating rating={testimonial.rating} />}
            <blockquote className="text-sm leading-relaxed whitespace-pre-line">{testimonial.body}</blockquote>
            <figcaption className="mt-auto flex items-center gap-3">
                {testimonial.photo_url && <img src={testimonial.photo_url} alt="" className="size-10 rounded-full object-cover" loading="lazy" />}
                <div className="text-sm">
                    <div className="font-semibold">{testimonial.respondent_name}</div>
                    {byline && <div className="text-xs opacity-70">{byline}</div>}
                </div>
            </figcaption>
        </figure>
    );
}
