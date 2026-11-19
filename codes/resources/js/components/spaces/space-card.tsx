import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Chip } from '@/components/ui/chip';
import { type Space } from '@/types';
import { Link } from '@inertiajs/react';
import { ArrowUpRight, MessageSquareQuote, Pencil } from 'lucide-react';
import { type CSSProperties } from 'react';

interface SpaceCardProps {
    space: Space;
    index: number;
}

export default function SpaceCard({ space, index }: SpaceCardProps) {
    return (
        <Card
            className="rise group flex flex-col gap-4 p-5 transition-[transform,box-shadow] duration-300 ease-(--ease-liquid) hover:-translate-y-0.5 hover:shadow-(--sh-lg)"
            style={{ '--i': index } as CSSProperties}
        >
            <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                    <h2 className="font-display truncate text-xl font-medium">{space.name}</h2>
                    <p className="text-muted-foreground truncate text-sm">/{space.slug}</p>
                </div>
                <Chip tone={space.is_accepting ? 'success' : 'neutral'} dot>
                    {space.is_accepting ? 'Collecting' : 'Paused'}
                </Chip>
            </div>
            <p className="text-muted-foreground flex items-center gap-2 text-sm">
                <MessageSquareQuote className="size-4" strokeWidth={1.75} />
                {space.testimonials_count ?? 0} testimonials
            </p>
            <div className="mt-auto flex gap-2">
                <Button asChild size="sm">
                    <Link href={route('spaces.show', space.public_id)}>
                        Open inbox <ArrowUpRight strokeWidth={1.75} className="ico-up-right" />
                    </Link>
                </Button>
                <Button asChild size="sm" variant="outline">
                    <Link href={route('spaces.edit', space.public_id)}>
                        <Pencil strokeWidth={1.75} className="ico-pencil" /> Edit
                    </Link>
                </Button>
            </div>
        </Card>
    );
}
