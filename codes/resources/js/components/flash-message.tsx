import { Alert, AlertDescription } from '@/components/ui/alert';
import { type SharedData } from '@/types';
import { usePage } from '@inertiajs/react';
import { CircleAlert, CircleCheck } from 'lucide-react';

export default function FlashMessage() {
    const { flash } = usePage<SharedData>().props;

    if (flash.error) {
        return (
            <Alert variant="destructive" role="alert" className="animate-pop">
                <CircleAlert className="size-4" strokeWidth={1.75} />
                <AlertDescription>{flash.error}</AlertDescription>
            </Alert>
        );
    }

    if (flash.success) {
        return (
            <Alert role="status" className="animate-pop">
                <CircleCheck className="ico-draw text-success size-4" strokeWidth={1.75} />
                <AlertDescription>{flash.success}</AlertDescription>
            </Alert>
        );
    }

    return null;
}
