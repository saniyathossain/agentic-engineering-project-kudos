import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Link, router } from '@inertiajs/react';
import { X } from 'lucide-react';

export default function UpgradeBanner() {
    const dismiss = () => router.post('/dashboard/banner/dismiss', {}, { preserveScroll: true, preserveState: true });

    return (
        <Alert className="flex items-start justify-between gap-4">
            <div>
                <AlertTitle>Unlock unlimited spaces and testimonials</AlertTitle>
                <AlertDescription>
                    The Free plan includes 1 space and 10 testimonials per space.{' '}
                    <Link href="/billing" className="font-medium underline underline-offset-4">
                        Upgrade to Pro
                    </Link>
                </AlertDescription>
            </div>
            <Button type="button" variant="ghost" size="icon" aria-label="Dismiss" onClick={dismiss}>
                <X />
            </Button>
        </Alert>
    );
}
