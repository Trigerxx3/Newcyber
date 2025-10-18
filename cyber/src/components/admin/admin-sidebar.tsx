'use client'

import { usePathname } from 'next/navigation'
import Link from 'next/link'
import { cn } from '@/lib/utils'
import { 
  Users, 
  Settings, 
  Database, 
  Shield, 
  FileText,
  Home,
  Activity,
  BarChart3,
  AlertTriangle,
  Clock,
  Key,
  Server,
  Archive,
  UserCheck,
  Eye
} from 'lucide-react'

const navigation = [
  {
    name: 'Dashboard',
    href: '/admin',
    icon: Home,
    description: 'System overview and quick stats'
  },
  {
    name: 'User & Access Management',
    href: '/admin/users',
    icon: Users,
    description: 'Manage analyst accounts and permissions',
    subItems: [
      { name: 'All Users', href: '/admin/users', icon: Users },
      { name: 'Roles & Permissions', href: '/admin/users/roles', icon: Key },
      { name: 'Access Logs', href: '/admin/users/logs', icon: Activity }
    ]
  },
  {
    name: 'System Configuration',
    href: '/admin/config',
    icon: Settings,
    description: 'API connections and system settings',
    subItems: [
      { name: 'API Connections', href: '/admin/config/api', icon: Server },
      { name: 'Keywords & Rules', href: '/admin/config/keywords', icon: AlertTriangle },
      { name: 'Scraping Schedule', href: '/admin/config/schedule', icon: Clock }
    ]
  },
  {
    name: 'Data Management',
    href: '/admin/data',
    icon: Database,
    description: 'Database and storage management',
    subItems: [
      { name: 'Database Status', href: '/admin/data', icon: Database },
      { name: 'Storage Policy', href: '/admin/data/storage', icon: Archive },
      { name: 'Data Retention', href: '/admin/data/retention', icon: Clock }
    ]
  },
  {
    name: 'Data Scraping',
    href: '/admin/scraping',
    icon: Activity,
    description: 'Manage scraping, view scraped content and analytics'
  },
  {
    name: 'Security & Compliance',
    href: '/admin/security',
    icon: Shield,
    description: 'Monitor activity and enforce guidelines',
    subItems: [
      { name: 'Activity Monitoring', href: '/admin/security', icon: Eye },
      { name: 'Compliance Reports', href: '/admin/security/compliance', icon: FileText },
      { name: 'Privacy Guidelines', href: '/admin/security/privacy', icon: Shield }
    ]
  },
  {
    name: 'Case & Report Oversight',
    href: '/admin/reports',
    icon: FileText,
    description: 'Review and approve analyst cases and reports',
    subItems: [
      { name: 'Case Requests', href: '/admin/case-requests', icon: Clock },
      { name: 'Pending Reports', href: '/admin/reports', icon: Clock },
      { name: 'Approved Reports', href: '/admin/reports/approved', icon: UserCheck },
      { name: 'Report Analytics', href: '/admin/reports/analytics', icon: BarChart3 }
    ]
  }
]

export function AdminSidebar() {
  const pathname = usePathname()

  return (
    <div className="w-80 bg-black/50 border-r border-white/10 h-[calc(100vh-73px)] overflow-y-auto">
      <div className="p-6">
        <h2 className="text-lg font-semibold text-white mb-6">Admin Modules</h2>
        
        <nav className="space-y-2">
          {navigation.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
            const Icon = item.icon

            return (
              <div key={item.name}>
                <Link
                  href={item.href}
                  className={cn(
                    'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-white/10 text-white'
                      : 'text-gray-400 hover:text-white hover:bg-white/5'
                  )}
                >
                  <Icon className="h-4 w-4" />
                  <div className="flex-1">
                    <div>{item.name}</div>
                    <div className="text-xs text-gray-500 mt-0.5 leading-tight">
                      {item.description}
                    </div>
                  </div>
                </Link>
                
                {/* Sub-navigation items */}
                {item.subItems && isActive && (
                  <div className="ml-7 mt-2 space-y-1">
                    {item.subItems.map((subItem) => {
                      const SubIcon = subItem.icon
                      const isSubActive = pathname === subItem.href
                      
                      return (
                        <Link
                          key={subItem.name}
                          href={subItem.href}
                          className={cn(
                            'flex items-center gap-2 px-3 py-1.5 rounded-md text-xs transition-colors',
                            isSubActive
                              ? 'bg-white/10 text-white'
                              : 'text-gray-500 hover:text-gray-300 hover:bg-white/5'
                          )}
                        >
                          <SubIcon className="h-3 w-3" />
                          {subItem.name}
                        </Link>
                      )
                    })}
                  </div>
                )}
              </div>
            )
          })}
        </nav>
      </div>
    </div>
  )
}