import FlashMessage from '@/components/flash-message';
import SpaceCard from '@/components/spaces/space-card';
import { Button } from '@/components/ui/button';
import AppLayout from '@/layouts/app-layout';
import { type BreadcrumbItem, type Space } from '@/types';
import { Head, Link } from '@inertiajs/react';

const breadcrumbs: BreadcrumbItem[] = [{ title: 'Spaces', href: '/spaces' }];

interface IndexProps {
    spaces: Space[];
    canCreate: boolean;
}

export default function Index({ spaces, canCreate }: IndexProps) {
    return (
        <AppLayout breadcrumbs={breadcrumbs}>
            <Head title="Spaces" />
            <div className="flex flex-col gap-4 p-4">
                <FlashMessage />
                <div className="flex items-center justify-between">
                    <h1 className="text-2xl font-semibold">Your spaces</h1>
                    {canCreate ? (
                        <Button asChild>
                            <Link href={route('spaces.create')}>New space</Link>
                        </Button>
                    ) : (
                        <Button asChild variant="outline">
                            <Link href={route('billing.show')}>Upgrade for more spaces</Link>
                        </Button>
                    )}
                </div>

                {spaces.length === 0 ? (
                    <p className="text-muted-foreground">No spaces yet. Create one to start collecting testimonials.</p>
                ) : (
                    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                        {spaces.map((space) => (
                            <SpaceCard key={space.public_id} space={space} />
                        ))}
                    </div>
                )}
            </div>
        </AppLayout>
    );
}
