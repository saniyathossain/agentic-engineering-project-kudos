import InputError from '@/components/input-error';
import StarRating from '@/components/star-rating';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { t, type TranslationKey } from '@/lib/i18n';
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

const TEXT_FIELDS: ReadonlyArray<{
    key: Exclude<OptionalFieldKey, 'photo'>;
    label: TranslationKey;
    type: string;
    placeholder: TranslationKey;
}> = [
    { key: 'company', label: 'collect.form.company', type: 'text', placeholder: 'collect.form.company_placeholder' },
    { key: 'title', label: 'collect.form.title', type: 'text', placeholder: 'collect.form.title_placeholder' },
    { key: 'social_link', label: 'collect.form.social_link', type: 'url', placeholder: 'collect.form.social_link_placeholder' },
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
        <form onSubmit={submit} className="mt-6 space-y-4" aria-label={t('collect.form.aria')}>
            {space.collect_rating && (
                <div className="grid gap-1.5">
                    <Label>{t('collect.form.rating')}</Label>
                    <StarRating value={data.rating} onChange={(value) => setData('rating', value)} className={theme.star} />
                    <InputError message={errors.rating} />
                </div>
            )}

            <div className="grid gap-1.5">
                <Label htmlFor="body">{t('collect.form.body')}</Label>
                <Textarea
                    id="body"
                    required
                    placeholder={t('collect.form.body_placeholder')}
                    value={data.body}
                    onChange={(e) => setData('body', e.target.value)}
                    className={theme.input}
                />
                <InputError message={errors.body} />
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
                <div className="grid gap-1.5">
                    <Label htmlFor="name">{t('collect.form.name')}</Label>
                    <Input
                        id="name"
                        required
                        autoComplete="name"
                        value={data.name}
                        onChange={(e) => setData('name', e.target.value)}
                        className={theme.input}
                    />
                    <InputError message={errors.name} />
                </div>
                <div className="grid gap-1.5">
                    <Label htmlFor="email">{t('collect.form.email')}</Label>
                    <Input
                        id="email"
                        type="email"
                        required
                        autoComplete="email"
                        value={data.email}
                        onChange={(e) => setData('email', e.target.value)}
                        className={theme.input}
                    />
                    <InputError message={errors.email} />
                </div>
            </div>

            {TEXT_FIELDS.filter(({ key }) => space.fields[key].enabled).map(({ key, label, type, placeholder }) => (
                <div key={key} className="grid gap-1.5">
                    <Label htmlFor={key}>
                        {t(label)}
                        {space.fields[key].required ? ' *' : ''}
                    </Label>
                    <Input
                        id={key}
                        type={type}
                        placeholder={t(placeholder)}
                        required={space.fields[key].required}
                        value={data[key]}
                        onChange={(e) => setData(key, e.target.value)}
                        className={theme.input}
                    />
                    <InputError message={errors[key]} />
                </div>
            ))}

            {space.fields.photo.enabled && (
                <div className="grid gap-1.5">
                    <Label htmlFor="photo">
                        {t('collect.form.photo')}
                        {space.fields.photo.required ? ' *' : ''}
                    </Label>
                    <Input
                        id="photo"
                        type="file"
                        accept="image/png,image/jpeg,image/webp"
                        required={space.fields.photo.required}
                        onChange={(e) => setData('photo', e.target.files?.[0] ?? null)}
                        className={theme.input}
                    />
                    <InputError message={errors.photo} />
                </div>
            )}

            <div className="flex items-start gap-2">
                <Checkbox
                    id="consent"
                    className="border-current/50 data-[state=checked]:border-transparent"
                    checked={data.consent}
                    onCheckedChange={(checked) => setData('consent', checked === true)}
                />
                <Label htmlFor="consent" className="text-sm leading-snug font-normal">
                    {t('collect.form.consent')}
                </Label>
            </div>
            <InputError message={errors.consent} />

            <Button type="submit" disabled={processing} size="lg" className={cn('w-full shadow-none', theme.button)}>
                {processing ? t('collect.form.sending') : t('collect.form.submit')}
            </Button>
        </form>
    );
}
