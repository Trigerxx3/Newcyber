'use client'

import { useEffect, useState } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import apiClient from '@/lib/api'
import { toast } from '@/hooks/use-toast'
import { Download, Info, Activity, FileText } from 'lucide-react'
import { CaseActivities } from '@/components/case-activities'
import { CaseActivitiesSummary } from '@/components/case-activities-summary'
import { format } from 'date-fns'

interface CaseDetails {
  id: number
  title: string
  description?: string
  case_number: string
  status: string
  priority: string
  type: string
  risk_level: string
  risk_score: number
  progress_percentage: number
  created_at: string
  updated_at: string
  start_date: string
  due_date?: string
  summary?: string
  objectives?: string
  methodology?: string
  findings?: string
  recommendations?: string
  linked_users?: Array<any>
  linked_content?: Array<any>
  statistics?: {
    user_count: number
    days_open: number
  }
}

interface CaseDetailsDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  caseId: number
  onCaseUpdate: () => void
}

export default function CaseDetailsDialog({ open, onOpenChange, caseId, onCaseUpdate }: CaseDetailsDialogProps) {
  const [caseDetails, setCaseDetails] = useState<CaseDetails | null>(null)
  const [loading, setLoading] = useState(false)
  const [downloading, setDownloading] = useState(false)

  const fetchCaseDetails = async () => {
    try {
      setLoading(true)
      console.log('🔍 Fetching case details for ID:', caseId)
      const response: any = await apiClient.get(`/api/cases/${caseId}`)
      console.log('📡 Case details response:', response)
      
      if (response) {
        setCaseDetails(response.data || response)
        console.log('✅ Case details loaded successfully')
      }
    } catch (error) {
      console.error('❌ Error fetching case details:', error)
      toast({ title: 'Error', description: 'Failed to fetch case details', variant: 'destructive' })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (open && caseId) {
      fetchCaseDetails()
    }
  }, [open, caseId])

  const downloadDetailedReport = async () => {
    try {
      setDownloading(true)
      const blob = await apiClient.generateDetailedCaseReport(caseId, {
        include_activities: true,
        include_content: true
      })
      
      // Create download link
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `case_${caseDetails?.case_number}_report_${format(new Date(), 'yyyyMMdd')}.pdf`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
      
      toast({ title: 'Success', description: 'Report downloaded successfully' })
    } catch (error) {
      console.error('Failed to generate report:', error)
      toast({ title: 'Error', description: 'Failed to generate report', variant: 'destructive' })
    } finally {
      setDownloading(false)
    }
  }

  if (loading) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Loading Case Details...</DialogTitle>
          </DialogHeader>
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        </DialogContent>
      </Dialog>
    )
  }

  if (!caseDetails) return null

  const statusColors: Record<string, string> = {
    open: 'bg-blue-100 text-blue-800',
    in_progress: 'bg-yellow-100 text-yellow-800',
    pending: 'bg-orange-100 text-orange-800',
    resolved: 'bg-green-100 text-green-800',
    closed: 'bg-gray-100 text-gray-800'
  }

  const priorityColors: Record<string, string> = {
    low: 'bg-green-100 text-green-800',
    medium: 'bg-yellow-100 text-yellow-800',
    high: 'bg-orange-100 text-orange-800',
    critical: 'bg-red-100 text-red-800'
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex justify-between items-start">
            <div>
              <DialogTitle className="text-2xl mb-2">{caseDetails.title}</DialogTitle>
              <div className="flex items-center gap-2 text-sm">
                <span className="font-mono">{caseDetails.case_number}</span>
                <Badge className={statusColors[caseDetails.status]}>
                  {caseDetails.status.replace('_', ' ').toUpperCase()}
                </Badge>
                <Badge className={priorityColors[caseDetails.priority]}>
                  {caseDetails.priority.toUpperCase()}
                </Badge>
                <Badge variant="outline">
                  Risk: {caseDetails.risk_level?.toUpperCase()}
                </Badge>
              </div>
            </div>
            <Button onClick={downloadDetailedReport} disabled={downloading} size="sm">
              <Download className="w-4 h-4 mr-2" />
              {downloading ? 'Generating...' : 'PDF Report'}
            </Button>
          </div>
        </DialogHeader>

        <div className="mt-4">
          <CaseActivitiesSummary caseId={caseId} />
        </div>

        <Tabs defaultValue="overview" className="mt-4">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="overview">
              <Info className="w-4 h-4 mr-2" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="activities">
              <Activity className="w-4 h-4 mr-2" />
              Activities
            </TabsTrigger>
            <TabsTrigger value="details">
              <FileText className="w-4 h-4 mr-2" />
              Details
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4 mt-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <div className="text-muted-foreground">Type</div>
                <div className="font-medium">{caseDetails.type?.replace(/_/g, ' ')}</div>
              </div>
              <div>
                <div className="text-muted-foreground">Progress</div>
                <div className="font-medium">{caseDetails.progress_percentage}%</div>
              </div>
              <div>
                <div className="text-muted-foreground">Start Date</div>
                <div className="font-medium">
                  {caseDetails.start_date ? format(new Date(caseDetails.start_date), 'MMM dd, yyyy') : 'N/A'}
                </div>
              </div>
              {caseDetails.due_date && (
                <div>
                  <div className="text-muted-foreground">Due Date</div>
                  <div className="font-medium">{format(new Date(caseDetails.due_date), 'MMM dd, yyyy')}</div>
                </div>
              )}
            </div>

            {caseDetails.description && (
              <div>
                <div className="text-sm text-muted-foreground mb-1">Description</div>
                <p className="text-sm">{caseDetails.description}</p>
              </div>
            )}

            {caseDetails.summary && (
              <div>
                <div className="text-sm text-muted-foreground mb-1">Summary</div>
                <p className="text-sm whitespace-pre-wrap">{caseDetails.summary}</p>
              </div>
            )}
          </TabsContent>

          <TabsContent value="activities" className="mt-4">
            <CaseActivities caseId={caseId} />
          </TabsContent>

          <TabsContent value="details" className="space-y-4 mt-4">
            {caseDetails.objectives && (
              <div>
                <div className="text-sm font-medium mb-1">Objectives</div>
                <p className="text-sm whitespace-pre-wrap">{caseDetails.objectives}</p>
              </div>
            )}

            {caseDetails.methodology && (
              <div>
                <div className="text-sm font-medium mb-1">Methodology</div>
                <p className="text-sm whitespace-pre-wrap">{caseDetails.methodology}</p>
              </div>
            )}

            {caseDetails.findings && (
              <div>
                <div className="text-sm font-medium mb-1">Findings</div>
                <p className="text-sm whitespace-pre-wrap">{caseDetails.findings}</p>
              </div>
            )}

            {caseDetails.recommendations && (
              <div>
                <div className="text-sm font-medium mb-1">Recommendations</div>
                <p className="text-sm whitespace-pre-wrap">{caseDetails.recommendations}</p>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  )
}
