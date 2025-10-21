'use client'

import { useEffect, useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { useToast } from '@/hooks/use-toast'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { 
  FileText, 
  Download, 
  Eye, 
  Search, 
  Filter,
  Calendar,
  User,
  AlertTriangle,
  CheckCircle,
  Clock,
  Loader2,
  RefreshCw,
  BarChart3,
  Shield,
  Star,
  FileBarChart,
  Activity,
  Users,
  TrendingUp,
  Edit,
  Trash2,
  Plus,
  UserCheck,
  Timer,
  Target
} from 'lucide-react'
import { apiClient } from '@/lib/api'
import ProtectedRoute from '@/components/ProtectedRoute'
import { useActiveCase } from '@/contexts/ActiveCaseContext'

interface Case {
  id: number
  title: string
  case_number: string
  status: string
  priority: string
  type: string
  created_at: string
  updated_at: string
  statistics: {
    flagged_content: number
    osint_results: number
    platform_users: number
  }
}

interface ReportPreview {
  case: {
    id: number
    title: string
    case_number: string
    status: string
    priority: string
    created_at: string
    updated_at: string
  }
  statistics: {
    platforms_analyzed: string
    flagged_users: number
    flagged_posts: number
    osint_results: number
  }
  flagged_content_summary: Array<{
    id: number
    author: string
    platform: string
    suspicion_score: number
    risk_level: string
    intent: string
    created_at: string
  }>
  osint_results_summary: Array<{
    id: number
    query: string
    search_type: string
    status: string
    risk_score: number
    created_at: string
  }>
}

interface AnalystActivity {
  id: number
  case_id: number
  analyst_id: number
  activity_type: string
  title: string
  description: string
  status: string
  tags: string[]
  priority: string
  activity_date: string
  time_spent_minutes: number
  include_in_report: boolean
  is_confidential: boolean
  visibility_level: string
  created_at: string
  updated_at: string
  analyst: {
    id: number
    username: string
    email: string
  }
  analyst_name?: string
  metadata?: any
}

interface AnalystActivitySummary {
  total_activities: number
  total_time_spent_minutes: number
  total_time_spent_hours: number
  by_type: Record<string, number>
  by_analyst: Record<string, number>
  report_items_count: number
  recent_activities: AnalystActivity[]
}

interface Analyst {
  id: number
  username: string
  email: string
  role: string
  total_activities: number
  total_time_spent: number
  active_cases: number
}

export default function ReportsPage() {
  const { systemUser } = useAuth()
  const { activeCase } = useActiveCase()
  const [activePreview, setActivePreview] = useState<ReportPreview | null>(null)
  const [activeLoading, setActiveLoading] = useState(false)
  const { toast } = useToast()
  const [loading, setLoading] = useState(true)
  const [cases, setCases] = useState<Case[]>([])
  const [filteredCases, setFilteredCases] = useState<Case[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [priorityFilter, setPriorityFilter] = useState('all')
  const [generatingReports, setGeneratingReports] = useState<Set<number>>(new Set())
  const [previewDialog, setPreviewDialog] = useState<{ open: boolean; caseId: number | null }>({
    open: false,
    caseId: null
  })
  const [reportPreview, setReportPreview] = useState<ReportPreview | null>(null)
  const [previewLoading, setPreviewLoading] = useState(false)
  
  // Analyst Activity Tracking State
  const [analystActivities, setAnalystActivities] = useState<AnalystActivity[]>([])
  const [activitySummary, setActivitySummary] = useState<AnalystActivitySummary | null>(null)
  const [analysts, setAnalysts] = useState<Analyst[]>([])
  const [selectedAnalyst, setSelectedAnalyst] = useState<number | null>(null)
  const [activityFilter, setActivityFilter] = useState('all')
  const [activityTypeFilter, setActivityTypeFilter] = useState('all')
  const [showActivityDialog, setShowActivityDialog] = useState(false)
  const [editingActivity, setEditingActivity] = useState<AnalystActivity | null>(null)
  const [activityLoading, setActivityLoading] = useState(false)
  const [previewActivity, setPreviewActivity] = useState<AnalystActivity | null>(null)
  const [showActivityPreviewDialog, setShowActivityPreviewDialog] = useState(false)
  const [pdfPreviewUrl, setPdfPreviewUrl] = useState<string | null>(null)
  const [showPdfPreviewDialog, setShowPdfPreviewDialog] = useState(false)
  const [pdfGenerating, setPdfGenerating] = useState(false)

  useEffect(() => {
    loadCases()
    loadActivePreview()
    loadAnalysts()
  }, [])

  useEffect(() => {
    if (activeCase?.id) {
      loadCaseActivities(activeCase.id)
      loadActivitySummary(activeCase.id)
    }
  }, [activeCase?.id])

  useEffect(() => {
    // When active case changes, refresh active preview
    loadActivePreview()
  }, [activeCase?.id])

  useEffect(() => {
    filterCases()
  }, [cases, searchTerm, statusFilter, priorityFilter])

  const loadCases = async () => {
    try {
      setLoading(true)
      const response = await apiClient.getCasesForReports() as any
      if (response.data?.data?.cases) {
        setCases(response.data.data.cases)
      }
    } catch (error: any) {
      console.error('Error loading cases:', error)
      toast({
        title: "Error",
        description: "Failed to load cases for reports",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  const filterCases = () => {
    let filtered = cases

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(case_ => 
        case_.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        case_.case_number.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(case_ => case_.status === statusFilter)
    }

    // Priority filter
    if (priorityFilter !== 'all') {
      filtered = filtered.filter(case_ => case_.priority === priorityFilter)
    }

    setFilteredCases(filtered)
  }

  const loadActivePreview = async () => {
    try {
      setActiveLoading(true)
      const res = await apiClient.previewActiveCaseReport()
      if ((res as any)?.data) setActivePreview((res as any).data)
    } catch (e) {
      setActivePreview(null)
    } finally {
      setActiveLoading(false)
    }
  }

  const loadAnalysts = async () => {
    try {
      const response = await apiClient.getUsers() as any
      if (response.data?.data?.users) {
        const analystData = response.data.data.users.map((user: any) => ({
          id: user.id,
          username: user.username,
          email: user.email,
          role: user.role,
          total_activities: 0,
          total_time_spent: 0,
          active_cases: 0
        }))
        setAnalysts(analystData)
      }
    } catch (error: any) {
      console.error('Error loading analysts:', error)
      toast({
        title: "Error",
        description: "Failed to load analysts",
        variant: "destructive"
      })
    }
  }

  const loadCaseActivities = async (caseId: number) => {
    try {
      setActivityLoading(true)
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000'}/api/cases/${caseId}/activities`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      })
      
      if (response.ok) {
        const data = await response.json()
        setAnalystActivities(data.activities || [])
      }
    } catch (error: any) {
      console.error('Error loading case activities:', error)
      toast({
        title: "Error",
        description: "Failed to load case activities",
        variant: "destructive"
      })
    } finally {
      setActivityLoading(false)
    }
  }

  const loadActivitySummary = async (caseId: number) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000'}/api/cases/${caseId}/activities/summary`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      })
      
      if (response.ok) {
        const data = await response.json()
        setActivitySummary(data)
      }
    } catch (error: any) {
      console.error('Error loading activity summary:', error)
    }
  }

  const generateReport = async (caseId: number) => {
    try {
      setGeneratingReports(prev => new Set(prev).add(caseId))
      
      // Get the API base URL from environment or use default
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000'
      const response = await fetch(`${apiBaseUrl}/api/reports/${caseId}/generate`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      })

      if (!response.ok) {
        throw new Error('Failed to generate report')
      }

      // Get the filename from the response headers
      const contentDisposition = response.headers.get('content-disposition')
      const filename = contentDisposition 
        ? contentDisposition.split('filename=')[1]?.replace(/"/g, '')
        : `Case_${caseId}_Report.pdf`

      // Create blob and download
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      toast({
        title: "Success",
        description: "Report generated and downloaded successfully",
      })
    } catch (error: any) {
      console.error('Error generating report:', error)
      toast({
        title: "Error",
        description: "Failed to generate report",
        variant: "destructive"
      })
    } finally {
      setGeneratingReports(prev => {
        const newSet = new Set(prev)
        newSet.delete(caseId)
        return newSet
      })
    }
  }

  const generateAndPreviewPdf = async (caseId: number) => {
    try {
      setPdfGenerating(true)
      
      // Get the API base URL from environment or use default
      let apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000'
      console.log('Generating PDF for case:', caseId, 'API URL:', apiBaseUrl)
      console.log('Environment API URL:', process.env.NEXT_PUBLIC_API_URL)
      
      // Ensure we have a complete URL - if truncated, use hardcoded fallback
      if (!apiBaseUrl || apiBaseUrl.length < 10 || apiBaseUrl.includes('127.0.0')) {
        apiBaseUrl = 'http://127.0.0.1:5000'
        console.log('Using fallback API URL:', apiBaseUrl)
      }
      
      // Try the detailed PDF generation endpoint first
      let response = await fetch(`${apiBaseUrl}/api/reports/${caseId}/generate-detailed?include_activities=true&include_content=true`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      })
      
      // If detailed endpoint fails, try the basic endpoint
      if (!response.ok) {
        console.log('Detailed PDF generation failed, trying basic endpoint...')
        response = await fetch(`${apiBaseUrl}/api/reports/${caseId}/generate`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          },
        })
      }

      console.log('PDF generation response:', response.status, response.statusText)
      console.log('Content-Type:', response.headers.get('content-type'))
      console.log('Response URL:', response.url)

      if (!response.ok) {
        const errorText = await response.text()
        console.error('PDF generation failed:', errorText)
        console.error('Full response:', response)
        throw new Error(`Failed to generate report: ${response.status} ${response.statusText}. Error: ${errorText}`)
      }

      // Create blob for preview
      const blob = await response.blob()
      console.log('PDF blob created:', blob.size, 'bytes, type:', blob.type)
      
      if (blob.size === 0) {
        throw new Error('Generated PDF is empty')
      }
      
      const url = window.URL.createObjectURL(blob)
      console.log('PDF preview URL created:', url)
      
      setPdfPreviewUrl(url)
      setShowPdfPreviewDialog(true)

      toast({
        title: "PDF Generated",
        description: "PDF preview is ready. You can now download it.",
      })
    } catch (error: any) {
      console.error('Error generating PDF preview:', error)
      toast({
        title: "Error",
        description: `Failed to generate PDF preview: ${error.message}`,
        variant: "destructive"
      })
    } finally {
      setPdfGenerating(false)
    }
  }

  const downloadPdfFromPreview = () => {
    if (pdfPreviewUrl && activeCase) {
      const caseData = cases.find(c => c.id === activeCase.id)
      const filename = `case_${caseData?.case_number || activeCase.id}_detailed_${new Date().toISOString().split('T')[0]}.pdf`
      const a = document.createElement('a')
      a.href = pdfPreviewUrl
      a.download = filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      
      toast({
        title: "Download Started",
        description: "PDF download has started",
      })
    }
  }

  const closePdfPreview = () => {
    if (pdfPreviewUrl) {
      window.URL.revokeObjectURL(pdfPreviewUrl)
      setPdfPreviewUrl(null)
    }
    setShowPdfPreviewDialog(false)
  }

  const debugApiConnection = async () => {
    try {
      const apiBaseUrl = 'http://127.0.0.1:5000'
      console.log('Testing API connection to:', apiBaseUrl)
      
      // Test basic health endpoint
      const healthResponse = await fetch(`${apiBaseUrl}/api/health`)
      console.log('Health check:', healthResponse.status, healthResponse.statusText)
      
      // Test reports endpoint
      const reportsResponse = await fetch(`${apiBaseUrl}/api/reports/1/generate-detailed`)
      console.log('Reports endpoint:', reportsResponse.status, reportsResponse.statusText)
      
      toast({
        title: "Debug Info",
        description: `Health: ${healthResponse.status}, Reports: ${reportsResponse.status}`,
      })
    } catch (error: any) {
      console.error('Debug connection error:', error)
      toast({
        title: "Debug Error",
        description: `Connection failed: ${error.message}`,
        variant: "destructive"
      })
    }
  }

  const generateDetailedReport = async (caseId: number) => {
    try {
      setGeneratingReports(prev => new Set(prev).add(caseId))
      
      const blob = await apiClient.generateDetailedCaseReport(caseId, {
        include_activities: true,
        include_content: true
      })
      
      const caseData = cases.find(c => c.id === caseId)
      const filename = `case_${caseData?.case_number || caseId}_detailed_${new Date().toISOString().split('T')[0]}.pdf`
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      toast({
        title: "Success",
        description: "Detailed report with activities downloaded successfully",
      })
    } catch (error: any) {
      console.error('Error generating detailed report:', error)
      toast({
        title: "Error",
        description: "Failed to generate detailed report",
        variant: "destructive"
      })
    } finally {
      setGeneratingReports(prev => {
        const newSet = new Set(prev)
        newSet.delete(caseId)
        return newSet
      })
    }
  }

  const previewReport = async (caseId: number) => {
    try {
      setPreviewLoading(true)
      const response = await apiClient.previewCaseReport(caseId) as any
      if (response.data?.data) {
        setReportPreview(response.data.data)
        setPreviewDialog({ open: true, caseId })
      }
    } catch (error: any) {
      console.error('Error loading report preview:', error)
      toast({
        title: "Error",
        description: "Failed to load report preview",
        variant: "destructive"
      })
    } finally {
      setPreviewLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'open': return 'bg-blue-500/20 text-blue-400 border-blue-400/30'
      case 'in_progress': return 'bg-yellow-500/20 text-yellow-400 border-yellow-400/30'
      case 'resolved': return 'bg-green-500/20 text-green-400 border-green-400/30'
      case 'closed': return 'bg-gray-500/20 text-gray-400 border-gray-400/30'
      default: return 'bg-gray-500/20 text-gray-400 border-gray-400/30'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'critical': return 'bg-red-500/20 text-red-400 border-red-400/30'
      case 'high': return 'bg-orange-500/20 text-orange-400 border-orange-400/30'
      case 'medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-400/30'
      case 'low': return 'bg-green-500/20 text-green-400 border-green-400/30'
      default: return 'bg-gray-500/20 text-gray-400 border-gray-400/30'
    }
  }

  if (loading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-[radial-gradient(1200px_600px_at_50%_-10%,rgba(14,165,233,0.18),transparent),radial-gradient(800px_400px_at_80%_10%,rgba(16,185,129,0.12),transparent)] flex items-center justify-center">
          <div className="flex flex-col items-center space-y-4">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            <p className="text-muted-foreground font-medium">Loading reports...</p>
          </div>
        </div>
      </ProtectedRoute>
    )
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-[radial-gradient(1200px_600px_at_50%_-10%,rgba(14,165,233,0.18),transparent),radial-gradient(800px_400px_at_80%_10%,rgba(16,185,129,0.12),transparent)]">
        {/* Header */}
        <div className="glassmorphism border-b border-white/10 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <FileText className="h-8 w-8 text-primary" />
                  <h1 className="text-2xl font-bold bg-gradient-to-r from-primary to-cyan-400 bg-clip-text text-transparent">
                    Investigation Reports
                  </h1>
                </div>
                <Badge variant="secondary" className="ml-2 bg-primary/20 text-primary border-primary/30">
                  Generate & Download
                </Badge>
              </div>
              <div className="flex items-center space-x-4">
                <Button 
                  onClick={loadCases} 
                  variant="outline" 
                  size="sm" 
                  className="border-white/10 hover:bg-white/5"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Refresh
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
          {/* Active Case Section */}
          <div className="mb-8">
            <Card className="glassmorphism">
              <CardHeader className="flex flex-row items-center justify-between">
                <div className="flex items-center gap-2">
                  <Star className="h-5 w-5 text-yellow-400" />
                  <CardTitle className="text-lg">Active Case</CardTitle>
                </div>
                {activeCase && (
                  <div className="text-sm text-muted-foreground">Case #{activeCase?.case_number}</div>
                )}
              </CardHeader>
              <CardContent>
                {activeCase ? (
                  <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                    <div>
                      <div className="text-foreground font-semibold">{activeCase.title}</div>
                      <div className="text-sm text-muted-foreground">{activeCase.type?.replace(/_/g, ' ')}</div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        className="border-white/10 hover:bg-white/5"
                        onClick={() => {
                          if (activeCase?.id) previewReport(activeCase.id)
                        }}
                        disabled={previewLoading || activeLoading}
                      >
                        {previewLoading || activeLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Eye className="h-4 w-4" />}
                        <span className="ml-2">Preview</span>
                      </Button>
                      <Button
                        className="bg-primary hover:bg-primary/90"
                        onClick={() => {
                          if (activeCase?.id) generateAndPreviewPdf(activeCase.id)
                        }}
                        disabled={pdfGenerating}
                      >
                        {pdfGenerating ? <Loader2 className="h-4 w-4 animate-spin" /> : <Download className="h-4 w-4" />}
                        <span className="ml-2">Generate PDF</span>
                      </Button>
                      <Button
                        variant="outline"
                        onClick={debugApiConnection}
                        className="ml-2"
                      >
                        Debug API
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="text-muted-foreground">No active case selected.</div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Analyst Activity Tracking Section */}
          {activeCase && (
            <div className="mb-8">
              <Card className="glassmorphism">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Activity className="h-5 w-5 text-primary" />
                      <CardTitle className="text-lg">Analyst Activity Tracking</CardTitle>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setShowActivityDialog(true)}
                        className="border-white/10 hover:bg-white/5"
                      >
                        <Plus className="h-4 w-4 mr-2" />
                        Add Activity
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => activeCase?.id && loadCaseActivities(activeCase.id)}
                        className="border-white/10 hover:bg-white/5"
                      >
                        <RefreshCw className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                  <CardDescription>
                    Track and manage all analyst activities for Case #{activeCase.case_number}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {/* Activity Summary Stats */}
                  {activitySummary && (
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                      <div className="text-center p-4 border border-white/10 rounded-lg">
                        <div className="text-2xl font-bold text-primary">{activitySummary.total_activities}</div>
                        <div className="text-sm text-muted-foreground">Total Activities</div>
                      </div>
                      <div className="text-center p-4 border border-white/10 rounded-lg">
                        <div className="text-2xl font-bold text-orange-400">{activitySummary.total_time_spent_hours}h</div>
                        <div className="text-sm text-muted-foreground">Time Tracked</div>
                      </div>
                      <div className="text-center p-4 border border-white/10 rounded-lg">
                        <div className="text-2xl font-bold text-green-400">{activitySummary.report_items_count}</div>
                        <div className="text-sm text-muted-foreground">Report Items</div>
                      </div>
                      <div className="text-center p-4 border border-white/10 rounded-lg">
                        <div className="text-2xl font-bold text-blue-400">{Object.keys(activitySummary.by_analyst).length}</div>
                        <div className="text-sm text-muted-foreground">Contributors</div>
                      </div>
                    </div>
                  )}

                  {/* Activity Filters */}
                  <div className="flex flex-wrap gap-4 mb-6">
                    <Select value={selectedAnalyst?.toString() || 'all'} onValueChange={(value) => setSelectedAnalyst(value === 'all' ? null : parseInt(value))}>
                      <SelectTrigger className="w-48">
                        <SelectValue placeholder="Filter by analyst" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Analysts</SelectItem>
                        {analysts.map((analyst) => (
                          <SelectItem key={analyst.id} value={analyst.id.toString()}>
                            {analyst.username}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    
                    <Select value={activityTypeFilter} onValueChange={setActivityTypeFilter}>
                      <SelectTrigger className="w-48">
                        <SelectValue placeholder="Filter by type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Types</SelectItem>
                        <SelectItem value="note">Notes</SelectItem>
                        <SelectItem value="finding">Findings</SelectItem>
                        <SelectItem value="evidence">Evidence</SelectItem>
                        <SelectItem value="interview">Interviews</SelectItem>
                        <SelectItem value="analysis">Analysis</SelectItem>
                        <SelectItem value="action">Actions</SelectItem>
                        <SelectItem value="meeting">Meetings</SelectItem>
                        <SelectItem value="communication">Communication</SelectItem>
                        <SelectItem value="task">Tasks</SelectItem>
                        <SelectItem value="update">Updates</SelectItem>
                        <SelectItem value="milestone">Milestones</SelectItem>
                        <SelectItem value="observation">Observations</SelectItem>
                        <SelectItem value="recommendation">Recommendations</SelectItem>
                        <SelectItem value="decision">Decisions</SelectItem>
                        <SelectItem value="investigation">User Investigation</SelectItem>
                        <SelectItem value="content_analysis">Content Analysis</SelectItem>
                        <SelectItem value="osint_search">OSINT Search</SelectItem>
                        <SelectItem value="batch_analysis">Batch Analysis</SelectItem>
                        <SelectItem value="platform_scraping">Platform Scraping</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                      </SelectContent>
                    </Select>

                    <Select value={activityFilter} onValueChange={setActivityFilter}>
                      <SelectTrigger className="w-48">
                        <SelectValue placeholder="Filter by status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Status</SelectItem>
                        <SelectItem value="active">Active</SelectItem>
                        <SelectItem value="completed">Completed</SelectItem>
                        <SelectItem value="draft">Draft</SelectItem>
                        <SelectItem value="archived">Archived</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Activities List */}
                  <div className="space-y-4">
                    {activityLoading ? (
                      <div className="flex items-center justify-center py-8">
                        <Loader2 className="h-8 w-8 animate-spin text-primary" />
                        <span className="ml-2 text-muted-foreground">Loading activities...</span>
                      </div>
                    ) : analystActivities.length > 0 ? (
                      analystActivities
                        .filter(activity => {
                          if (selectedAnalyst && activity.analyst_id !== selectedAnalyst) return false
                          if (activityTypeFilter !== 'all' && activity.activity_type !== activityTypeFilter) return false
                          if (activityFilter !== 'all' && activity.status !== activityFilter) return false
                          return true
                        })
                        .map((activity) => (
                          <div key={activity.id} className="p-4 border border-white/10 rounded-lg hover:border-white/20 transition-colors">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-2">
                                  <Badge variant="outline" className="text-xs">
                                    {activity.activity_type}
                                  </Badge>
                                  <Badge className={getPriorityColor(activity.priority)}>
                                    {activity.priority}
                                  </Badge>
                                  {activity.include_in_report && (
                                    <Badge variant="secondary" className="text-xs">
                                      <FileText className="h-3 w-3 mr-1" />
                                      In Report
                                    </Badge>
                                  )}
                                  {activity.is_confidential && (
                                    <Badge variant="destructive" className="text-xs">
                                      <Shield className="h-3 w-3 mr-1" />
                                      Confidential
                                    </Badge>
                                  )}
                                </div>
                                <h4 className="font-semibold text-foreground mb-1">{activity.title}</h4>
                                <p className="text-sm text-muted-foreground mb-2">{activity.description}</p>
                                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                                  <div className="flex items-center gap-1">
                                    <User className="h-3 w-3" />
                                    {activity.analyst.username}
                                  </div>
                                  <div className="flex items-center gap-1">
                                    <Calendar className="h-3 w-3" />
                                    {new Date(activity.activity_date).toLocaleDateString()}
                                  </div>
                                  <div className="flex items-center gap-1">
                                    <Timer className="h-3 w-3" />
                                    {activity.time_spent_minutes} min
                                  </div>
                                  {activity.tags && activity.tags.length > 0 && (
                                    <div className="flex items-center gap-1">
                                      <Target className="h-3 w-3" />
                                      {activity.tags.join(', ')}
                                    </div>
                                  )}
                                </div>
                              </div>
                              <div className="flex items-center gap-2 ml-4">
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => {
                                    setEditingActivity(activity)
                                    setShowActivityDialog(true)
                                  }}
                                  className="border-white/10 hover:bg-white/5"
                                >
                                  <Edit className="h-4 w-4" />
                                </Button>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => {
                                    setPreviewActivity(activity)
                                    setShowActivityPreviewDialog(true)
                                  }}
                                  className="border-white/10 hover:bg-white/5"
                                  title="Preview activity"
                                >
                                  <Eye className="h-4 w-4" />
                                </Button>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => {
                                    // Toggle report inclusion
                                    const updatedActivities = analystActivities.map(a => 
                                      a.id === activity.id ? { ...a, include_in_report: !a.include_in_report } : a
                                    )
                                    setAnalystActivities(updatedActivities)
                                  }}
                                  className={`border-white/10 hover:bg-white/5 ${activity.include_in_report ? 'bg-green-500/20 text-green-400' : ''}`}
                                  title={activity.include_in_report ? 'Remove from report' : 'Include in report'}
                                >
                                  <FileText className="h-4 w-4" />
                                </Button>
                              </div>
                            </div>
                          </div>
                        ))
                    ) : (
                      <div className="text-center py-8">
                        <Activity className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                        <p className="text-muted-foreground font-medium">No activities found</p>
                        <p className="text-sm text-muted-foreground/70 mt-1">
                          Start tracking analyst work by adding activities
                        </p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Stats Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card className="glassmorphism">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground flex items-center">
                  <FileText className="h-4 w-4 mr-2 text-primary" />
                  Total Cases
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-foreground">{cases.length}</div>
                <p className="text-xs text-muted-foreground mt-1">Available for reports</p>
              </CardContent>
            </Card>

            <Card className="glassmorphism">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground flex items-center">
                  <AlertTriangle className="h-4 w-4 mr-2 text-red-400" />
                  High Priority
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-red-400">
                  {cases.filter(c => c.priority === 'high' || c.priority === 'critical').length}
                </div>
                <p className="text-xs text-muted-foreground mt-1">Require attention</p>
              </CardContent>
            </Card>

            <Card className="glassmorphism">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground flex items-center">
                  <Clock className="h-4 w-4 mr-2 text-yellow-400" />
                  In Progress
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-yellow-400">
                  {cases.filter(c => c.status === 'in_progress').length}
                </div>
                <p className="text-xs text-muted-foreground mt-1">Active investigations</p>
              </CardContent>
            </Card>

            <Card className="glassmorphism">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground flex items-center">
                  <CheckCircle className="h-4 w-4 mr-2 text-green-400" />
                  Completed
                </CardTitle>
            </CardHeader>
            <CardContent>
                <div className="text-3xl font-bold text-green-400">
                  {cases.filter(c => c.status === 'resolved' || c.status === 'closed').length}
                </div>
                <p className="text-xs text-muted-foreground mt-1">Ready for reports</p>
            </CardContent>
        </Card>
      </div>

          {/* Filters and Search */}
          <Card className="glassmorphism mb-6">
            <CardHeader>
              <CardTitle className="text-lg font-semibold text-foreground flex items-center">
                <Filter className="h-5 w-5 mr-2 text-primary" />
                Filter Cases
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search cases..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger>
                    <SelectValue placeholder="Filter by status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Statuses</SelectItem>
                    <SelectItem value="open">Open</SelectItem>
                    <SelectItem value="in_progress">In Progress</SelectItem>
                    <SelectItem value="resolved">Resolved</SelectItem>
                    <SelectItem value="closed">Closed</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={priorityFilter} onValueChange={setPriorityFilter}>
                  <SelectTrigger>
                    <SelectValue placeholder="Filter by priority" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Priorities</SelectItem>
                    <SelectItem value="critical">Critical</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="low">Low</SelectItem>
                  </SelectContent>
                </Select>
                <Button 
                  onClick={() => {
                    setSearchTerm('')
                    setStatusFilter('all')
                    setPriorityFilter('all')
                  }}
                  variant="outline"
                  className="border-white/10 hover:bg-white/5"
                >
                  Clear Filters
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Cases Table */}
          <Card className="glassmorphism">
            <CardHeader>
              <CardTitle className="text-xl font-semibold text-foreground flex items-center">
                <BarChart3 className="h-5 w-5 mr-2 text-primary" />
                Case Reports ({filteredCases.length})
              </CardTitle>
              <CardDescription className="text-muted-foreground">
                Generate comprehensive PDF reports for investigation cases
                {activeCase ? ` • Active Case: ${activeCase.title}` : ''}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {filteredCases.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Case Details</TableHead>
                      <TableHead>Status & Priority</TableHead>
                      <TableHead>Statistics</TableHead>
                      <TableHead>Last Updated</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredCases.map((case_) => (
                      <TableRow key={case_.id}>
                        <TableCell>
                          <div>
                            <div className="font-medium text-foreground">{case_.title}</div>
                            <div className="text-sm text-muted-foreground">
                              Case #{case_.case_number}
                            </div>
                            <div className="text-xs text-muted-foreground mt-1">
                              {case_.type.replace(/_/g, ' ').toLowerCase()}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="space-y-2">
                            <Badge className={getStatusColor(case_.status)}>
                              {case_.status.replace('_', ' ').toUpperCase()}
                            </Badge>
                            <Badge className={getPriorityColor(case_.priority)}>
                              {case_.priority.toUpperCase()}
                            </Badge>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="text-sm space-y-1">
                            <div className="flex items-center space-x-2">
                              <AlertTriangle className="h-3 w-3 text-red-400" />
                              <span>{case_.statistics.flagged_content} flagged posts</span>
                            </div>
                            <div className="flex items-center space-x-2">
                              <User className="h-3 w-3 text-orange-400" />
                              <span>{case_.statistics.platform_users} flagged users</span>
                            </div>
                            <div className="flex items-center space-x-2">
                              <Shield className="h-3 w-3 text-blue-400" />
                              <span>{case_.statistics.osint_results} OSINT results</span>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="text-sm">
                            <div className="flex items-center space-x-1">
                              <Calendar className="h-3 w-3 text-muted-foreground" />
                              <span>{new Date(case_.updated_at).toLocaleDateString()}</span>
                            </div>
                            <div className="text-xs text-muted-foreground">
                              {new Date(case_.updated_at).toLocaleTimeString()}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center space-x-2">
                            <Button
                              onClick={() => previewReport(case_.id)}
                              variant="outline"
                              size="sm"
                              className="border-white/10 hover:bg-white/5"
                              disabled={previewLoading}
                              title="Preview report"
                            >
                              {previewLoading ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                              ) : (
                                <Eye className="h-4 w-4" />
                              )}
                            </Button>
                            <Button
                              onClick={() => generateReport(case_.id)}
                              variant="outline"
                              size="sm"
                              disabled={generatingReports.has(case_.id)}
                              title="Download basic report"
                            >
                              {generatingReports.has(case_.id) ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                              ) : (
                                <Download className="h-4 w-4" />
                              )}
                            </Button>
                            <Button
                              onClick={() => generateDetailedReport(case_.id)}
                              size="sm"
                              className="bg-primary hover:bg-primary/90"
                              disabled={generatingReports.has(case_.id)}
                              title="Download detailed report with activities"
                            >
                              {generatingReports.has(case_.id) ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                              ) : (
                                <FileBarChart className="h-4 w-4" />
                              )}
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-12">
                  <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground font-medium">No cases found</p>
                  <p className="text-sm text-muted-foreground/70 mt-1">
                    {searchTerm || statusFilter !== 'all' || priorityFilter !== 'all'
                      ? 'Try adjusting your filters'
                      : 'No cases available for report generation'
                    }
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
    </main>

        {/* Activity Dialog */}
        <Dialog open={showActivityDialog} onOpenChange={setShowActivityDialog}>
          <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="flex items-center space-x-2">
                <Activity className="h-5 w-5 text-primary" />
                <span>{editingActivity ? 'Edit Activity' : 'Add New Activity'}</span>
              </DialogTitle>
              <DialogDescription>
                {editingActivity ? 'Update the activity details' : 'Track analyst work and investigation activities'}
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-foreground mb-2 block">Activity Type</label>
                  <Select defaultValue={editingActivity?.activity_type || 'note'}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select activity type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="note">Note</SelectItem>
                      <SelectItem value="finding">Finding</SelectItem>
                      <SelectItem value="evidence">Evidence</SelectItem>
                      <SelectItem value="interview">Interview</SelectItem>
                      <SelectItem value="analysis">Analysis</SelectItem>
                      <SelectItem value="action">Action</SelectItem>
                      <SelectItem value="meeting">Meeting</SelectItem>
                      <SelectItem value="communication">Communication</SelectItem>
                      <SelectItem value="task">Task</SelectItem>
                      <SelectItem value="update">Update</SelectItem>
                      <SelectItem value="milestone">Milestone</SelectItem>
                      <SelectItem value="observation">Observation</SelectItem>
                      <SelectItem value="recommendation">Recommendation</SelectItem>
                      <SelectItem value="decision">Decision</SelectItem>
                      <SelectItem value="investigation">User Investigation</SelectItem>
                      <SelectItem value="content_analysis">Content Analysis</SelectItem>
                      <SelectItem value="osint_search">OSINT Search</SelectItem>
                      <SelectItem value="batch_analysis">Batch Analysis</SelectItem>
                      <SelectItem value="platform_scraping">Platform Scraping</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-foreground mb-2 block">Priority</label>
                  <Select defaultValue={editingActivity?.priority || 'medium'}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select priority" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="critical">Critical</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-foreground mb-2 block">Title</label>
                <Input 
                  placeholder="Activity title" 
                  defaultValue={editingActivity?.title || ''}
                />
              </div>

              <div>
                <label className="text-sm font-medium text-foreground mb-2 block">Description</label>
                <textarea 
                  className="w-full min-h-[100px] p-3 border border-white/10 rounded-lg bg-transparent text-foreground placeholder:text-muted-foreground focus:border-primary/50 focus:outline-none"
                  placeholder="Detailed description of the activity..."
                  defaultValue={editingActivity?.description || ''}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-foreground mb-2 block">Time Spent (minutes)</label>
                  <Input 
                    type="number" 
                    placeholder="0" 
                    defaultValue={editingActivity?.time_spent_minutes || 0}
                  />
                </div>
                
                <div>
                  <label className="text-sm font-medium text-foreground mb-2 block">Activity Date</label>
                  <Input 
                    type="datetime-local" 
                    defaultValue={editingActivity?.activity_date ? new Date(editingActivity.activity_date).toISOString().slice(0, 16) : new Date().toISOString().slice(0, 16)}
                  />
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-foreground mb-2 block">Tags (comma-separated)</label>
                <Input 
                  placeholder="investigation, suspect-a, evidence" 
                  defaultValue={editingActivity?.tags?.join(', ') || ''}
                />
              </div>

              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <input 
                    type="checkbox" 
                    id="include_in_report" 
                    defaultChecked={editingActivity?.include_in_report ?? true}
                    className="rounded border-white/10"
                  />
                  <label htmlFor="include_in_report" className="text-sm text-foreground">
                    Include in PDF report
                  </label>
                </div>
                
                <div className="flex items-center space-x-2">
                  <input 
                    type="checkbox" 
                    id="is_confidential" 
                    defaultChecked={editingActivity?.is_confidential ?? false}
                    className="rounded border-white/10"
                  />
                  <label htmlFor="is_confidential" className="text-sm text-foreground">
                    Mark as confidential
                  </label>
                </div>
              </div>
            </div>

            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => {
                  setShowActivityDialog(false)
                  setEditingActivity(null)
                }}
              >
                Cancel
              </Button>
              <Button
                onClick={() => {
                  // Handle save activity
                  setShowActivityDialog(false)
                  setEditingActivity(null)
                  if (activeCase?.id) {
                    loadCaseActivities(activeCase.id)
                    loadActivitySummary(activeCase.id)
                  }
                }}
                className="bg-primary hover:bg-primary/90"
              >
                {editingActivity ? 'Update Activity' : 'Create Activity'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Report Preview Dialog */}
        <Dialog open={previewDialog.open} onOpenChange={(open) => setPreviewDialog({ open, caseId: null })}>
          <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="flex items-center space-x-2">
                <Eye className="h-5 w-5 text-primary" />
                <span>Report Preview - Case #{reportPreview?.case.case_number}</span>
              </DialogTitle>
              <DialogDescription>
                Preview of the investigation report before generating the PDF
              </DialogDescription>
            </DialogHeader>
            
            {reportPreview && (
              <div className="space-y-6">
                {/* Case Overview */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Case Overview</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">Case Name</p>
                        <p className="text-foreground">{reportPreview.case.title}</p>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">Status</p>
                        <Badge className={getStatusColor(reportPreview.case.status)}>
                          {reportPreview.case.status.replace('_', ' ').toUpperCase()}
                        </Badge>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">Priority</p>
                        <Badge className={getPriorityColor(reportPreview.case.priority)}>
                          {reportPreview.case.priority.toUpperCase()}
                        </Badge>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">Created</p>
                        <p className="text-foreground">{new Date(reportPreview.case.created_at).toLocaleDateString()}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Statistics */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Investigation Statistics</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-primary">{reportPreview.statistics.flagged_posts}</div>
                        <div className="text-sm text-muted-foreground">Flagged Posts</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-orange-400">{reportPreview.statistics.flagged_users}</div>
                        <div className="text-sm text-muted-foreground">Flagged Users</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-400">{reportPreview.statistics.osint_results}</div>
                        <div className="text-sm text-muted-foreground">OSINT Results</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-400">{reportPreview.statistics.platforms_analyzed.split(',').length}</div>
                        <div className="text-sm text-muted-foreground">Platforms</div>
                      </div>
                    </div>
                    <div className="mt-4">
                      <p className="text-sm font-medium text-muted-foreground">Platforms Analyzed</p>
                      <p className="text-foreground">{reportPreview.statistics.platforms_analyzed}</p>
                    </div>
                  </CardContent>
                </Card>

                {/* Flagged Content Summary */}
                {reportPreview.flagged_content_summary.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Flagged Content Summary</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {reportPreview.flagged_content_summary.map((content, index) => (
                          <div key={content.id} className="p-3 border border-white/10 rounded-lg">
                            <div className="flex items-center justify-between mb-2">
                              <div className="flex items-center space-x-2">
                                <span className="font-medium">{content.author}</span>
                                <Badge variant="outline" className="text-xs">
                                  {content.platform}
                                </Badge>
                              </div>
                              <div className="flex items-center space-x-2">
                                <Badge className={getPriorityColor(content.risk_level)}>
                                  {content.risk_level}
                                </Badge>
                                <span className="text-sm text-muted-foreground">
                                  Score: {content.suspicion_score}
                                </span>
                              </div>
                            </div>
                            <div className="text-sm text-muted-foreground">
                              Intent: {content.intent} • {new Date(content.created_at).toLocaleDateString()}
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* OSINT Results Summary */}
                {reportPreview.osint_results_summary.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">OSINT Results Summary</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {reportPreview.osint_results_summary.map((result, index) => (
                          <div key={result.id} className="p-3 border border-white/10 rounded-lg">
                            <div className="flex items-center justify-between mb-2">
                              <div className="flex items-center space-x-2">
                                <span className="font-medium">{result.query}</span>
                                <Badge variant="outline" className="text-xs">
                                  {result.search_type}
                                </Badge>
                              </div>
                              <div className="flex items-center space-x-2">
                                <Badge className={getStatusColor(result.status)}>
                                  {result.status}
                                </Badge>
                                <span className="text-sm text-muted-foreground">
                                  Risk: {result.risk_score}
                                </span>
                              </div>
                            </div>
                            <div className="text-sm text-muted-foreground">
                              {new Date(result.created_at).toLocaleDateString()}
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            )}

            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setPreviewDialog({ open: false, caseId: null })}
              >
                Close
              </Button>
              {previewDialog.caseId && (
                <Button
                  onClick={() => {
                    setPreviewDialog({ open: false, caseId: null })
                    generateReport(previewDialog.caseId!)
                  }}
                  className="bg-primary hover:bg-primary/90"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Generate PDF Report
                </Button>
              )}
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Activity Preview Dialog */}
        <Dialog open={showActivityPreviewDialog} onOpenChange={setShowActivityPreviewDialog}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle className="flex items-center space-x-2">
                <Eye className="h-5 w-5 text-primary" />
                <span>Activity Preview</span>
              </DialogTitle>
              <DialogDescription>
                Preview of the selected activity details
              </DialogDescription>
            </DialogHeader>
            
            {previewActivity && (
              <div className="space-y-6">
                {/* Activity Header */}
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-foreground">{previewActivity.title}</h3>
                    <p className="text-sm text-muted-foreground mt-1">{previewActivity.description}</p>
                  </div>
                  <div className="flex space-x-2">
                    <Badge variant={previewActivity.priority === 'high' ? 'destructive' : previewActivity.priority === 'medium' ? 'default' : 'secondary'}>
                      {previewActivity.priority}
                    </Badge>
                    <Badge variant="outline">
                      {previewActivity.activity_type}
                    </Badge>
                    {previewActivity.include_in_report && (
                      <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
                        In Report
                      </Badge>
                    )}
                  </div>
                </div>

                {/* Activity Details */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-3">
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Analyst</label>
                      <p className="text-sm text-foreground">{previewActivity.analyst?.username || 'Unknown'}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Status</label>
                      <p className="text-sm text-foreground capitalize">{previewActivity.status}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Activity Date</label>
                      <p className="text-sm text-foreground">
                        {new Date(previewActivity.activity_date).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Time Spent</label>
                      <p className="text-sm text-foreground">{previewActivity.time_spent_minutes} minutes</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Created</label>
                      <p className="text-sm text-foreground">
                        {new Date(previewActivity.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Confidential</label>
                      <p className="text-sm text-foreground">
                        {previewActivity.is_confidential ? 'Yes' : 'No'}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Tags */}
                {previewActivity.tags && previewActivity.tags.length > 0 && (
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Tags</label>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {previewActivity.tags.map((tag, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {/* Activity Metadata */}
                {previewActivity.metadata && Object.keys(previewActivity.metadata).length > 0 && (
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Additional Information</label>
                    <div className="mt-2 p-3 bg-muted/50 rounded-lg">
                      <pre className="text-xs text-foreground whitespace-pre-wrap">
                        {JSON.stringify(previewActivity.metadata, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            )}

            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setShowActivityPreviewDialog(false)}
              >
                Close
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* PDF Preview Dialog */}
        <Dialog open={showPdfPreviewDialog} onOpenChange={closePdfPreview}>
          <DialogContent className="max-w-6xl max-h-[90vh]">
            <DialogHeader>
              <DialogTitle className="flex items-center space-x-2">
                <FileText className="h-5 w-5 text-primary" />
                <span>PDF Preview - {activeCase?.title}</span>
              </DialogTitle>
              <DialogDescription>
                Preview the generated PDF report before downloading
              </DialogDescription>
            </DialogHeader>
            
            {pdfPreviewUrl && (
              <div className="flex-1 min-h-0">
                <div className="mb-4 p-3 bg-muted/50 rounded-lg">
                  <p className="text-sm text-muted-foreground">
                    PDF Preview - If the PDF doesn't display, try downloading it directly.
                  </p>
                </div>
                <iframe
                  src={pdfPreviewUrl}
                  className="w-full h-[70vh] border rounded-lg"
                  title="PDF Preview"
                  onError={() => {
                    console.error('PDF iframe failed to load')
                    toast({
                      title: "Preview Error",
                      description: "PDF preview failed to load. You can still download the PDF.",
                      variant: "destructive"
                    })
                  }}
                />
                <div className="mt-4 text-center">
                  <p className="text-sm text-muted-foreground">
                    If the PDF doesn't appear above, click "Download PDF" to save it to your device.
                  </p>
                </div>
              </div>
            )}

            <DialogFooter className="flex justify-between">
              <Button
                variant="outline"
                onClick={closePdfPreview}
              >
                Close Preview
              </Button>
              <Button
                onClick={downloadPdfFromPreview}
                className="bg-primary hover:bg-primary/90"
              >
                <Download className="h-4 w-4 mr-2" />
                Download PDF
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </ProtectedRoute>
  )
}