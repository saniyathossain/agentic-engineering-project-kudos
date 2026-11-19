import { t } from '@/lib/i18n';
import AppLogoIcon from './app-logo-icon';

export default function AppLogo() {
    return (
        <>
            <div className="bg-primary text-primary-foreground flex aspect-square size-9 items-center justify-center rounded-xl shadow-(--lift)">
                <AppLogoIcon className="size-5 fill-current" />
            </div>
            <div className="ml-1 grid flex-1 text-left">
                <span className="font-display truncate text-lg leading-none font-semibold">{t('app.name')}</span>
            </div>
        </>
    );
}
