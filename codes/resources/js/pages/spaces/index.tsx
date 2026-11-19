import FlashMessage from '@/components/flash-message';
import PageHeader from '@/components/page-header';
import SpaceCard from '@/components/spaces/space-card';
import { Button } from '@/components/ui/button';
import AppLayout from '@/layouts/app-layout';
import { t } from '@/lib/i18n';
import { type BreadcrumbItem, type Space } from '@/types';
import { Head, Link } from '@inertiajs/react';
import { MessageSquareQuote, Plus, Sparkles } from 'lucide-react';

interface IndexProps {
    spaces: Space[];
    canCreate: boolean;
}

export default function Index({ spaces, canCreate }: IndexProps) {
    const breadcrumbs: BreadcrumbItem[] = [{ title: t('spaces.index.title'), href: '/spaces' }];
    const action = canCreate ? (
        <Button asChild>
            <Link href={route('spaces.create')}>
                <Plus strokeWidth={1.75} className="ico-plus" /> {t('spaces.index.new')}
            </Link>
        </Button>
    ) : (
        <Button asChild variant="outline">
            <Link href={route('billing.show')}>
                <Sparkles strokeWidth={1.75} className="ico-sparkles" /> {t('spaces.index.more_with_pro')}
            </Link>
        </Button>
    );

    return (
        <AppLayout breadcrumbs={breadcrumbs}>
            <Head title={t('spaces.index.title')} />
            <div className="mx-auto flex w-full max-w-6xl flex-col gap-6 p-4 sm:p-6">
                <FlashMessage />
                <PageHeader title={t('spaces.index.title')} description={t('spaces.index.description')} actions={action} />

                {spaces.length === 0 ? (
                    <div className="pane rise flex flex-col items-center gap-3 rounded-3xl px-6 py-16 text-center">
                        <span className="icon-chip size-12 rounded-2xl">
                            <MessageSquareQuote className="size-6" strokeWidth={1.5} />
                        </span>
                        <h2 className="font-display text-2xl font-medium">{t('spaces.index.empty_title')}</h2>
                        <p className="text-muted-foreground max-w-sm text-sm">{t('spaces.index.empty_body')}</p>
                    </div>
                ) : (
                    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
                        {spaces.map((space, index) => (
                            <SpaceCard key={space.public_id} space={space} index={index} />
                        ))}
                    </div>
                )}
            </div>
        </AppLayout>
    );
}
