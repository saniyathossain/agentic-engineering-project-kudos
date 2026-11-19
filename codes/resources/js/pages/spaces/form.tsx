import InputError from '@/components/input-error';
import PageHeader from '@/components/page-header';
import CollectionCard from '@/components/spaces/collection-card';
import OptionalFieldRow from '@/components/spaces/optional-field-row';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Chip } from '@/components/ui/chip';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import AppLayout from '@/layouts/app-layout';
import { t, type TranslationKey } from '@/lib/i18n';
import { cn } from '@/lib/utils';
import { type BreadcrumbItem, type FieldConfig, type FieldsConfig, type OptionalFieldKey, type Space, type SpaceTheme } from '@/types';
import { Head, Link, useForm } from '@inertiajs/react';
import { type FormEventHandler, useMemo } from 'react';

interface ThemeOption {
    value: SpaceTheme;
    label: string;
}

interface FormProps {
    space: Space | null;
    themes: ThemeOption[];
    optionalFields: OptionalFieldKey[];
}

type SpaceFormState = {
    name: string;
    header_title: string;
    message: string;
    collect_rating: boolean;
    theme: SpaceTheme;
    is_accepting: boolean;
    fields: FieldsConfig;
    logo: File | null;
};

const FIELD_LABELS: Record<OptionalFieldKey, TranslationKey> = {
    company: 'spaces.form.field.company',
    title: 'spaces.form.field.title',
    social_link: 'spaces.form.field.social_link',
    photo: 'spaces.form.field.photo',
};

const THEME_SWATCH: Record<SpaceTheme, string> = {
    light: 'bg-[oklch(0.975_0.011_78)]',
    dark: 'bg-[oklch(0.24_0.013_55)]',
    brand: 'bg-[oklch(0.6_0.14_40)]',
};

const EMPTY_FIELD: FieldConfig = { enabled: false, required: false };

function initialState(space: Space | null, optionalFields: OptionalFieldKey[]): SpaceFormState {
    const fields = Object.fromEntries(optionalFields.map((key) => [key, space?.fields[key] ?? EMPTY_FIELD])) as FieldsConfig;

    return {
        name: space?.name ?? '',
        header_title: space?.header_title ?? '',
        message: space?.message ?? '',
        collect_rating: space?.collect_rating ?? true,
        theme: space?.theme ?? 'light',
        is_accepting: space?.is_accepting ?? true,
        fields,
        logo: null,
    };
}

