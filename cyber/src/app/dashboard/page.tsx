'use client'

import { useEffect, useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import apiClient from '@/lib/api'
import ProtectedRoute from '@/components/ProtectedRoute'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useRouter } from 'next/navigation'
import { useActiveCase } from '@/contexts/ActiveCaseContext'
import { 
  Users, 
  Shield, 
  AlertTriangle, 
  Database, 
  FileText, 
  TrendingUp,
  Activity,
  Globe,
  UserCheck,
  Clock,
  BarChart3,
  Eye
} from 'lucide-react'

interface DashboardStats {
  totalSources: number
  totalUsers: number
  flaggedUsers: number
  highRiskContent: number
  activeCases: number
}

interface ScrapedContentItem {
  id: string
  platform: string
  author: string
  text: string
  url: string
  timestamp: string
  scrapedAt: string
  keywordMatches: string[]
  riskLevel: string
  status: string
  sentimentScore: number
  analysisComplete: boolean
  flagged: boolean
}

export default function DashboardPage() {
  const { user, systemUser, signOut } = useAuth()
  const { activeCase, setActiveCase, clearActiveCase } = useActiveCase()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [recentScrapedContent, setRecentScrapedContent] = useState<ScrapedContentItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  useEffect(() => {
    if (!user) {
      router.push('/login')
      return
    }
    loadDashboardData()
  }, [user, router])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Check if we have a valid token first
      const token = localStorage.getItem('access_token')
      console.log('🔐 Dashboard: Checking token...', token ? 'Token found' : 'No token')
      
      if (!token) {
        console.log('🔐 Dashboard: No token found, redirecting to login')
        setError('No authentication token found. Please log in again.')
        router.push('/login')
        return
      }
      
      console.log('🔐 Dashboard: Token found, making API calls...')

      // Load dashboard statistics
      const [sourcesRes, usersRes, flaggedUsersRes, highRiskRes, casesRes] = await Promise.all([
        apiClient.getSources({ per_page: 1 }),
        apiClient.getUsers({ per_page: 1 }),
        apiClient.getUsers({ flagged: true, per_page: 1 }),
        apiClient.getHighRiskContent(),
        apiClient.getCases('Open')
      ])

      setStats({
        totalSources: (sourcesRes as any).pagination?.total || 0,
        totalUsers: (usersRes as any).pagination?.total || 0,
        flaggedUsers: (flaggedUsersRes as any).pagination?.total || 0,
        highRiskContent: (highRiskRes as any).data?.length || 0,
        activeCases: (casesRes as any).data?.length || 0
      })

      // Load recent content (available to all authenticated users)
      try {
        const contentRes = await apiClient.getContent({ per_page: 10 })
        const rawItems = (contentRes as any)?.data || []
        const items: ScrapedContentItem[] = rawItems.map((c: any) => ({
          id: String(c.id),
          platform: 'unknown',
          author: c.author || 'Unknown',
          text: c.text || '',
          url: c.url || '',
          timestamp: c.created_at || new Date().toISOString(),
          scrapedAt: c.created_at || new Date().toISOString(),
          keywordMatches: Array.isArray(c.keywords) ? c.keywords : [],
          riskLevel: c.risk_level || 'Low',
          status: c.status || 'Pending',
          sentimentScore: typeof c.sentiment_score === 'number' ? c.sentiment_score : 0,
          analysisComplete: (c.status || '').toLowerCase() === 'analyzed',
          flagged: false,
        }))
        setRecentScrapedContent(items)
      } catch (e) {
        console.warn('🔐 Dashboard: Failed to load recent content', e)
        setRecentScrapedContent([])
      }

    } catch (error: any) {
      console.error('🔐 Dashboard: Error loading dashboard data:', error)
      
      // Handle authentication errors
      if (error.message?.includes('401') || error.message?.includes('Unauthorized')) {
        console.log('🔐 Dashboard: 401 error - clearing tokens and redirecting')
        setError('Authentication failed. Please log in again.')
        // Clear tokens and redirect to login
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        router.push('/login')
        return
      }
      
      // Handle CORS errors specifically
      if (error.message?.includes('CORS') || error.message?.includes('Failed to fetch')) {
        console.log('🔐 Dashboard: CORS/Network error detected')
        setError('Connection error. Please check if the backend server is running.')
        return
      }
      
      setError(`Failed to load dashboard data: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleSignOut = async () => {
    try {
      await signOut()
      router.push('/login')
    } catch (error) {
      console.error('Error signing out:', error)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[radial-gradient(1200px_600px_at_50%_-10%,rgba(14,165,233,0.18),transparent),radial-gradient(800px_400px_at_80%_10%,rgba(16,185,129,0.12),transparent)] flex items-center justify-center">
        <div className="flex flex-col items-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          <p className="text-muted-foreground font-medium">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[radial-gradient(1200px_600px_at_50%_-10%,rgba(14,165,233,0.18),transparent),radial-gradient(800px_400px_at_80%_10%,rgba(16,185,129,0.12),transparent)] flex items-center justify-center">
        <div className="glassmorphism p-8 rounded-lg max-w-md w-full mx-4">
          <div className="text-center">
            <AlertTriangle className="h-12 w-12 text-red-400 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-foreground mb-2">Authentication Error</h2>
            <p className="text-muted-foreground mb-6">{error}</p>
            <Button onClick={() => router.push('/login')} className="w-full">
              Go to Login
            </Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-[radial-gradient(1200px_600px_at_50%_-10%,rgba(14,165,233,0.18),transparent),radial-gradient(800px_400px_at_80%_10%,rgba(16,185,129,0.12),transparent)]">
        {/* Header */}
        <header className="glassmorphism border-b border-white/10 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <Shield className="h-8 w-8 text-primary" />
                  <h1 className="text-2xl font-bold bg-gradient-to-r from-primary to-cyan-400 bg-clip-text text-transparent">
                    Cyber Intelligence
                  </h1>
                </div>
                <Badge variant="secondary" className="ml-2 bg-primary/20 text-primary border-primary/30">
                  Analyst Dashboard
                </Badge>
              </div>
              <div className="flex items-center space-x-4">
                <div className="text-right">
                  <p className="text-sm font-medium text-foreground">
                    {systemUser?.username}
                  </p>
                  <p className="text-xs text-muted-foreground capitalize">
                    {systemUser?.role?.toLowerCase()}
                  </p>
                </div>
                <Button onClick={handleSignOut} variant="outline" size="sm" className="border-white/10 hover:bg-white/5">
                  Sign Out
                </Button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
          {/* Welcome Section */}
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-foreground mb-2">
              Welcome back, {systemUser?.username}!
            </h2>
            <p className="text-muted-foreground">
              Here's what's happening with your cyber intelligence monitoring today.
            </p>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-6 mb-8">
            <Card className="glassmorphism hover:bg-secondary/60 transition-all duration-200">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm font-medium text-muted-foreground flex items-center">
                    <Database className="h-4 w-4 mr-2 text-primary" />
                    Total Sources
                  </CardTitle>
                  <TrendingUp className="h-4 w-4 text-green-400" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-foreground">{stats?.totalSources || 0}</div>
                <p className="text-xs text-muted-foreground mt-1">Active monitoring</p>
              </CardContent>
            </Card>

            <Card className="glassmorphism hover:bg-secondary/60 transition-all duration-200">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm font-medium text-muted-foreground flex items-center">
                    <Users className="h-4 w-4 mr-2 text-cyan-400" />
                    Monitored Users
                  </CardTitle>
                  <Activity className="h-4 w-4 text-primary" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-foreground">{stats?.totalUsers || 0}</div>
                <p className="text-xs text-muted-foreground mt-1">Under surveillance</p>
              </CardContent>
            </Card>

            <Card className="glassmorphism hover:bg-secondary/60 transition-all duration-200">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm font-medium text-muted-foreground flex items-center">
                    <AlertTriangle className="h-4 w-4 mr-2 text-red-400" />
                    Flagged Users
                  </CardTitle>
                  <UserCheck className="h-4 w-4 text-orange-400" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-red-400">{stats?.flaggedUsers || 0}</div>
                <p className="text-xs text-muted-foreground mt-1">Require attention</p>
              </CardContent>
            </Card>

            <Card className="glassmorphism hover:bg-secondary/60 transition-all duration-200">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm font-medium text-muted-foreground flex items-center">
                    <FileText className="h-4 w-4 mr-2 text-orange-400" />
                    High Risk Content
                  </CardTitle>
                  <Eye className="h-4 w-4 text-red-400" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-orange-400">{stats?.highRiskContent || 0}</div>
                <p className="text-xs text-muted-foreground mt-1">Needs review</p>
              </CardContent>
            </Card>

            <Card className="glassmorphism hover:bg-secondary/60 transition-all duration-200">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm font-medium text-muted-foreground flex items-center">
                    <Shield className="h-4 w-4 mr-2 text-green-400" />
                    Active Cases
                  </CardTitle>
                  <BarChart3 className="h-4 w-4 text-green-400" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-green-400">{stats?.activeCases || 0}</div>
                <p className="text-xs text-muted-foreground mt-1">In progress</p>
              </CardContent>
            </Card>

            <Card className="glassmorphism hover:bg-secondary/60 transition-all duration-200">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm font-medium text-muted-foreground flex items-center">
                    <Activity className="h-4 w-4 mr-2 text-cyan-400" />
                    Scraped Content
                  </CardTitle>
                  <Clock className="h-4 w-4 text-cyan-400" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-cyan-400">{recentScrapedContent.length || 0}</div>
                <p className="text-xs text-muted-foreground mt-1">Last 7 days</p>
              </CardContent>
            </Card>
          </div>


          {/* Recently Scraped Content Section */}
          <Card className="glassmorphism">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-xl font-semibold text-foreground flex items-center">
                    <Activity className="h-5 w-5 mr-2 text-cyan-400" />
                    Recently Scraped Content
                  </CardTitle>
                  <CardDescription className="text-muted-foreground">
                    Latest content scraped from monitored sources (last 7 days)
                  </CardDescription>
                </div>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="border-white/10 hover:bg-white/5"
                  onClick={() => router.push('/dashboard/content-analysis')}
                >
                  Analyze Content
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {recentScrapedContent.length > 0 ? (
                <div className="space-y-4">
                  {recentScrapedContent.map((content, index) => (
                    <div 
                      key={content.id || index} 
                      className="group p-4 rounded-lg border border-white/10 bg-secondary/30 hover:bg-secondary/50 hover:shadow-lg transition-all duration-200"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center space-x-3">
                          <div className="flex items-center space-x-2">
                            <Globe className="h-4 w-4 text-muted-foreground" />
                            <span className="text-sm font-medium text-foreground capitalize">
                              {content.platform || 'Unknown Platform'}
                            </span>
                          </div>
                          <span className="text-muted-foreground">•</span>
                          <span className="text-sm text-muted-foreground">
                            {content.author || 'Unknown User'}
                          </span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge 
                            variant="secondary" 
                            className={`text-xs ${
                              content.riskLevel === 'HIGH' || content.riskLevel === 'CRITICAL' 
                                ? 'bg-red-500/20 text-red-400 border-red-400/30' 
                                : content.riskLevel === 'MEDIUM'
                                ? 'bg-yellow-500/20 text-yellow-400 border-yellow-400/30'
                                : 'bg-green-500/20 text-green-400 border-green-400/30'
                            }`}
                          >
                            {content.riskLevel || 'Unknown'}
                          </Badge>
                          <Badge variant="secondary" className="text-xs bg-primary/20 text-primary border-primary/30">
                            {new Date(content.timestamp).toLocaleDateString()}
                          </Badge>
                          <Button variant="ghost" size="sm" className="opacity-0 group-hover:opacity-100 transition-opacity hover:bg-white/5">
                            <Eye className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                      <p className="text-sm text-foreground leading-relaxed line-clamp-2">
                        {content.text || 'No content available'}
                      </p>
                      <div className="mt-3 flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <Badge variant="outline" className="text-xs border-primary/30 text-primary">
                            ID: {content.id?.substring(0, 8) || 'N/A'}
                          </Badge>
                          {content.keywordMatches && content.keywordMatches.length > 0 && (
                            <Badge variant="outline" className="text-xs border-purple-400/30 text-purple-400">
                              {content.keywordMatches.length} keyword{content.keywordMatches.length !== 1 ? 's' : ''}
                            </Badge>
                          )}
                          {content.flagged && (
                            <Badge variant="outline" className="text-xs border-red-400/30 text-red-400">
                              🚩 Flagged
                            </Badge>
                          )}
                        </div>
                        <div className="flex items-center space-x-1">
                          {content.analysisComplete && (
                            <Badge variant="outline" className="text-xs border-green-400/30 text-green-400">
                              ✓ Analyzed
                            </Badge>
                          )}
                          <Badge variant="outline" className="text-xs border-cyan-400/30 text-cyan-400">
                            Sentiment: {content.sentimentScore?.toFixed(1) || '0.0'}
                          </Badge>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <Activity className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground font-medium">No recently scraped content found</p>
                  <p className="text-sm text-muted-foreground/70 mt-1">
                    Content will appear here as it's scraped from sources
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="glassmorphism bg-gradient-to-br from-primary/10 to-cyan-400/10 border-primary/30 hover:bg-primary/20 transition-all duration-200">
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-foreground flex items-center">
                  <Activity className="h-5 w-5 mr-2 text-primary" />
                  Start Analysis
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground text-sm mb-4">
                  Begin analyzing new content for potential threats
                </p>
                <Button className="w-full bg-primary hover:bg-primary/90 text-primary-foreground">
                  Analyze Content
                </Button>
              </CardContent>
            </Card>

            <Card className="glassmorphism bg-gradient-to-br from-green-400/10 to-emerald-400/10 border-green-400/30 hover:bg-green-400/20 transition-all duration-200">
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-foreground flex items-center">
                  <Users className="h-5 w-5 mr-2 text-green-400" />
                  User Investigation
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground text-sm mb-4">
                  Investigate suspicious user profiles and activities
                </p>
                <Button variant="outline" className="w-full border-green-400/30 text-green-400 hover:bg-green-400/10">
                  Investigate User
                </Button>
              </CardContent>
            </Card>

            <Card className="glassmorphism bg-gradient-to-br from-purple-400/10 to-pink-400/10 border-purple-400/30 hover:bg-purple-400/20 transition-all duration-200">
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-foreground flex items-center">
                  <BarChart3 className="h-5 w-5 mr-2 text-purple-400" />
                  Generate Reports
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground text-sm mb-4">
                  Generate comprehensive PDF reports for investigation cases
                </p>
                <Button 
                  variant="outline" 
                  className="w-full border-purple-400/30 text-purple-400 hover:bg-purple-400/10"
                  onClick={() => router.push('/dashboard/reports')}
                >
                  View Reports
                </Button>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
