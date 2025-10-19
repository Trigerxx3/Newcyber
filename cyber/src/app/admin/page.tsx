'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  Users, 
  Settings, 
  Database, 
  Shield, 
  FileText, 
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  TrendingUp,
  Download
} from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { apiClient } from '@/lib/api'

interface DashboardStats {
  system_users: {
    total: number
    active: number
    admins: number
    analysts: number
  }
  platform_users: {
    total: number
    flagged: number
  }
  content: {
    total: number
    high_risk: number
  }
  cases: {
    total: number
    active: number
    pending: number
  }
  sources: {
    total: number
    active: number
  }
  keywords: {
    total: number
  }
  osint_results: {
    total: number
  }
  system_health: {
    last_backup: string
    uptime: string
    database_size: string
  }
}

interface ActivityItem {
  type: string
  message: string
  timestamp: string
  severity: string
}

interface ApiStatus {
  telegram: {
    status: string
    last_checked: string
    response_time: string
  }
  instagram: {
    status: string
    last_checked: string
    response_time: string
  }
  sherlock: {
    status: string
    last_checked: string
    response_time: string
  }
  spiderfoot: {
    status: string
    last_checked: string
    response_time: string
  }
}

export default function AdminDashboard() {
  const { systemUser } = useAuth()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [activity, setActivity] = useState<ActivityItem[]>([])
  const [apiStatus, setApiStatus] = useState<ApiStatus | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        // Fetch real data from the backend
        const [statsResponse, activityResponse, apiStatusResponse] = await Promise.all([
          apiClient.getAdminStats(),
          apiClient.getAdminActivity(),
          apiClient.getApiStatus()
        ]) as any[]
        
        setStats(statsResponse)
        setActivity(activityResponse)
        setApiStatus(apiStatusResponse)
      } catch (error) {
        console.error('Failed to load dashboard data:', error)
        // Set default/empty state on error
        setStats({
          system_users: { total: 0, active: 0, admins: 0, analysts: 0 },
          platform_users: { total: 0, flagged: 0 },
          content: { total: 0, high_risk: 0 },
          cases: { total: 0, active: 0, pending: 0 },
          sources: { total: 0, active: 0 },
          keywords: { total: 0 },
          osint_results: { total: 0 },
          system_health: { last_backup: 'Never', uptime: '0h', database_size: '0KB' }
        })
        setActivity([])
        setApiStatus({
          telegram: { status: 'unknown', last_checked: 'Never', response_time: 'N/A' },
          instagram: { status: 'unknown', last_checked: 'Never', response_time: 'N/A' },
          sherlock: { status: 'unknown', last_checked: 'Never', response_time: 'N/A' },
          spiderfoot: { status: 'unknown', last_checked: 'Never', response_time: 'N/A' }
        })
      } finally {
        setLoading(false)
      }
    }

    loadDashboardData()
  }, [])

  const quickActions = [
    { 
      title: 'User Management', 
      description: 'Manage analyst accounts and permissions',
      icon: Users,
      href: '/admin/users',
      color: 'bg-blue-500/10 text-blue-400 border-blue-500/20'
    },
    { 
      title: 'System Config', 
      description: 'Configure API connections and settings',
      icon: Settings,
      href: '/admin/config',
      color: 'bg-green-500/10 text-green-400 border-green-500/20'
    },
    { 
      title: 'Data Management', 
      description: 'Database and storage management',
      icon: Database,
      href: '/admin/data',
      color: 'bg-purple-500/10 text-purple-400 border-purple-500/20'
    },
    { 
      title: 'Data Scraping', 
      description: 'Automated social media data collection',
      icon: Download,
      href: '/admin/scraping',
      color: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20'
    },
    { 
      title: 'Security & Compliance', 
      description: 'Monitor activity and enforce guidelines',
      icon: Shield,
      href: '/admin/security',
      color: 'bg-red-500/10 text-red-400 border-red-500/20'
    },
    { 
      title: 'Report Oversight', 
      description: 'Review and approve analyst reports',
      icon: FileText,
      href: '/admin/reports',
      color: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20'
    }
  ]

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-white/10 rounded w-1/4 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-white/5 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Welcome Header */}
      <div className="border-b border-white/10 pb-6">
        <h1 className="text-3xl font-bold text-white mb-2">
          Admin Dashboard
        </h1>
        <p className="text-gray-400">
          Welcome back, {systemUser?.username}. Manage your cyber intelligence platform.
        </p>
      </div>

      {/* System Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-white/5 border-white/10">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-400">System Users</CardTitle>
            <Users className="h-4 w-4 text-blue-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{stats?.system_users.total || 0}</div>
            <p className="text-xs text-gray-500">{stats?.system_users.active || 0} active, {stats?.system_users.admins || 0} admins</p>
          </CardContent>
        </Card>

        <Card className="bg-white/5 border-white/10">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-400">Active Cases</CardTitle>
            <Activity className="h-4 w-4 text-green-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{stats?.cases.active || 0}</div>
            <p className="text-xs text-gray-500">{stats?.cases.total || 0} total cases</p>
          </CardContent>
        </Card>

        <Card className="bg-white/5 border-white/10">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-400">Data Sources</CardTitle>
            <Clock className="h-4 w-4 text-yellow-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{stats?.sources.total || 0}</div>
            <p className="text-xs text-gray-500">{stats?.sources.active || 0} active sources</p>
          </CardContent>
        </Card>

        <Card className="bg-white/5 border-white/10">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-400">Keywords</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{stats?.keywords.total || 0}</div>
            <p className="text-xs text-gray-500">Detection patterns</p>
          </CardContent>
        </Card>
      </div>

      {/* System Health */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-white/5 border-white/10">
          <CardHeader>
            <CardTitle className="text-white">System Health</CardTitle>
            <CardDescription className="text-gray-400">
              Current system status and performance
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-400">System Uptime</span>
              <Badge variant="outline" className="text-green-400 border-green-400/50">
                {stats?.system_health.uptime || '0h'}
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Last Backup</span>
              <Badge variant="outline" className="text-blue-400 border-blue-400/50">
                {stats?.system_health.last_backup || 'Never'}
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Database Size</span>
              <Badge variant="outline" className="text-purple-400 border-purple-400/50">
                {stats?.system_health.database_size || '0KB'}
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/5 border-white/10">
          <CardHeader>
            <CardTitle className="text-white">API Connections</CardTitle>
            <CardDescription className="text-gray-400">
              External service integration status
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Telegram API</span>
              <div className="flex items-center gap-2">
                {apiStatus?.telegram.status === 'connected' ? (
                  <CheckCircle className="h-4 w-4 text-green-400" />
                ) : (
                  <AlertTriangle className="h-4 w-4 text-red-400" />
                )}
                <Badge 
                  variant="outline" 
                  className={apiStatus?.telegram.status === 'connected' ? 
                    "text-green-400 border-green-400/50" : 
                    "text-red-400 border-red-400/50"
                  }
                >
                  {apiStatus?.telegram.status || 'Unknown'}
                </Badge>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Instagram API</span>
              <div className="flex items-center gap-2">
                {apiStatus?.instagram.status === 'connected' ? (
                  <CheckCircle className="h-4 w-4 text-green-400" />
                ) : (
                  <AlertTriangle className="h-4 w-4 text-red-400" />
                )}
                <Badge 
                  variant="outline" 
                  className={apiStatus?.instagram.status === 'connected' ? 
                    "text-green-400 border-green-400/50" : 
                    "text-red-400 border-red-400/50"
                  }
                >
                  {apiStatus?.instagram.status || 'Unknown'}
                </Badge>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Sherlock OSINT</span>
              <div className="flex items-center gap-2">
                {apiStatus?.sherlock.status === 'connected' ? (
                  <CheckCircle className="h-4 w-4 text-green-400" />
                ) : (
                  <AlertTriangle className="h-4 w-4 text-red-400" />
                )}
                <Badge 
                  variant="outline" 
                  className={apiStatus?.sherlock.status === 'connected' ? 
                    "text-green-400 border-green-400/50" : 
                    "text-red-400 border-red-400/50"
                  }
                >
                  {apiStatus?.sherlock.status || 'Unknown'}
                </Badge>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">SpiderFoot</span>
              <div className="flex items-center gap-2">
                {apiStatus?.spiderfoot.status === 'connected' ? (
                  <CheckCircle className="h-4 w-4 text-green-400" />
                ) : (
                  <AlertTriangle className="h-4 w-4 text-red-400" />
                )}
                <Badge 
                  variant="outline" 
                  className={apiStatus?.spiderfoot.status === 'connected' ? 
                    "text-green-400 border-green-400/50" : 
                    "text-red-400 border-red-400/50"
                  }
                >
                  {apiStatus?.spiderfoot.status || 'Unknown'}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card className="bg-white/5 border-white/10">
        <CardHeader>
          <CardTitle className="text-white">Admin Modules</CardTitle>
          <CardDescription className="text-gray-400">
            Quick access to administrative functions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
            {quickActions.map((action) => {
              const Icon = action.icon
              return (
                <Button
                  key={action.title}
                  variant="outline"
                  className={`h-auto p-4 flex flex-col items-center gap-3 ${action.color} hover:bg-white/10`}
                  onClick={() => window.location.href = action.href}
                >
                  <Icon className="h-6 w-6" />
                  <div className="text-center">
                    <div className="font-medium">{action.title}</div>
                    <div className="text-xs text-gray-400 mt-1">{action.description}</div>
                  </div>
                </Button>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <Card className="bg-white/5 border-white/10">
        <CardHeader>
          <CardTitle className="text-white">Recent Activity</CardTitle>
          <CardDescription className="text-gray-400">
            Latest system events and user actions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {activity.length > 0 ? (
              activity.map((item, index) => {
                const getSeverityColor = (severity: string) => {
                  switch (severity) {
                    case 'success': return 'bg-green-400'
                    case 'info': return 'bg-blue-400'
                    case 'warning': return 'bg-yellow-400'
                    case 'error': return 'bg-red-400'
                    default: return 'bg-gray-400'
                  }
                }
                
                const formatTimestamp = (timestamp: string) => {
                  try {
                    const date = new Date(timestamp)
                    const now = new Date()
                    const diffMs = now.getTime() - date.getTime()
                    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
                    const diffDays = Math.floor(diffHours / 24)
                    
                    if (diffDays > 0) {
                      return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
                    } else if (diffHours > 0) {
                      return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
                    } else {
                      const diffMinutes = Math.floor(diffMs / (1000 * 60))
                      return `${diffMinutes} minute${diffMinutes > 1 ? 's' : ''} ago`
                    }
                  } catch {
                    return 'Recently'
                  }
                }
                
                return (
                  <div key={index} className="flex items-center gap-4 p-3 rounded-lg bg-white/5">
                    <div className={`w-2 h-2 rounded-full ${getSeverityColor(item.severity)}`}></div>
                    <div className="flex-1">
                      <p className="text-white text-sm">{item.message}</p>
                      <p className="text-gray-400 text-xs">{formatTimestamp(item.timestamp)}</p>
                    </div>
                  </div>
                )
              })
            ) : (
              <div className="flex items-center gap-4 p-3 rounded-lg bg-white/5">
                <div className="w-2 h-2 rounded-full bg-gray-400"></div>
                <div className="flex-1">
                  <p className="text-white text-sm">No recent activity</p>
                  <p className="text-gray-400 text-xs">System is running normally</p>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}