'use client'

import { useEffect, useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import apiClient from '@/lib/api'
import ProtectedRoute from '@/components/ProtectedRoute'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { useRouter } from 'next/navigation'
import { useActiveCase } from '@/contexts/ActiveCaseContext'
import { 
  Plus, 
  Search, 
  Filter, 
  FileText, 
  Users, 
  Clock, 
  AlertTriangle,
  CheckCircle,
  XCircle,
  Eye,
  Edit,
  Trash2,
  UserPlus,
  BarChart3,
  RefreshCw,
  Calendar,
  Tag,
  Archive
} from 'lucide-react'
import { toast } from '@/hooks/use-toast'
import CreateCaseDialog from '@/components/cases/CreateCaseDialog'
import CaseDetailsDialog from '@/components/cases/CaseDetailsDialog'
import CaseStatistics from '@/components/cases/CaseStatistics'
import CaseRequestStatus from '@/components/cases/CaseRequestStatus'

interface Case {
  id: number
  title: string
  description?: string
  case_number: string
  type: string
  status: string
  priority: string
  created_by_id: number
  summary?: string
  objectives?: string
  methodology?: string
  findings?: string
  recommendations?: string
  risk_score: number
  risk_level: string
  tags?: string[]
  start_date: string
  created_at: string
  updated_at: string
  user_count: number
  content_count: number
}

interface CaseFilters {
  status: string
  priority: string
  type: string
  search: string
}

export default function CasesPage() {
  const { user } = useAuth()
  const router = useRouter()
  const { setActiveCase: setActiveCaseSession, refreshActiveCase } = useActiveCase()
  const [cases, setCases] = useState<Case[]>([])
  const [loading, setLoading] = useState(true)
  const [canCreateCase, setCanCreateCase] = useState<boolean | null>(null)
  const [checkingPermission, setCheckingPermission] = useState(false)
  const [filters, setFilters] = useState<CaseFilters>({
    status: '',
    priority: '',
    type: '',
    search: ''
  })
  const [selectedCase, setSelectedCase] = useState<Case | null>(null)
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [showDetailsDialog, setShowDetailsDialog] = useState(false)
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 10,
    total: 0,
    pages: 0,
    has_next: false,
    has_prev: false
  })

  // Fetch cases
  const fetchCases = async (page = 1) => {
    try {
      setLoading(true)
      console.log('🔄 Fetching cases...')
      
      toast({
        title: "Loading Cases",
        description: "Fetching your cases...",
        duration: 1000
      })
      
      const params = new URLSearchParams({
        page: page.toString(),
        per_page: pagination.per_page.toString()
      })

      // Add filters
      if (filters.status && filters.status !== 'all') params.append('status', filters.status)
      if (filters.priority && filters.priority !== 'all') params.append('priority', filters.priority)
      if (filters.type && filters.type !== 'all') params.append('type', filters.type)

      console.log('📡 Fetching cases with params:', params.toString())
      const response = await apiClient.get(`/api/cases/?${params.toString()}`)
      console.log('📡 Cases response:', response)
      
      // Handle the direct API response format
      let casesData, paginationData, status
      
      if (response && response.status === 'success') {
        // Standard API response format
        casesData = response.data
        paginationData = response.pagination
        status = response.status
      } else if (Array.isArray(response)) {
        // Direct array response (fallback)
        casesData = response
        paginationData = {
          page: 1,
          per_page: casesData.length,
          total: casesData.length,
          pages: 1,
          has_next: false,
          has_prev: false
        }
        status = 'success'
      } else {
        // Handle other response formats
        casesData = response?.data || []
        paginationData = response?.pagination || {
          page: 1,
          per_page: 10,
          total: 0,
          pages: 0,
          has_next: false,
          has_prev: false
        }
        status = response?.status || 'success'
      }
      
      if (status === 'success') {
        console.log('✅ Cases fetched successfully:', {
          casesCount: casesData?.length || 0,
          pagination: paginationData
        })
        
        setCases(casesData || [])
        setPagination(paginationData || {
          page: 1,
          per_page: 10,
          total: 0,
          pages: 0,
          has_next: false,
          has_prev: false
        })
        
        const casesList = casesData as Case[] || []
        const activeCases = casesList.filter((c: Case) => !['closed', 'archived', 'resolved'].includes(c.status))
        const closedCases = casesList.filter((c: Case) => ['closed', 'archived', 'resolved'].includes(c.status))
        
        toast({
          title: "Cases Loaded",
          description: `Found ${activeCases.length} active cases and ${closedCases.length} archived cases`,
          duration: 2000
        })
        
        if (casesData && casesData.length === 0) {
          console.log('ℹ️ No cases found')
        }
      } else {
        console.error('❌ Failed to fetch cases:', response)
        toast({
          title: "Error",
          description: response?.message || "Failed to fetch cases",
          variant: "destructive"
        })
      }
    } catch (error) {
      console.error('❌ Error fetching cases:', error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to fetch cases",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  const checkCanCreate = async () => {
    try {
      setCheckingPermission(true)
      const res = await apiClient.canCreateCase()
      if ((res as any)?.status === 'success') {
        const canCreate = (res as any).can_create
        setCanCreateCase(canCreate)
        
        toast({
          title: "Permission Check",
          description: canCreate ? "You can create a new case" : "Admin approval required for new cases",
          duration: 2000
        })
      } else {
        setCanCreateCase(null)
      }
    } catch (e) {
      setCanCreateCase(null)
      toast({
        title: "Permission Check Failed",
        description: "Could not verify case creation permissions",
        variant: "destructive"
      })
    } finally {
      setCheckingPermission(false)
    }
  }

  useEffect(() => {
    fetchCases()
    checkCanCreate()
  }, [filters])

  const handleFilterChange = (key: keyof CaseFilters, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }))
    
    toast({
      title: "Filter Applied",
      description: `Updated ${key} filter`,
      duration: 1000
    })
  }

  const handleCaseClick = (caseItem: Case) => {
    console.log('🔍 Opening case details for:', caseItem.title, 'ID:', caseItem.id)
    setSelectedCase(caseItem)
    setShowDetailsDialog(true)
    
    toast({
      title: "Opening Case Details",
      description: `Viewing details for case: ${caseItem.title}`,
      duration: 1500
    })
  }

  const handleCreateCase = async (caseData: any) => {
    try {
      // Debug: Check if user is authenticated
      const token = localStorage.getItem('access_token')
      console.log('🔐 Debug - Token exists:', !!token)
      console.log('🔐 Debug - Token preview:', token ? token.substring(0, 50) + '...' : 'No token')
      
      console.log('📝 Creating case with data:', caseData)
      const response = await apiClient.post('/api/cases/', caseData)
      console.log('📝 Case creation response:', response)
      
      if (response.status === 'success') {
        // Check if this was a case creation request
        if (response.requires_approval) {
          toast({
            title: "Case Request Submitted",
            description: response.message,
            duration: 4000
          })
          toast({
            title: "Admin Approval Required",
            description: "Your case creation request has been submitted for admin approval. You'll be notified once it's reviewed.",
            duration: 5000
          })
        } else {
          toast({
            title: "Success",
            description: `Case "${response.data.title}" created successfully!`,
            duration: 3000
          })
          
          // Refresh the cases list
          console.log('🔄 Refreshing cases list...')
          await fetchCases()
          console.log('✅ Cases list refreshed')
          
          // Set newly created case as active session case
          try {
            if (response.data?.id) {
              await setActiveCaseSession(response.data.id)
              await refreshActiveCase()
              toast({ title: 'Active Case Set', description: `Now working on ${response.data.title}` })
            }
          } catch (e) {
            // ignore
          }

          // Show updated count
          setTimeout(() => {
            toast({
              title: "Cases Updated",
              description: `Total cases: ${cases.length + 1}`,
              duration: 2000
            })
          }, 500)
        }
        
        setShowCreateDialog(false)
      } else {
        console.error('❌ Case creation failed:', response)
        toast({
          title: "Error",
          description: response.message || "Failed to create case",
          variant: "destructive"
        })
      }
    } catch (error) {
      console.error('❌ Error creating case:', error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to create case",
        variant: "destructive"
      })
    }
  }

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      open: { variant: 'default' as const, icon: FileText },
      in_progress: { variant: 'secondary' as const, icon: Clock },
      pending: { variant: 'outline' as const, icon: AlertTriangle },
      resolved: { variant: 'default' as const, icon: CheckCircle },
      closed: { variant: 'destructive' as const, icon: XCircle },
      archived: { variant: 'secondary' as const, icon: FileText }
    }

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.open
    const Icon = config.icon

    return (
      <Badge variant={config.variant} className="flex items-center gap-1">
        <Icon className="w-3 h-3" />
        {status.replace('_', ' ').toUpperCase()}
      </Badge>
    )
  }

  const getPriorityBadge = (priority: string) => {
    const priorityConfig = {
      low: { variant: 'outline' as const, color: 'text-gray-600' },
      medium: { variant: 'secondary' as const, color: 'text-blue-600' },
      high: { variant: 'default' as const, color: 'text-orange-600' },
      critical: { variant: 'destructive' as const, color: 'text-red-600' }
    }

    const config = priorityConfig[priority as keyof typeof priorityConfig] || priorityConfig.medium

    return (
      <Badge variant={config.variant} className={config.color}>
        {priority.toUpperCase()}
      </Badge>
    )
  }

  const filteredCases = cases.filter(caseItem => {
    // Exclude closed/archived cases from "All Cases" tab
    if (['closed', 'archived', 'resolved'].includes(caseItem.status)) {
      return false
    }
    
    if (filters.search) {
      return caseItem.title.toLowerCase().includes(filters.search.toLowerCase()) ||
             caseItem.case_number.toLowerCase().includes(filters.search.toLowerCase())
    }
    return true
  })

  // Fallback: infer if user likely has an active case when permission check fails
  const hasActiveCase = cases.some(c => ['open', 'in_progress', 'pending'].includes(c.status))
  const createButtonLabel = checkingPermission
    ? 'Checking…'
    : (canCreateCase === null
        ? (hasActiveCase ? 'Request New Case' : 'Create New Case')
        : (canCreateCase ? 'Create New Case' : 'Request New Case'))

  return (
    <ProtectedRoute>
      <div className="container mx-auto p-6 space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Cases</h1>
            <p className="text-muted-foreground">
              Manage investigation cases and track suspicious activities
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => {
              toast({
                title: "Refreshing Cases",
                description: "Reloading case data...",
                duration: 1000
              })
              fetchCases()
            }} disabled={loading} className="flex items-center gap-2">
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          <Button onClick={() => {
            toast({
              title: "Opening Create Case Dialog",
              description: hasActiveCase ? "This will submit a request for admin approval" : "Creating a new case",
              duration: 1500
            })
            setShowCreateDialog(true)
          }} className="flex items-center gap-2">
            <Plus className="w-4 h-4" />
            {createButtonLabel}
          </Button>
          </div>
        </div>

        <Tabs defaultValue="cases" className="space-y-6">
          <TabsList>
            <TabsTrigger value="cases">All Cases</TabsTrigger>
            <TabsTrigger value="archives">Case Archives</TabsTrigger>
            <TabsTrigger value="requests">My Requests</TabsTrigger>
            <TabsTrigger value="statistics">Statistics</TabsTrigger>
          </TabsList>

          <TabsContent value="cases" className="space-y-6">
            {/* Filters */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Filter className="w-4 h-4" />
                  Filters
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="search">Search</Label>
                    <div className="relative">
                      <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="search"
                        placeholder="Search cases..."
                        value={filters.search}
                        onChange={(e) => handleFilterChange('search', e.target.value)}
                        className="pl-10"
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="status">Status</Label>
                    <Select value={filters.status} onValueChange={(value) => handleFilterChange('status', value)}>
                      <SelectTrigger>
                        <SelectValue placeholder="All statuses" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All statuses</SelectItem>
                        <SelectItem value="open">Open</SelectItem>
                        <SelectItem value="in_progress">In Progress</SelectItem>
                        <SelectItem value="pending">Pending</SelectItem>
                        <SelectItem value="resolved">Resolved</SelectItem>
                        <SelectItem value="closed">Closed</SelectItem>
                        <SelectItem value="archived">Archived</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="priority">Priority</Label>
                    <Select value={filters.priority} onValueChange={(value) => handleFilterChange('priority', value)}>
                      <SelectTrigger>
                        <SelectValue placeholder="All priorities" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All priorities</SelectItem>
                        <SelectItem value="low">Low</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="high">High</SelectItem>
                        <SelectItem value="critical">Critical</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="type">Type</Label>
                    <Select value={filters.type} onValueChange={(value) => handleFilterChange('type', value)}>
                      <SelectTrigger>
                        <SelectValue placeholder="All types" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All types</SelectItem>
                        <SelectItem value="drug_trafficking_investigation">Drug Trafficking Investigation</SelectItem>
                        <SelectItem value="substance_abuse_detection">Substance Abuse Detection</SelectItem>
                        <SelectItem value="social_media_monitoring">Social Media Monitoring</SelectItem>
                        <SelectItem value="suspicious_content_analysis">Suspicious Content Analysis</SelectItem>
                        <SelectItem value="user_behavior_analysis">User Behavior Analysis</SelectItem>
                        <SelectItem value="network_disruption">Network Disruption</SelectItem>
                        <SelectItem value="compliance_enforcement">Compliance Enforcement</SelectItem>
                        <SelectItem value="custom">Custom</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Cases List */}
            <div className="grid gap-4">
              {loading ? (
                <div className="flex items-center justify-center h-32">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </div>
              ) : filteredCases.length === 0 ? (
                <Card>
                  <CardContent className="flex flex-col items-center justify-center py-12">
                    <FileText className="h-12 w-12 text-muted-foreground mb-4" />
                    <h3 className="text-lg font-semibold mb-2">No cases found</h3>
                    <p className="text-muted-foreground text-center mb-4">
                      {filters.search || filters.status || filters.priority || filters.type
                        ? "No cases match your current filters"
                        : "Get started by creating your first investigation case"}
                    </p>
                    <Button onClick={() => {
                      toast({
                        title: "Opening Create Case Dialog",
                        description: hasActiveCase ? "This will submit a request for admin approval" : "Creating a new case",
                        duration: 1500
                      })
                      setShowCreateDialog(true)
                    }}>
                      <Plus className="w-4 h-4 mr-2" />
                      {createButtonLabel}
                    </Button>
                  </CardContent>
                </Card>
              ) : (
                filteredCases.map((caseItem) => (
                  <Card key={caseItem.id} className="hover:shadow-md transition-shadow cursor-pointer" onClick={() => handleCaseClick(caseItem)}>
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between">
                        <div className="space-y-2 flex-1">
                          <div className="flex items-center gap-2">
                            <h3 className="text-lg font-semibold">{caseItem.title}</h3>
                            {getStatusBadge(caseItem.status)}
                            {getPriorityBadge(caseItem.priority)}
                          </div>
                          
                          <p className="text-sm text-muted-foreground">
                            {caseItem.case_number} • {caseItem.type.replace('_', ' ').toUpperCase()}
                          </p>
                          
                          {caseItem.description && (
                            <p className="text-sm text-muted-foreground line-clamp-2">
                              {caseItem.description}
                            </p>
                          )}
                          
                          <div className="flex items-center gap-4 text-sm text-muted-foreground">
                            <div className="flex items-center gap-1">
                              <Users className="w-4 h-4" />
                              {caseItem.user_count} users
                            </div>
                            <div className="flex items-center gap-1">
                              <FileText className="w-4 h-4" />
                              {caseItem.content_count} content
                            </div>
                            <div className="flex items-center gap-1">
                              <Calendar className="w-4 h-4" />
                              {new Date(caseItem.created_at).toLocaleDateString()}
                            </div>
                          </div>

                          {caseItem.tags && caseItem.tags.length > 0 && (
                            <div className="flex items-center gap-1 flex-wrap">
                              <Tag className="w-3 h-3 text-muted-foreground" />
                              {caseItem.tags.map((tag, index) => (
                                <Badge key={index} variant="outline" className="text-xs">
                                  {tag}
                                </Badge>
                              ))}
                            </div>
                          )}
                        </div>
                        
                        <div className="flex items-center gap-2">
                          <Button 
                            variant="ghost" 
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation()
                              handleCaseClick(caseItem)
                            }}
                            title="View case details"
                          >
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={async (e) => {
                              e.stopPropagation()
                              try {
                                await setActiveCaseSession(caseItem.id)
                                await refreshActiveCase()
                                toast({ title: 'Active Case Set', description: `Now working on ${caseItem.title}` })
                              } catch (err) {
                                toast({ title: 'Failed to set active case', variant: 'destructive' })
                              }
                            }}
                            title="Set as Active Case"
                          >
                            Set Active
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>

            {/* Pagination */}
            {pagination.pages > 1 && (
              <div className="flex items-center justify-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => fetchCases(pagination.page - 1)}
                  disabled={!pagination.has_prev}
                >
                  Previous
                </Button>
                <span className="text-sm text-muted-foreground">
                  Page {pagination.page} of {pagination.pages}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => fetchCases(pagination.page + 1)}
                  disabled={!pagination.has_next}
                >
                  Next
                </Button>
              </div>
            )}
          </TabsContent>

          {/* Archives Tab - Closed cases only */}
          <TabsContent value="archives" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Archive className="w-4 h-4" />
                  Case Archives
                </CardTitle>
                <CardDescription>
                  View cases that have been closed. Archived items are read-only.
                </CardDescription>
              </CardHeader>
            </Card>

            <div className="grid gap-4">
              {loading ? (
                <div className="flex items-center justify-center h-32">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </div>
              ) : (
                (() => {
                  const archivedCases = cases.filter(c => ['closed', 'archived', 'resolved'].includes(c.status))
                  if (archivedCases.length === 0) {
                    return (
                      <Card>
                        <CardContent className="flex flex-col items-center justify-center py-12">
                          <FileText className="h-12 w-12 text-muted-foreground mb-4" />
                          <h3 className="text-lg font-semibold mb-2">No archived cases</h3>
                          <p className="text-muted-foreground text-center">
                            Closed cases will appear here for reference.
                          </p>
                        </CardContent>
                      </Card>
                    )
                  }
                  return archivedCases.map((caseItem) => (
                    <Card key={caseItem.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-6">
                        <div className="flex items-start justify-between">
                          <div className="space-y-2 flex-1">
                            <div className="flex items-center gap-2">
                              <h3 className="text-lg font-semibold">{caseItem.title}</h3>
                              {getStatusBadge(caseItem.status)}
                              {getPriorityBadge(caseItem.priority)}
                            </div>
                            <p className="text-sm text-muted-foreground">
                              {caseItem.case_number} • {caseItem.type.replace('_', ' ').toUpperCase()}
                            </p>
                            {caseItem.description && (
                              <p className="text-sm text-muted-foreground line-clamp-2">
                                {caseItem.description}
                              </p>
                            )}
                          </div>
                          <div className="flex items-center gap-2">
                            <Badge variant="outline">Archived</Badge>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))
                })()
              )}
            </div>
          </TabsContent>

          <TabsContent value="requests">
            <CaseRequestStatus />
          </TabsContent>

          <TabsContent value="statistics">
            <CaseStatistics />
          </TabsContent>
        </Tabs>

        {/* Dialogs */}
        <CreateCaseDialog
          open={showCreateDialog}
          onOpenChange={setShowCreateDialog}
          onCreateCase={handleCreateCase}
        />

        {selectedCase && (
          <CaseDetailsDialog
            open={showDetailsDialog}
            onOpenChange={setShowDetailsDialog}
            caseId={selectedCase.id}
            onCaseUpdate={fetchCases}
          />
        )}
      </div>
    </ProtectedRoute>
  )
}
