import InputError from '@/components/input-error';
import CollectionCard from '@/components/spaces/collection-card';
import OptionalFieldRow from '@/components/spaces/optional-field-row';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import AppLayout from '@/layouts/app-layout';
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

const FIELD_LABELS: Record<OptionalFieldKey, string> = {
    company: 'Company name',
    title: 'Job title',
    social_link: 'Social link',
    photo: 'Profile photo',
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
        { title: 'Spaces', href: '/spaces' },
        { title: isEditing ? 'Edit' : 'New', href: '#' },
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
            <Head title={isEditing ? 'Edit space' : 'New space'} />
            <div className="grid gap-6 p-4 lg:grid-cols-2">
                <form onSubmit={submit} className="space-y-5" aria-label="Space settings">
                    <div className="grid gap-1.5">
                        <Label htmlFor="name">Space name *</Label>
                        <Input id="name" required value={data.name} onChange={(e) => setData('name', e.target.value)} />
                        <InputError message={errors.name} />
                    </div>
                    <div className="grid gap-1.5">
                        <Label htmlFor="header_title">Header title *</Label>
                        <Input id="header_title" required placeholder="Would you recommend us?" value={data.header_title} onChange={(e) => setData('header_title', e.target.value)} />
                        <InputError message={errors.header_title} />
                    </div>
                    <div className="grid gap-1.5">
                        <Label htmlFor="message">Custom message * (Markdown supported)</Label>
                        <Textarea id="message" required value={data.message} onChange={(e) => setData('message', e.target.value)} />
                        <InputError message={errors.message} />
                    </div>
                    <div className="grid gap-1.5">
                        <Label htmlFor="logo">Logo</Label>
                        <Input id="logo" type="file" accept="image/png,image/jpeg,image/webp" onChange={(e) => setData('logo', e.target.files?.[0] ?? null)} />
                        <InputError message={errors.logo} />
                    </div>

                    <fieldset className="space-y-2">
                        <legend className="text-sm font-medium">Respondent fields</legend>
                        <p className="text-muted-foreground text-sm">Name and email are always required.</p>
                        {optionalFields.map((key) => (
                            <OptionalFieldRow key={key} id={key} label={FIELD_LABELS[key]} config={data.fields[key]} onChange={(config) => setData('fields', { ...data.fields, [key]: config })} />
                        ))}
                    </fieldset>

                    <div className="grid gap-1.5">
                        <Label>Theme</Label>
                        <div className="flex gap-2" role="radiogroup" aria-label="Theme">
                            {themes.map((theme) => (
                                <Button key={theme.value} type="button" role="radio" aria-checked={data.theme === theme.value} variant={data.theme === theme.value ? 'default' : 'outline'} onClick={() => setData('theme', theme.value)}>
                                    {theme.label}
                                </Button>
                            ))}
                        </div>
                        <InputError message={errors.theme} />
                    </div>

                    <div className="flex items-center gap-2">
                        <Checkbox id="collect_rating" checked={data.collect_rating} onCheckedChange={(checked) => setData('collect_rating', checked === true)} />
                        <Label htmlFor="collect_rating">Collect star ratings</Label>
                    </div>
                    <div className="flex items-center gap-2">
                        <Checkbox id="is_accepting" checked={data.is_accepting} onCheckedChange={(checked) => setData('is_accepting', checked === true)} />
                        <Label htmlFor="is_accepting">Accepting new testimonials</Label>
                    </div>

                    <div className="flex gap-2">
                        <Button type="submit" disabled={processing}>
                            {isEditing ? 'Save changes' : 'Create space'}
                        </Button>
                        <Button asChild variant="ghost">
                            <Link href={route('spaces.index')}>Cancel</Link>
                        </Button>
                    </div>
                </form>

                <aside aria-label="Live preview" className="flex flex-col items-center gap-2">
                    <p className="text-muted-foreground text-xs tracking-wide uppercase">Live preview</p>
                    <CollectionCard space={{ ...data, logo_url: logoPreview }} />
                </aside>
            </div>
        </AppLayout>
    );
}
