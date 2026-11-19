import AppLogoIcon from '@/components/app-logo-icon';
import ThemeSwitch from '@/components/theme-switch';
import { Chip } from '@/components/ui/chip';
import { type ServiceStatus, useServiceStatus } from '@/hooks/use-service-status';
import { t } from '@/lib/i18n';
import { cn } from '@/lib/utils';
import { type SharedData } from '@/types';
import { Link, usePage } from '@inertiajs/react';

interface AppFooterProps {
    /** `compact` keeps only the bottom bar (used inside the app shell and on auth pages). */
    compact?: boolean;
    className?: string;
}

interface FooterLink {
    label: string;
    href: string;
}

const STATUS_TONE: Record<ServiceStatus, string> = {
    checking: 'bg-ink-3',
    operational: 'bg-success',
    degraded: 'bg-warning',
    unreachable: 'bg-destructive',
};

function StatusChip() {
    const status = useServiceStatus();

    return (
        <Chip tone="outline" role="status" aria-live="polite">
            <span className="relative flex size-2">
                {status === 'operational' && <span className="bg-success absolute inline-flex size-full animate-ping rounded-full opacity-50" />}
                <span className={cn('relative inline-flex size-2 rounded-full', STATUS_TONE[status])} />
            </span>
            {t(`footer.status.${status}`)}
        </Chip>
    );
}

function LinkGroup({ title, links }: { title: string; links: FooterLink[] }) {
    return (
        <nav aria-label={title}>
            <h2 className="eyebrow mb-3">{title}</h2>
            <ul className="space-y-2 text-sm">
                {links.map(({ label, href }) => (
                    <li key={href}>
                        <Link href={href} className="text-ink-2 hover:text-foreground transition-colors">
                            {label}
                        </Link>
                    </li>
                ))}
            </ul>
        </nav>
    );
}

/** Site footer: brand, links for the current visitor, live status, theme switch, build info. Light/dark and responsive. */
export default function AppFooter({ compact = false, className }: AppFooterProps) {
    const { auth, build, locale } = usePage<SharedData>().props;
    const year = new Date().getFullYear();
    const language = new Intl.DisplayNames([locale], { type: 'language' }).of(locale) ?? locale;
    const signedIn = auth.user !== null;

    const product: FooterLink[] = signedIn
        ? [
              { label: t('footer.link.dashboard'), href: route('dashboard') },
              { label: t('footer.link.spaces'), href: route('spaces.index') },
              { label: t('footer.link.billing'), href: route('billing.show') },
          ]
        : [
              { label: t('footer.link.home'), href: route('home') },
              { label: t('footer.link.log_in'), href: route('login') },
              { label: t('footer.link.register'), href: route('register') },
          ];
    const account: FooterLink[] = signedIn
        ? [
              { label: t('footer.link.profile'), href: route('profile.edit') },
              { label: t('footer.link.settings'), href: route('appearance') },
          ]
        : [];

    return (
        <footer aria-label={t('footer.label')} className={cn('border-border/70 mt-auto w-full border-t', className)}>
            <div className="mx-auto w-full max-w-6xl px-4 py-8 sm:px-6">
                {!compact && (
                    <div className="grid gap-8 pb-8 sm:grid-cols-2 lg:grid-cols-[1.4fr_1fr_1fr_auto]">
                        <div className="space-y-3 sm:col-span-2 lg:col-span-1">
                            <Link href={route('home')} className="flex items-center gap-2.5" aria-label={build.name}>
                                <span className="bg-primary text-primary-foreground flex size-9 items-center justify-center rounded-xl shadow-(--lift)">
                                    <AppLogoIcon className="size-5 fill-current" />
                                </span>
                                <span className="font-display text-lg font-semibold">{build.name}</span>
                            </Link>
                            <p className="text-ink-2 max-w-xs text-sm">{t('footer.tagline')}</p>
                            <StatusChip />
                        </div>
                        <LinkGroup title={t('footer.group.product')} links={product} />
                        {account.length > 0 ? <LinkGroup title={t('footer.group.account')} links={account} /> : <div className="hidden lg:block" />}
                        <div>
                            <h2 className="eyebrow mb-3">{t('footer.group.appearance')}</h2>
                            <ThemeSwitch />
                        </div>
                    </div>
                )}

                <div
                    className={cn('flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between', !compact && 'border-border/70 border-t pt-6')}
                >
                    <p className="text-ink-3 text-xs tabular-nums">{t('footer.copyright', { year, name: build.name })}</p>
                    <div className="flex flex-wrap items-center gap-2">
                        {compact && <StatusChip />}
                        <Chip tone="neutral">{t('footer.language', { language })}</Chip>
                        <Chip tone="neutral" className="font-mono">
                            {/^\d/.test(build.version) ? t('footer.version', { version: build.version }) : build.version}
                            {build.commit !== '' && ` · ${t('footer.build', { commit: build.commit })}`}
                        </Chip>
                        {build.env !== 'production' && <Chip tone="warning">{t('footer.env', { env: build.env })}</Chip>}
                        {compact && <ThemeSwitch />}
                    </div>
                </div>
            </div>
        </footer>
    );
}
