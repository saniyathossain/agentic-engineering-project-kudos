import StarRating from '@/components/star-rating';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Chip } from '@/components/ui/chip';
import { Textarea } from '@/components/ui/textarea';
import { formatTimestamp } from '@/lib/dates';
import { t, tDynamic, type TranslationKey } from '@/lib/i18n';
import { cn } from '@/lib/utils';
import { type Testimonial, type TestimonialStatus } from '@/types';
import { router } from '@inertiajs/react';
import { CalendarDays, Eye, EyeOff, Heart, type LucideIcon, Pencil, Send, Trash2 } from 'lucide-react';
import { useState } from 'react';

interface TestimonialCardProps {
    testimonial: Testimonial;
}

const STATUS_TONE = { published: 'success', pending: 'warning', hidden: 'neutral' } as const;

const STATUS_ACTIONS: ReadonlyArray<{ status: TestimonialStatus; label: TranslationKey; icon: LucideIcon; anim: string }> = [
    { status: 'published', label: 'inbox.action.publish', icon: Send, anim: 'ico-send' },
    { status: 'hidden', label: 'inbox.action.hide', icon: EyeOff, anim: 'ico-eye' },
    { status: 'pending', label: 'inbox.action.mark_pending', icon: Eye, anim: 'ico-eye' },
];

export default function TestimonialCard({ testimonial }: TestimonialCardProps) {
    const [editing, setEditing] = useState(false);
    const [body, setBody] = useState(testimonial.body);
    const base = (name: string) => route(name, testimonial.public_id);

    const saveBody = () => router.patch(base('testimonials.update'), { body }, { preserveScroll: true, onSuccess: () => setEditing(false) });
    const remove = () => {
        if (window.confirm(t('inbox.action.delete_confirm'))) {
            router.delete(base('testimonials.destroy'), { preserveScroll: true });
        }
    };

    return (
        <Card className="rise lift cv-auto">
            <CardContent className="space-y-4 p-5 sm:p-6">
                <div className="flex items-start justify-between gap-2">
                    <div>
                        <p className="font-semibold">{testimonial.respondent_name}</p>
                        <p className="text-muted-foreground text-sm">
                            {testimonial.respondent_email}
                            {testimonial.company ? ` · ${testimonial.company}` : ''}
                            {testimonial.title ? ` · ${testimonial.title}` : ''}
                        </p>
                    </div>
                    <Chip tone={STATUS_TONE[testimonial.status]} dot>
                        {tDynamic(`inbox.status.${testimonial.status}`)}
                    </Chip>
                </div>

                <div className="flex flex-wrap items-center gap-3">
                    {testimonial.rating !== null && <StarRating value={testimonial.rating} />}
                    <Chip icon={CalendarDays} tone="outline">
                        {formatTimestamp(testimonial.submitted_at)}
                    </Chip>
                </div>

                {editing ? (
                    <div className="space-y-2">
                        <Textarea value={body} onChange={(e) => setBody(e.target.value)} aria-label={t('inbox.edit_aria')} />
                        <div className="flex gap-2">
                            <Button size="sm" onClick={saveBody}>
                                {t('common.save')}
                            </Button>
                            <Button size="sm" variant="ghost" onClick={() => setEditing(false)}>
                                {t('common.cancel')}
                            </Button>
                        </div>
                    </div>
                ) : (
                    <blockquote className="font-display text-lg leading-relaxed whitespace-pre-line">{testimonial.body}</blockquote>
                )}

                <div className="flex flex-wrap gap-2">
                    {STATUS_ACTIONS.filter(({ status }) => status !== testimonial.status).map(({ status, label, icon: Icon, anim }) => (
                        <Button
                            key={status}
                            size="sm"
                            variant="outline"
                            onClick={() => router.patch(base('testimonials.status'), { status }, { preserveScroll: true })}
                        >
                            <Icon strokeWidth={1.75} className={anim} /> {t(label)}
                        </Button>
                    ))}
                    <Button
                        size="sm"
                        variant="outline"
                        aria-pressed={testimonial.is_favorite}
                        onClick={() => router.patch(base('testimonials.favorite'), {}, { preserveScroll: true })}
                    >
                        <Heart strokeWidth={1.75} className={cn('ico-heart', testimonial.is_favorite && 'text-destructive fill-current')} />
                        {testimonial.is_favorite ? t('inbox.action.favorited') : t('inbox.action.favorite')}
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => setEditing(true)}>
                        <Pencil strokeWidth={1.75} className="ico-pencil" /> {t('common.edit')}
                    </Button>
                    <Button size="sm" variant="ghost" onClick={remove} aria-label={t('inbox.action.delete_aria')}>
                        <Trash2 strokeWidth={1.75} className="ico-trash" />
                    </Button>
                </div>
            </CardContent>
        </Card>
    );
}
