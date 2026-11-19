import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { type Space } from '@/types';
import { Link } from '@inertiajs/react';

interface SpaceCardProps {
    space: Space;
}

export default function SpaceCard({ space }: SpaceCardProps) {
    return (
        <Card>
            <CardHeader className="flex-row items-start justify-between gap-2">
                <CardTitle className="text-lg">{space.name}</CardTitle>
                <Badge variant={space.is_accepting ? 'default' : 'secondary'}>{space.is_accepting ? 'Collecting' : 'Paused'}</Badge>
            </CardHeader>
            <CardContent className="text-muted-foreground text-sm">
                <p>/{space.slug}</p>
                <p>{space.testimonials_count ?? 0} testimonials</p>
            </CardContent>
            <CardFooter className="gap-2">
                <Button asChild size="sm">
                    <Link href={route('spaces.show', space.public_id)}>Open inbox</Link>
                </Button>
                <Button asChild size="sm" variant="outline">
                    <Link href={route('spaces.edit', space.public_id)}>Edit</Link>
                </Button>
            </CardFooter>
        </Card>
    );
}
