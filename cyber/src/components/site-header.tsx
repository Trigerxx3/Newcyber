"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Logo } from "./logo";
import { Navigation } from "./navigation";
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'

const topLinks = [
  { name: "Dashboard", href: "/dashboard" },
  { name: "Reports", href: "/dashboard/reports" },
  { name: "Alerts", href: "/dashboard/alerts" },
  { name: "API Test", href: "/api-test" },
  { name: "Settings", href: "/dashboard/settings" },
];

export function SiteHeader() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, systemUser, signOut } = useAuth();

  const handleLogout = async () => {
    await signOut();
    router.push('/login');
  }

  return (
    <div className="w-full">
      {/* Thin top bar */}
      <div className="border-b border-white/10 bg-black/40 backdrop-blur supports-[backdrop-filter]:bg-black/30">
        <div className="container mx-auto flex items-center justify-between px-6 py-3">
          <div className="flex items-center gap-3">
            <Logo />
            <span className="text-sm text-muted-foreground hidden md:inline">
              Cyber Investigation Platform
            </span>
          </div>
          <div className="flex items-center gap-3">
            <Navigation />
            {user ? (
              <div className="flex items-center gap-3">
                <span className="text-sm text-muted-foreground hidden sm:inline">
                  {systemUser?.username || systemUser?.email || 'Signed in'}
                </span>
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button variant="outline" size="sm">Sign out</Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Confirm sign out</AlertDialogTitle>
                      <AlertDialogDescription>
                        You will be signed out and redirected to the login page.
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                      <AlertDialogAction onClick={handleLogout}>Sign out</AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </div>
            ) : (
              <Button variant="default" size="sm" onClick={() => router.push('/login')}>Sign in</Button>
            )}
          </div>
        </div>
      </div>

      {/* Main nav - commented out per request */}
      {/**
      <div className="border-b border-white/10 bg-black/50 backdrop-blur supports-[backdrop-filter]:bg-black/40">
        <div className="container mx-auto flex items-center gap-6 px-6 py-3 overflow-x-auto">
          {topLinks.map((item) => (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "text-sm whitespace-nowrap px-1 py-1 transition-colors hover:text-primary",
                pathname === item.href || pathname?.startsWith(item.href)
                  ? "text-foreground"
                  : "text-muted-foreground"
              )}
            >
              {item.name}
            </Link>
          ))}
        </div>
      </div>
      **/}
    </div>
  );
}

