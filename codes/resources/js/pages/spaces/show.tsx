import CopyButton from '@/components/copy-button';
import EmbedSnippet from '@/components/embed-snippet';
import FlashMessage from '@/components/flash-message';
import PageHeader from '@/components/page-header';
import DateRangeFilter from '@/components/spaces/date-range-filter';
import TestimonialCard from '@/components/spaces/testimonial-card';
import { Button } from '@/components/ui/button';
import { Chip } from '@/components/ui/chip';
import AppLayout from '@/layouts/app-layout';
import { t, type TranslationKey } from '@/lib/i18n';
import { type BreadcrumbItem, type Space, type Testimonial } from '@/types';
import { Head, Link, router } from '@inertiajs/react';
import { ExternalLink, Pencil, Trash2 } from 'lucide-react';
import { type CSSProperties } from 'react';

type InboxFilter = 'all' | 'favorite' | 'pending' | 'published' | 'hidden';

interface Paginated<T> {
    data: T[];
    links: { prev: string | null; next: string | null };
}

interface ShowProps {
    space: Space;
    testimonials: Paginated<Testimonial>;
    filter: InboxFilter;
    range: { from: string | null; to: string | null };
    counts: Record<InboxFilter, number>;
    publicUrl: string;
}

const FILTERS: ReadonlyArray<{ value: InboxFilter; label: TranslationKey }> = [
    { value: 'all', label: 'inbox.filter.all' },
    { value: 'pending', label: 'inbox.filter.pending' },
    { value: 'favorite', label: 'inbox.filter.favorite' },
    { value: 'published', label: 'inbox.filter.published' },
    { value: 'hidden', label: 'inbox.filter.hidden' },
];

export default function Show({ space, testimonials, filter, range, counts, publicUrl }: ShowProps) {
    const breadcrumbs: BreadcrumbItem[] = [
        { title: t('spaces.index.title'), href: '/spaces' },
        { title: space.name, href: route('spaces.show', space.public_id) },
    ];

    return (
        <AppLayout breadcrumbs={breadcrumbs}>
            <Head title={space.name} />
            <div className="mx-auto flex w-full max-w-5xl flex-col gap-6 p-4 sm:p-6">
                <FlashMessage />
                <PageHeader
                    title={space.name}
                    description={publicUrl}
                    actions={
                        <>
                            <CopyButton text={publicUrl} label={t('spaces.show.copy_link')} />
                            <Button asChild variant="outline" size="sm">
                                <a href={publicUrl} target="_blank" rel="noreferrer">
                                    <ExternalLink strokeWidth={1.75} className="ico-up-right" /> {t('spaces.show.visit')}
                                </a>
                            </Button>
                            <Button asChild variant="outline" size="sm">
                                <Link href={route('spaces.edit', space.public_id)}>
                                    <Pencil strokeWidth={1.75} className="ico-pencil" /> {t('common.edit')}
                                </Link>
                            </Button>
                            <Button
                                variant="ghost"
                                size="sm"
                                aria-label={t('spaces.show.delete_aria')}
                                onClick={() =>
                                    window.confirm(t('spaces.show.delete_confirm')) && router.delete(route('spaces.destroy', space.public_id))
                                }
                            >
                                <Trash2 strokeWidth={1.75} className="ico-trash" />
                            </Button>
                        </>
                    }
                />

                <section className="pane rise rounded-2xl p-5" style={{ '--i': 1 } as CSSProperties} aria-label={t('spaces.show.embed_aria')}>
                    <h2 className="font-display mb-1 text-lg font-medium">{t('spaces.show.embed_title')}</h2>
                    <p className="text-muted-foreground mb-3 text-sm">{t('spaces.show.embed_body')}</p>
                    <EmbedSnippet publicId={space.public_id} />
                </section>

                <div className="flex flex-col gap-3">
                    <nav className="flex flex-wrap gap-2" aria-label={t('spaces.show.filters_aria')}>
                        {FILTERS.map(({ value, label }) => (
                            <Chip key={value} asChild selected={filter === value} tone="outline" className="px-3 py-1.5 text-sm">
                                <Link
                                    href={route('spaces.show', {
                                        space: space.public_id,
                                        filter: value,
                                        ...(range.from && { from: range.from }),
                                        ...(range.to && { to: range.to }),
                                    })}
                                    preserveScroll
                                    aria-current={filter === value ? 'page' : undefined}
                                >
                                    {t(label)}
                                    <span className="tabular-nums opacity-70">{counts[value]}</span>
                                </Link>
                            </Chip>
                        ))}
                    </nav>
                    <DateRangeFilter spaceId={space.public_id} filter={filter} from={range.from} to={range.to} />
                </div>

                {testimonials.data.length === 0 ? (
                    <div className="pane rise rounded-2xl px-6 py-14 text-center">
                        <p className="font-display text-xl">{t('spaces.show.empty_title')}</p>
                        <p className="text-muted-foreground mt-1 text-sm">{t('spaces.show.empty_body')}</p>
                    </div>
                ) : (
                    <div className="grid gap-4">
                        {testimonials.data.map((testimonial) => (
                            <TestimonialCard key={testimonial.public_id} testimonial={testimonial} />
                        ))}
                    </div>
                )}
            </div>
        </AppLayout>
    );
}
