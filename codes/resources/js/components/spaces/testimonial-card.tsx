import StarRating from '@/components/star-rating';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { type Testimonial, type TestimonialStatus } from '@/types';
import { router } from '@inertiajs/react';
import { Eye, EyeOff, Heart, type LucideIcon, Pencil, Send, Trash2 } from 'lucide-react';
import { useState } from 'react';

interface TestimonialCardProps {
    testimonial: Testimonial;
}

const STATUS_ACTIONS: ReadonlyArray<{ status: TestimonialStatus; label: string; icon: LucideIcon }> = [
    { status: 'published', label: 'Publish', icon: Send },
    { status: 'hidden', label: 'Hide', icon: EyeOff },
    { status: 'pending', label: 'Mark pending', icon: Eye },
];

export default function TestimonialCard({ testimonial }: TestimonialCardProps) {
    const [editing, setEditing] = useState(false);
    const [body, setBody] = useState(testimonial.body);
    const base = (name: string) => route(name, testimonial.public_id);

    const saveBody = () => router.patch(base('testimonials.update'), { body }, { preserveScroll: true, onSuccess: () => setEditing(false) });
    const remove = () => {
        if (window.confirm('Delete this testimonial permanently?')) {
            router.delete(base('testimonials.destroy'), { preserveScroll: true });
        }
    };

    return (
        <Card className="rise">
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
                    <Badge variant={testimonial.status === 'published' ? 'default' : 'secondary'}>{testimonial.status}</Badge>
                </div>

                {testimonial.rating !== null && <StarRating value={testimonial.rating} />}

                {editing ? (
                    <div className="space-y-2">
                        <Textarea value={body} onChange={(e) => setBody(e.target.value)} aria-label="Edit testimonial text" />
                        <div className="flex gap-2">
                            <Button size="sm" onClick={saveBody}>
                                Save
                            </Button>
                            <Button size="sm" variant="ghost" onClick={() => setEditing(false)}>
                                Cancel
                            </Button>
                        </div>
                    </div>
                ) : (
                    <blockquote className="font-display text-lg leading-relaxed whitespace-pre-line">{testimonial.body}</blockquote>
                )}

                <div className="flex flex-wrap gap-2">
                    {STATUS_ACTIONS.filter(({ status }) => status !== testimonial.status).map(({ status, label, icon: Icon }) => (
                        <Button
                            key={status}
                            size="sm"
                            variant="outline"
                            onClick={() => router.patch(base('testimonials.status'), { status }, { preserveScroll: true })}
                        >
                            <Icon strokeWidth={1.75} /> {label}
                        </Button>
                    ))}
                    <Button
                        size="sm"
                        variant="outline"
                        aria-pressed={testimonial.is_favorite}
                        onClick={() => router.patch(base('testimonials.favorite'), {}, { preserveScroll: true })}
                    >
                        <Heart strokeWidth={1.75} className={testimonial.is_favorite ? 'text-destructive fill-current' : ''} />
                        {testimonial.is_favorite ? 'Favorited' : 'Favorite'}
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => setEditing(true)}>
                        <Pencil strokeWidth={1.75} /> Edit
                    </Button>
                    <Button size="sm" variant="ghost" onClick={remove} aria-label="Delete testimonial">
                        <Trash2 strokeWidth={1.75} />
                    </Button>
                </div>
            </CardContent>
        </Card>
    );
}
