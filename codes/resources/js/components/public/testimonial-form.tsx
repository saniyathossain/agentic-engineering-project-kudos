import InputError from '@/components/input-error';
import StarRating from '@/components/star-rating';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { THEME_CLASSES } from '@/lib/space-theme';
import { cn } from '@/lib/utils';
import { type OptionalFieldKey, type Space } from '@/types';
import { useForm } from '@inertiajs/react';
import { type FormEventHandler } from 'react';

interface TestimonialFormProps {
    space: Space;
}

type FormState = {
    name: string;
    email: string;
    body: string;
    rating: number | null;
    company: string;
    title: string;
    social_link: string;
    photo: File | null;
    consent: boolean;
};

const TEXT_FIELDS: ReadonlyArray<{ key: Exclude<OptionalFieldKey, 'photo'>; label: string; type: string }> = [
    { key: 'company', label: 'Company', type: 'text' },
    { key: 'title', label: 'Job title', type: 'text' },
    { key: 'social_link', label: 'Social link', type: 'url' },
];

export default function TestimonialForm({ space }: TestimonialFormProps) {
    const theme = THEME_CLASSES[space.theme];
    const { data, setData, post, errors, processing, reset } = useForm<FormState>({
        name: '',
        email: '',
        body: '',
        rating: null,
        company: '',
        title: '',
        social_link: '',
        photo: null,
        consent: false,
    });

    const submit: FormEventHandler = (event) => {
        event.preventDefault();
        post(route('public.submit', space.slug), { forceFormData: true, preserveScroll: true, onSuccess: () => reset() });
    };

    return (
        <form onSubmit={submit} className="mt-6 space-y-4" aria-label="Send a testimonial">
            {space.collect_rating && (
                <div className="grid gap-1.5">
                    <Label>Rating *</Label>
                    <StarRating value={data.rating} onChange={(value) => setData('rating', value)} className={theme.accent} />
                    <InputError message={errors.rating} />
                </div>
            )}

            <div className="grid gap-1.5">
                <Label htmlFor="body">Your testimonial *</Label>
                <Textarea id="body" required value={data.body} onChange={(e) => setData('body', e.target.value)} className={theme.input} />
                <InputError message={errors.body} />
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
                <div className="grid gap-1.5">
                    <Label htmlFor="name">Name *</Label>
                    <Input id="name" required autoComplete="name" value={data.name} onChange={(e) => setData('name', e.target.value)} className={theme.input} />
                    <InputError message={errors.name} />
                </div>
                <div className="grid gap-1.5">
                    <Label htmlFor="email">Email * (never shown publicly)</Label>
                    <Input id="email" type="email" required autoComplete="email" value={data.email} onChange={(e) => setData('email', e.target.value)} className={theme.input} />
                    <InputError message={errors.email} />
                </div>
            </div>

            {TEXT_FIELDS.filter(({ key }) => space.fields[key].enabled).map(({ key, label, type }) => (
                <div key={key} className="grid gap-1.5">
                    <Label htmlFor={key}>
                        {label}
                        {space.fields[key].required ? ' *' : ''}
                    </Label>
                    <Input id={key} type={type} required={space.fields[key].required} value={data[key]} onChange={(e) => setData(key, e.target.value)} className={theme.input} />
                    <InputError message={errors[key]} />
                </div>
            ))}

            {space.fields.photo.enabled && (
                <div className="grid gap-1.5">
                    <Label htmlFor="photo">Your photo{space.fields.photo.required ? ' *' : ''}</Label>
                    <Input id="photo" type="file" accept="image/png,image/jpeg,image/webp" required={space.fields.photo.required} onChange={(e) => setData('photo', e.target.files?.[0] ?? null)} className={theme.input} />
                    <InputError message={errors.photo} />
                </div>
            )}

            <div className="flex items-start gap-2">
                <Checkbox id="consent" checked={data.consent} onCheckedChange={(checked) => setData('consent', checked === true)} />
                <Label htmlFor="consent" className="text-sm leading-snug font-normal">
                    I give permission to use this testimonial across social channels and other marketing efforts.
                </Label>
            </div>
            <InputError message={errors.consent} />

            <Button type="submit" disabled={processing} className={cn('w-full', theme.button)}>
                {processing ? 'Sending…' : 'Send testimonial'}
            </Button>
        </form>
    );
}
