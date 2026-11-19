import { NavMain } from '@/components/nav-main';
import { NavUser } from '@/components/nav-user';
import { Sidebar, SidebarContent, SidebarFooter, SidebarHeader, SidebarMenu, SidebarMenuButton, SidebarMenuItem } from '@/components/ui/sidebar';
import { t } from '@/lib/i18n';
import { type NavItem } from '@/types';
import { Link } from '@inertiajs/react';
import { CreditCard, LayoutGrid, MessageSquareHeart } from 'lucide-react';
import AppLogo from './app-logo';

const buildMainNavItems = (): NavItem[] => [
    { title: t('nav.main.dashboard'), url: '/dashboard', icon: LayoutGrid },
    { title: t('nav.main.spaces'), url: '/spaces', icon: MessageSquareHeart },
    { title: t('nav.main.billing'), url: '/billing', icon: CreditCard },
];

export function AppSidebar() {
    return (
        <Sidebar collapsible="icon" variant="inset">
            <SidebarHeader>
                <SidebarMenu>
                    <SidebarMenuItem>
                        <SidebarMenuButton size="lg" asChild>
                            <Link href="/dashboard" prefetch>
                                <AppLogo />
                            </Link>
                        </SidebarMenuButton>
                    </SidebarMenuItem>
                </SidebarMenu>
            </SidebarHeader>

            <SidebarContent>
                <NavMain items={buildMainNavItems()} />
            </SidebarContent>

            <SidebarFooter>
                <NavUser />
            </SidebarFooter>
        </Sidebar>
    );
}
