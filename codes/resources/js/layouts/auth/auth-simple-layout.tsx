import AppLogoIcon from '@/components/app-logo-icon';
import AppearanceToggleDropdown from '@/components/appearance-dropdown';
import { Link } from '@inertiajs/react';

interface AuthLayoutProps {
    children: React.ReactNode;
    name?: string;
    title?: string;
    description?: string;
}

export default function AuthSimpleLayout({ children, title, description }: AuthLayoutProps) {
    return (
        <div className="flex min-h-svh flex-col items-center justify-center gap-6 px-4 py-10">
            <div className="absolute top-4 right-4">
                <AppearanceToggleDropdown />
            </div>

            <div className="rise w-full max-w-sm space-y-6">
                <div className="flex flex-col items-center gap-4 text-center">
                    <Link href={route('home')} className="flex flex-col items-center gap-2" aria-label="Kudos home">
                        <span className="bg-primary text-primary-foreground flex size-11 items-center justify-center rounded-2xl shadow-(--lift)">
                            <AppLogoIcon className="size-6 fill-current" />
                        </span>
                        <span className="font-display text-xl font-semibold">Kudos</span>
                    </Link>
                    <div className="space-y-1.5">
                        <h1 className="font-display text-3xl leading-tight font-medium">{title}</h1>
                        <p className="text-muted-foreground text-sm">{description}</p>
                    </div>
                </div>
                <div className="pane rounded-2xl p-6">{children}</div>
            </div>
        </div>
    );
}
