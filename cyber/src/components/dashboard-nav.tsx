"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { SidebarMenu, SidebarMenuItem, SidebarMenuButton } from "@/components/ui/sidebar";
import { LayoutDashboard, Search, Users, FileText, Bell, FolderOpen } from 'lucide-react';

const navItems = [
    { href: '/dashboard', icon: <LayoutDashboard />, label: 'Dashboard' },
    { href: '/dashboard/cases', icon: <FolderOpen />, label: 'Cases' },
    { href: '/dashboard/content-analysis', icon: <Search />, label: 'Content Analysis' },
    { href: '/dashboard/user-investigation', icon: <Users />, label: 'User Investigation' },
    { href: '/dashboard/reports', icon: <FileText />, label: 'Reports' },
    { href: '/dashboard/alerts', icon: <Bell />, label: 'Alerts' },
];

export function DashboardNav() {
    const pathname = usePathname();

    return (
        <SidebarMenu>
            {navItems.map((item) => {
                const isActive = item.href === '/dashboard' ? pathname === item.href : pathname.startsWith(item.href);
                return (
                    <SidebarMenuItem key={item.href}>
                        <SidebarMenuButton asChild isActive={isActive} tooltip={item.label}>
                            <Link href={item.href}>
                                {item.icon}
                                {item.label}
                            </Link>
                        </SidebarMenuButton>
                    </SidebarMenuItem>
                );
            })}
        </SidebarMenu>
    );
}
