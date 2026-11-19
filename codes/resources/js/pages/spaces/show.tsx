import CopyButton from '@/components/copy-button';
import FlashMessage from '@/components/flash-message';
import TestimonialCard from '@/components/spaces/testimonial-card';
import { Button } from '@/components/ui/button';
import AppLayout from '@/layouts/app-layout';
import { cn } from '@/lib/utils';
import { type BreadcrumbItem, type Space, type Testimonial } from '@/types';
import { Head, Link, router } from '@inertiajs/react';

type InboxFilter = 'all' | 'favorite' | 'pending' | 'published' | 'hidden';

interface Paginated<T> {
    data: T[];
    links: { prev: string | null; next: string | null };
}

interface ShowProps {
    space: Space;
    testimonials: Paginated<Testimonial>;
    filter: InboxFilter;
    counts: Record<InboxFilter, number>;
    publicUrl: string;
}

const FILTERS: ReadonlyArray<{ value: InboxFilter; label: string }> = [
    { value: 'all', label: 'All' },
    { value: 'pending', label: 'Pending' },
    { value: 'favorite', label: 'Favorites' },
    { value: 'published', label: 'Published' },
    { value: 'hidden', label: 'Hidden' },
];

export default function Show({ space, testimonials, filter, counts, publicUrl }: ShowProps) {
    const breadcrumbs: BreadcrumbItem[] = [
        { title: 'Spaces', href: '/spaces' },
        { title: space.name, href: route('spaces.show', space.public_id) },
    ];

    return (
        <AppLayout breadcrumbs={breadcrumbs}>
            <Head title={space.name} />
            <div className="flex flex-col gap-4 p-4">
                <FlashMessage />
                <div className="flex flex-wrap items-center justify-between gap-2">
                    <div>
                        <h1 className="text-2xl font-semibold">{space.name}</h1>
                        <p className="text-muted-foreground text-sm">{publicUrl}</p>
                    </div>
                    <div className="flex gap-2">
                        <CopyButton text={publicUrl} label="Copy link" />
                        <Button asChild variant="outline" size="sm">
                            <a href={publicUrl} target="_blank" rel="noreferrer">
                                Visit
                            </a>
                        </Button>
                        <Button asChild variant="outline" size="sm">
                            <Link href={route('spaces.edit', space.public_id)}>Edit</Link>
                        </Button>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => window.confirm('Delete this space and all its testimonials?') && router.delete(route('spaces.destroy', space.public_id))}
                        >
                            Delete
                        </Button>
                    </div>
                </div>

                <nav className="flex flex-wrap gap-2" aria-label="Inbox filters">
                    {FILTERS.map(({ value, label }) => (
                        <Link
                            key={value}
                            href={route('spaces.show', { space: space.public_id, filter: value })}
                            preserveScroll
                            className={cn('rounded-full border px-3 py-1 text-sm', filter === value ? 'bg-primary text-primary-foreground' : 'hover:bg-muted')}
                        >
                            {label} ({counts[value]})
                        </Link>
                    ))}
                </nav>

                {testimonials.data.length === 0 ? (
                    <p className="text-muted-foreground">No testimonials here yet.</p>
                ) : (
                    <div className="grid gap-3">
                        {testimonials.data.map((testimonial) => (
                            <TestimonialCard key={testimonial.public_id} testimonial={testimonial} />
                        ))}
                    </div>
                )}
            </div>
        </AppLayout>
    );
}
