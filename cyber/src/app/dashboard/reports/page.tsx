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
  FileBarChart
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

  useEffect(() => {
    loadCases()
    loadActivePreview()
  }, [])

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
                          if (activeCase?.id) generateReport(activeCase.id)
                        }}
                        disabled={generatingReports.has(activeCase?.id)}
                      >
                        {generatingReports.has(activeCase?.id) ? <Loader2 className="h-4 w-4 animate-spin" /> : <Download className="h-4 w-4" />}
                        <span className="ml-2">Generate PDF</span>
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="text-muted-foreground">No active case selected.</div>
                )}
              </CardContent>
            </Card>
          </div>

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
      </div>
    </ProtectedRoute>
  )
}