export default function SpaceForm({ space, themes, optionalFields }: FormProps) {
    const isEditing = space !== null;
    const { data, setData, post, errors, processing, transform } = useForm<SpaceFormState>(initialState(space, optionalFields));
    const breadcrumbs: BreadcrumbItem[] = [
        { title: t('spaces.index.title'), href: '/spaces' },
        { title: isEditing ? t('spaces.form.breadcrumb_edit') : t('spaces.form.breadcrumb_new'), href: '#' },
    ];

    const logoPreview = useMemo(() => (data.logo ? URL.createObjectURL(data.logo) : (space?.logo_url ?? null)), [data.logo, space?.logo_url]);

    const submit: FormEventHandler = (event) => {
        event.preventDefault();
        if (isEditing) {
            transform((payload) => ({ ...payload, _method: 'put' }));
            post(route('spaces.update', space.public_id), { forceFormData: true });
            return;
        }
        post(route('spaces.store'), { forceFormData: true });
    };

    return (
        <AppLayout breadcrumbs={breadcrumbs}>
            <Head title={isEditing ? t('spaces.form.title_edit') : t('spaces.form.title_new')} />
            <div className="mx-auto flex w-full max-w-6xl flex-col gap-6 p-4 sm:p-6">
                <PageHeader title={isEditing ? t('spaces.form.title_edit') : t('spaces.form.title_new')} description={t('spaces.form.description')} />
                <div className="grid items-start gap-6 lg:grid-cols-2">
                    <form onSubmit={submit} className="pane rise space-y-5 rounded-2xl p-5 sm:p-6" aria-label={t('spaces.form.aria')}>
                        <div className="grid gap-1.5">
                            <Label htmlFor="name">{t('spaces.form.name')}</Label>
                            <Input
                                id="name"
                                required
                                placeholder={t('spaces.form.name_placeholder')}
                                value={data.name}
                                onChange={(e) => setData('name', e.target.value)}
                            />
                            <InputError message={errors.name} />
                        </div>
                        <div className="grid gap-1.5">
                            <Label htmlFor="header_title">{t('spaces.form.header_title')}</Label>
                            <Input
                                id="header_title"
                                required
                                placeholder={t('spaces.form.header_title_placeholder')}
                                value={data.header_title}
                                onChange={(e) => setData('header_title', e.target.value)}
                            />
                            <InputError message={errors.header_title} />
                        </div>
                        <div className="grid gap-1.5">
                            <Label htmlFor="message">{t('spaces.form.message')}</Label>
                            <Textarea
                                id="message"
                                required
                                placeholder={t('spaces.form.message_placeholder')}
                                value={data.message}
                                onChange={(e) => setData('message', e.target.value)}
                            />
                            <InputError message={errors.message} />
                        </div>
                        <div className="grid gap-1.5">
                            <Label htmlFor="logo">{t('spaces.form.logo')}</Label>
                            <Input
                                id="logo"
                                type="file"
                                accept="image/png,image/jpeg,image/webp"
                                onChange={(e) => setData('logo', e.target.files?.[0] ?? null)}
                            />
                            <InputError message={errors.logo} />
                        </div>

                        <fieldset className="space-y-2">
                            <legend className="text-sm font-medium">{t('spaces.form.fields_legend')}</legend>
                            <p className="text-muted-foreground text-sm">{t('spaces.form.fields_note')}</p>
                            {optionalFields.map((key) => (
                                <OptionalFieldRow
                                    key={key}
                                    id={key}
                                    label={t(FIELD_LABELS[key])}
                                    config={data.fields[key]}
                                    onChange={(config) => setData('fields', { ...data.fields, [key]: config })}
                                />
                            ))}
                        </fieldset>

                        <div className="grid gap-1.5">
                            <Label>{t('spaces.form.theme')}</Label>
                            <div className="flex flex-wrap gap-2" role="radiogroup" aria-label={t('spaces.form.theme')}>
                                {themes.map((theme) => (
                                    <Chip
                                        key={theme.value}
                                        asChild
                                        selected={data.theme === theme.value}
                                        tone="outline"
                                        className="px-3 py-1.5 text-sm"
                                    >
                                        <button
                                            type="button"
                                            role="radio"
                                            aria-checked={data.theme === theme.value}
                                            onClick={() => setData('theme', theme.value)}
                                        >
                                            <span
                                                aria-hidden="true"
                                                className={cn('size-3 rounded-full border border-current/30', THEME_SWATCH[theme.value])}
                                            />
                                            {theme.label}
                                        </button>
                                    </Chip>
                                ))}
                            </div>
                            <InputError message={errors.theme} />
                        </div>

                        <div className="flex items-center gap-2">
                            <Checkbox
                                id="collect_rating"
                                checked={data.collect_rating}
                                onCheckedChange={(checked) => setData('collect_rating', checked === true)}
                            />
                            <Label htmlFor="collect_rating">{t('spaces.form.collect_rating')}</Label>
                        </div>
                        <div className="flex items-center gap-2">
                            <Checkbox
                                id="is_accepting"
                                checked={data.is_accepting}
                                onCheckedChange={(checked) => setData('is_accepting', checked === true)}
                            />
                            <Label htmlFor="is_accepting">{t('spaces.form.is_accepting')}</Label>
                        </div>

                        <div className="flex gap-2">
                            <Button type="submit" disabled={processing}>
                                {isEditing ? t('spaces.form.save') : t('spaces.form.create')}
                            </Button>
                            <Button asChild variant="ghost">
                                <Link href={route('spaces.index')}>{t('common.cancel')}</Link>
                            </Button>
                        </div>
                    </form>

                    <aside aria-label={t('spaces.form.preview')} className="flex flex-col items-center gap-3 lg:sticky lg:top-20">
                        <p className="text-muted-foreground text-xs font-medium tracking-wide uppercase">{t('spaces.form.preview')}</p>
                        <CollectionCard space={{ ...data, logo_url: logoPreview }} />
                    </aside>
                </div>
            </div>
        </AppLayout>
    );
}
