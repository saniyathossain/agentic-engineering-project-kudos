import CopyButton from '@/components/copy-button';
import { Button } from '@/components/ui/button';
import { t, tDynamic } from '@/lib/i18n';
import { Head, Link, router } from '@inertiajs/react';
import { TriangleAlert } from 'lucide-react';

interface ErrorProps {
    status: number;
    copyKey: string;
    retryAfter: number | null;
    requestId: string | null;
}

/** Shown in place of a page that failed (not found, forbidden, expired, throttled, unexpected). */
export default function Error({ status, copyKey, retryAfter, requestId }: ErrorProps) {
    const title = tDynamic(`status.title.${copyKey}`);
    const details = [
        `${t('status.error_code', { code: status })} · ${title}`,
        requestId ? `${t('status.request_id')}: ${requestId}` : null,
        new Date().toISOString(),
    ]
        .filter((line): line is string => line !== null)
        .join('\n');

    return (
        <>
            <Head title={title} />
            <main className="flex min-h-svh items-center justify-center px-4 py-10">
                <section role="alert" className="pane rise w-full max-w-md rounded-3xl p-7 text-center">
                    <span className="icon-chip mx-auto size-14 rounded-2xl">
                        <TriangleAlert className="size-6" strokeWidth={1.75} />
                    </span>
                    <p className="text-ink-2 bg-muted mx-auto mt-4 w-fit rounded-full px-3 py-1 text-xs font-semibold">
                        {t('status.error_code', { code: status })}
                    </p>
                    <h1 className="font-display mt-2 text-3xl leading-tight font-medium">{title}</h1>
                    <p className="text-ink-2 mt-2 text-sm">{tDynamic(`status.why.${copyKey}`)}</p>
                    {retryAfter !== null && <p className="text-ink-3 mt-2 text-xs">{t('status.retry_after', { seconds: retryAfter })}</p>}
                    <div className="mt-6 flex flex-wrap justify-center gap-2">
                        <Button onClick={() => router.reload()}>{t('status.action.retry')}</Button>
                        <Button asChild variant="outline">
                            <Link href="/">{t('status.action.home')}</Link>
                        </Button>
                        <CopyButton text={details} label={t('status.action.copy')} />
                    </div>
                    {requestId && (
                        <p className="text-ink-3 mt-5 text-xs break-all">
                            {t('status.request_id')}: <code className="text-ink-2 font-mono">{requestId}</code>
                        </p>
                    )}
                </section>
            </main>
        </>
    );
}
