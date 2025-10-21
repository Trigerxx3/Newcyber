'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { 
  TrendingUp, 
  Users, 
  Activity, 
  Clock, 
  Target,
  BarChart3,
  PieChart,
  Calendar,
  Award,
  Zap,
  CheckCircle,
  AlertTriangle,
  UserCheck,
  Timer,
  FileText,
  Download,
  RefreshCw,
  Loader2
} from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

interface AnalystPerformanceMetrics {
  productivity_score: number
  consistency_score: number
  quality_score: number
  collaboration_score: number
}

interface AnalystSummary {
  total_activities: number
  total_time_spent_minutes: number
  total_time_spent_hours: number
  by_type: Record<string, number>
  by_case: Record<string, number>
  by_month: Record<string, number>
  report_items_count: number
  average_activity_duration: number
  most_productive_day: string | null
  activity_trend: Array<{
    month: string
    count: number
  }>
}

interface Analyst {
  id: number
  username: string
  email: string
  role: string
}

interface AnalystPerformanceData {
  analyst: Analyst
  summary: AnalystSummary
  performance_metrics: AnalystPerformanceMetrics
}

interface AnalystPerformanceDashboardProps {
  selectedAnalystId?: number
  onAnalystSelect?: (analystId: number | null) => void
}

export default function AnalystPerformanceDashboard({ 
  selectedAnalystId, 
  onAnalystSelect 
}: AnalystPerformanceDashboardProps) {
  const { toast } = useToast()
  const [analysts, setAnalysts] = useState<Analyst[]>([])
  const [selectedAnalyst, setSelectedAnalyst] = useState<number | null>(selectedAnalystId || null)
  const [performanceData, setPerformanceData] = useState<AnalystPerformanceData | null>(null)
  const [loading, setLoading] = useState(true)
  const [dataLoading, setDataLoading] = useState(false)
  const [timeRange, setTimeRange] = useState('all')

  useEffect(() => {
    loadAnalysts()
  }, [])

  useEffect(() => {
    if (selectedAnalyst) {
      loadAnalystPerformance(selectedAnalyst)
    }
  }, [selectedAnalyst, timeRange])

  const loadAnalysts = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000'}/api/users`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      })
      
      if (response.ok) {
        const data = await response.json()
        if (data.data?.users) {
          const analystData = data.data.users.map((user: any) => ({
            id: user.id,
            username: user.username,
            email: user.email,
            role: user.role
          }))
          setAnalysts(analystData)
        }
      }
    } catch (error: any) {
      console.error('Error loading analysts:', error)
      toast({
        title: "Error",
        description: "Failed to load analysts",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  const loadAnalystPerformance = async (analystId: number) => {
    try {
      setDataLoading(true)
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000'}/api/analysts/${analystId}/activities/summary`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      })
      
      if (response.ok) {
        const data = await response.json()
        setPerformanceData(data)
      }
    } catch (error: any) {
      console.error('Error loading analyst performance:', error)
      toast({
        title: "Error",
        description: "Failed to load analyst performance data",
        variant: "destructive"
      })
    } finally {
      setDataLoading(false)
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-400'
    if (score >= 60) return 'text-yellow-400'
    return 'text-red-400'
  }

  const getScoreBadgeColor = (score: number) => {
    if (score >= 80) return 'bg-green-500/20 text-green-400 border-green-400/30'
    if (score >= 60) return 'bg-yellow-500/20 text-yellow-400 border-yellow-400/30'
    return 'bg-red-500/20 text-red-400 border-red-400/30'
  }

  const getPerformanceLevel = (score: number) => {
    if (score >= 90) return { level: 'Excellent', icon: Award, color: 'text-green-400' }
    if (score >= 80) return { level: 'Good', icon: CheckCircle, color: 'text-green-400' }
    if (score >= 70) return { level: 'Average', icon: Target, color: 'text-yellow-400' }
    if (score >= 60) return { level: 'Below Average', icon: AlertTriangle, color: 'text-orange-400' }
    return { level: 'Needs Improvement', icon: AlertTriangle, color: 'text-red-400' }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="flex flex-col items-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-muted-foreground font-medium">Loading analyst performance dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <BarChart3 className="h-6 w-6 text-primary" />
          <h2 className="text-2xl font-bold bg-gradient-to-r from-primary to-cyan-400 bg-clip-text text-transparent">
            Analyst Performance Dashboard
          </h2>
        </div>
        <div className="flex items-center gap-2">
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Time range" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Time</SelectItem>
              <SelectItem value="30">Last 30 Days</SelectItem>
              <SelectItem value="90">Last 90 Days</SelectItem>
              <SelectItem value="365">Last Year</SelectItem>
            </SelectContent>
          </Select>
          <Button
            variant="outline"
            onClick={loadAnalysts}
            className="border-white/10 hover:bg-white/5"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Analyst Selection */}
      <Card className="glassmorphism">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5 text-primary" />
            Select Analyst
          </CardTitle>
          <CardDescription>
            Choose an analyst to view their performance metrics and activity analytics
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {analysts.map((analyst) => (
              <div
                key={analyst.id}
                className={`p-4 border rounded-lg cursor-pointer transition-all hover:border-primary/50 ${
                  selectedAnalyst === analyst.id 
                    ? 'border-primary bg-primary/10' 
                    : 'border-white/10 hover:bg-white/5'
                }`}
                onClick={() => {
                  setSelectedAnalyst(analyst.id)
                  onAnalystSelect?.(analyst.id)
                }}
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
                    <UserCheck className="h-5 w-5 text-primary" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-foreground">{analyst.username}</h3>
                    <p className="text-sm text-muted-foreground">{analyst.email}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant="outline" className="text-xs">
                        {analyst.role}
                      </Badge>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Performance Data */}
      {selectedAnalyst && performanceData && (
        <div className="space-y-6">
          {/* Performance Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="glassmorphism">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Productivity</p>
                    <p className={`text-2xl font-bold ${getScoreColor(performanceData.performance_metrics.productivity_score)}`}>
                      {performanceData.performance_metrics.productivity_score}%
                    </p>
                  </div>
                  <Zap className="h-8 w-8 text-primary" />
                </div>
                <Badge className={getScoreBadgeColor(performanceData.performance_metrics.productivity_score)}>
                  {getPerformanceLevel(performanceData.performance_metrics.productivity_score).level}
                </Badge>
              </CardContent>
            </Card>

            <Card className="glassmorphism">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Consistency</p>
                    <p className={`text-2xl font-bold ${getScoreColor(performanceData.performance_metrics.consistency_score)}`}>
                      {performanceData.performance_metrics.consistency_score}%
                    </p>
                  </div>
                  <TrendingUp className="h-8 w-8 text-orange-400" />
                </div>
                <Badge className={getScoreBadgeColor(performanceData.performance_metrics.consistency_score)}>
                  {getPerformanceLevel(performanceData.performance_metrics.consistency_score).level}
                </Badge>
              </CardContent>
            </Card>

            <Card className="glassmorphism">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Quality</p>
                    <p className={`text-2xl font-bold ${getScoreColor(performanceData.performance_metrics.quality_score)}`}>
                      {performanceData.performance_metrics.quality_score}%
                    </p>
                  </div>
                  <Award className="h-8 w-8 text-green-400" />
                </div>
                <Badge className={getScoreBadgeColor(performanceData.performance_metrics.quality_score)}>
                  {getPerformanceLevel(performanceData.performance_metrics.quality_score).level}
                </Badge>
              </CardContent>
            </Card>

            <Card className="glassmorphism">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Collaboration</p>
                    <p className={`text-2xl font-bold ${getScoreColor(performanceData.performance_metrics.collaboration_score)}`}>
                      {performanceData.performance_metrics.collaboration_score}%
                    </p>
                  </div>
                  <Users className="h-8 w-8 text-blue-400" />
                </div>
                <Badge className={getScoreBadgeColor(performanceData.performance_metrics.collaboration_score)}>
                  {getPerformanceLevel(performanceData.performance_metrics.collaboration_score).level}
                </Badge>
              </CardContent>
            </Card>
          </div>

          {/* Detailed Analytics */}
          <Tabs defaultValue="overview" className="space-y-4">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="activities">Activities</TabsTrigger>
              <TabsTrigger value="trends">Trends</TabsTrigger>
              <TabsTrigger value="cases">Cases</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card className="glassmorphism">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Activity className="h-5 w-5 text-primary" />
                      Activity Summary
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex justify-between items-center">
                        <span className="text-muted-foreground">Total Activities</span>
                        <span className="font-semibold text-foreground">{performanceData.summary.total_activities}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-muted-foreground">Time Tracked</span>
                        <span className="font-semibold text-foreground">{performanceData.summary.total_time_spent_hours}h</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-muted-foreground">Report Items</span>
                        <span className="font-semibold text-foreground">{performanceData.summary.report_items_count}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-muted-foreground">Avg Duration</span>
                        <span className="font-semibold text-foreground">{performanceData.summary.average_activity_duration}min</span>
                      </div>
                      {performanceData.summary.most_productive_day && (
                        <div className="flex justify-between items-center">
                          <span className="text-muted-foreground">Most Productive Day</span>
                          <span className="font-semibold text-foreground">{performanceData.summary.most_productive_day}</span>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>

                <Card className="glassmorphism">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <PieChart className="h-5 w-5 text-primary" />
                      Activity Types
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {Object.entries(performanceData.summary.by_type)
                        .sort(([,a], [,b]) => b - a)
                        .slice(0, 5)
                        .map(([type, count]) => (
                          <div key={type} className="flex justify-between items-center">
                            <span className="text-sm text-muted-foreground capitalize">{type.replace('_', ' ')}</span>
                            <div className="flex items-center gap-2">
                              <div className="w-20 bg-white/10 rounded-full h-2">
                                <div 
                                  className="bg-primary h-2 rounded-full" 
                                  style={{ 
                                    width: `${(count / Math.max(...Object.values(performanceData.summary.by_type))) * 100}%` 
                                  }}
                                />
                              </div>
                              <span className="text-sm font-medium text-foreground">{count}</span>
                            </div>
                          </div>
                        ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="activities" className="space-y-4">
              <Card className="glassmorphism">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="h-5 w-5 text-primary" />
                    Activity Breakdown
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {Object.entries(performanceData.summary.by_type).map(([type, count]) => (
                      <div key={type} className="text-center p-4 border border-white/10 rounded-lg">
                        <div className="text-2xl font-bold text-primary">{count}</div>
                        <div className="text-sm text-muted-foreground capitalize">{type.replace('_', ' ')}</div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="trends" className="space-y-4">
              <Card className="glassmorphism">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-primary" />
                    Activity Trends
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="text-sm text-muted-foreground">
                      Activity trend over the last 6 months
                    </div>
                    <div className="grid grid-cols-6 gap-2">
                      {performanceData.summary.activity_trend.map((trend, index) => (
                        <div key={trend.month} className="text-center">
                          <div className="text-xs text-muted-foreground mb-1">{trend.month}</div>
                          <div className="w-full bg-white/10 rounded h-20 flex items-end">
                            <div 
                              className="w-full bg-primary rounded-b" 
                              style={{ 
                                height: `${Math.max(10, (trend.count / Math.max(...performanceData.summary.activity_trend.map(t => t.count), 1)) * 100)}%` 
                              }}
                            />
                          </div>
                          <div className="text-xs font-medium text-foreground mt-1">{trend.count}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="cases" className="space-y-4">
              <Card className="glassmorphism">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5 text-primary" />
                    Case Involvement
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {Object.entries(performanceData.summary.by_case)
                      .sort(([,a], [,b]) => b - a)
                      .map(([caseTitle, count]) => (
                        <div key={caseTitle} className="flex justify-between items-center p-3 border border-white/10 rounded-lg">
                          <span className="text-sm text-foreground">{caseTitle}</span>
                          <div className="flex items-center gap-2">
                            <div className="w-16 bg-white/10 rounded-full h-2">
                              <div 
                                className="bg-primary h-2 rounded-full" 
                                style={{ 
                                  width: `${(count / Math.max(...Object.values(performanceData.summary.by_case))) * 100}%` 
                                }}
                              />
                            </div>
                            <span className="text-sm font-medium text-foreground">{count}</span>
                          </div>
                        </div>
                      ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      )}

      {dataLoading && (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin text-primary" />
          <span className="ml-2 text-muted-foreground">Loading performance data...</span>
        </div>
      )}
    </div>
  )
}
