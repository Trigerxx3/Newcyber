'use client'

import { useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
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
import { 
  Bell, 
  LogOut, 
  Settings, 
  User,
  Shield,
  Activity
} from 'lucide-react'
import { useRouter } from 'next/navigation'

export function AdminHeader() {
  const { systemUser, signOut } = useAuth()
  const router = useRouter()
  const [notifications] = useState([
    { id: 1, message: 'New analyst account pending approval', type: 'info' },
    { id: 2, message: 'System backup completed', type: 'success' },
    { id: 3, message: 'API rate limit warning', type: 'warning' }
  ])

  const handleSignOut = async () => {
    await signOut()
    router.push('/')
  }

  return (
    <header className="border-b border-white/10 bg-black/50 backdrop-blur supports-[backdrop-filter]:bg-black/40">
      <div className="container mx-auto flex items-center justify-between px-6 py-4">
        {/* Logo and Title */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3">
            <Shield className="h-8 w-8 text-red-500" />
            <div>
              <h1 className="text-xl font-bold text-white">Admin Panel</h1>
              <p className="text-xs text-gray-400">Cyber Intelligence Platform</p>
            </div>
          </div>
        </div>

        {/* Status Indicators */}
        <div className="hidden md:flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-green-400" />
            <Badge variant="outline" className="text-green-400 border-green-400/50">
              System Online
            </Badge>
          </div>
        </div>

        {/* User Actions */}
        <div className="flex items-center gap-4">
          {/* Notifications */}
          <Button variant="ghost" size="sm" className="relative">
            <Bell className="h-4 w-4" />
            {notifications.length > 0 && (
              <Badge 
                variant="destructive" 
                className="absolute -top-1 -right-1 h-5 w-5 p-0 flex items-center justify-center text-xs"
              >
                {notifications.length}
              </Badge>
            )}
          </Button>

          {/* User Info */}
            <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <User className="h-4 w-4 text-gray-400" />
              <div className="text-right">
                <p className="text-sm font-medium text-white">
                  {systemUser?.username || 'Admin'}
                </p>
                <p className="text-xs text-gray-400">
                  {systemUser?.email || 'admin@cyber.com'} • password
                </p>
              </div>
            </div>
            <Badge variant="secondary" className="bg-red-500/10 text-red-400 border-red-500/20">
              {systemUser?.role || 'ADMIN'}
            </Badge>
          </div>

          {/* Settings */}
          <Button variant="ghost" size="sm">
            <Settings className="h-4 w-4" />
          </Button>

          {/* Sign Out */}
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant="ghost" size="sm" className="text-red-400 hover:text-red-300 hover:bg-red-500/10">
                <LogOut className="h-4 w-4" />
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent className="bg-black border-white/20">
              <AlertDialogHeader>
                <AlertDialogTitle className="text-white">Sign Out</AlertDialogTitle>
                <AlertDialogDescription className="text-gray-400">
                  Are you sure you want to sign out of the admin panel? You'll need to sign in again to access administrative functions.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel className="bg-white/10 border-white/20 text-white hover:bg-white/20">
                  Cancel
                </AlertDialogCancel>
                <AlertDialogAction 
                  onClick={handleSignOut}
                  className="bg-red-500 hover:bg-red-600 text-white"
                >
                  Sign Out
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
      </div>
    </header>
  )
}