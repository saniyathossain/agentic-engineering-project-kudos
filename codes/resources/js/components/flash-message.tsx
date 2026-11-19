import { Alert, AlertDescription } from '@/components/ui/alert';
import { type SharedData } from '@/types';
import { usePage } from '@inertiajs/react';

export default function FlashMessage() {
    const { flash } = usePage<SharedData>().props;

    if (flash.error) {
        return (
            <Alert variant="destructive" role="alert">
                <AlertDescription>{flash.error}</AlertDescription>
            </Alert>
        );
    }

    if (flash.success) {
        return (
            <Alert role="status">
                <AlertDescription>{flash.success}</AlertDescription>
            </Alert>
        );
    }

    return null;
}
