import { NavMain } from '@/components/nav-main';
import { NavUser } from '@/components/nav-user';
import { SidebarUpgradeCard } from '@/components/sidebar-upgrade-card';
import { Sidebar, SidebarContent, SidebarFooter, SidebarHeader, SidebarMenu, SidebarMenuButton, SidebarMenuItem } from '@/components/ui/sidebar';
import { t } from '@/lib/i18n';
import { type NavItem } from '@/types';
import { Link } from '@inertiajs/react';
import { CreditCard, LayoutGrid, MessageSquareHeart, Settings } from 'lucide-react';
import AppLogo from './app-logo';

const buildMainNavItems = (): NavItem[] => [
    { title: t('nav.main.dashboard'), url: '/dashboard', icon: LayoutGrid },
    { title: t('nav.main.spaces'), url: '/spaces', icon: MessageSquareHeart },
    { title: t('nav.main.billing'), url: '/billing', icon: CreditCard },
];

const buildAccountNavItems = (): NavItem[] => [{ title: t('nav.main.settings'), url: '/settings', icon: Settings }];

export function AppSidebar() {
    return (
        <Sidebar collapsible="icon" variant="floating">
            <SidebarHeader className="p-3 pb-2">
                <SidebarMenu>
                    <SidebarMenuItem>
                        <SidebarMenuButton size="lg" asChild className="hover:translate-x-0">
                            <Link href="/dashboard" prefetch>
                                <AppLogo />
                            </Link>
                        </SidebarMenuButton>
                    </SidebarMenuItem>
                </SidebarMenu>
            </SidebarHeader>

            <SidebarContent className="gap-4 px-1 pt-2">
                <NavMain label={t('nav.main.platform')} items={buildMainNavItems()} />
                <NavMain label={t('nav.account')} items={buildAccountNavItems()} />
            </SidebarContent>

            <SidebarFooter className="gap-3 p-3">
                <SidebarUpgradeCard />
                <NavUser />
            </SidebarFooter>
        </Sidebar>
    );
}
