"use client"

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import ProtectedRoute from '@/components/ProtectedRoute'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { apiClient } from '@/lib/api'
import { CaseActivities } from '@/components/case-activities'
import { CaseActivitiesSummary } from '@/components/case-activities-summary'
import { ArrowLeft, Download, FileText, Activity, Info } from 'lucide-react'
import { format } from 'date-fns'

interface Case {
  id: number
  title: string
  case_number: string
  description: string
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
}

export default function CaseDetailsPage() {
  const params = useParams()
  const router = useRouter()
  const caseId = parseInt(params.id as string)
  
  const [caseData, setCaseData] = useState<Case | null>(null)
  const [loading, setLoading] = useState(true)
  const [downloading, setDownloading] = useState(false)

  useEffect(() => {
    loadCase()
  }, [caseId])

  const loadCase = async () => {
    try {
      setLoading(true)
      const response: any = await apiClient.get(`/api/cases/${caseId}`)
      setCaseData(response)
    } catch (error) {
      console.error('Failed to load case:', error)
    } finally {
      setLoading(false)
    }
  }

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
      a.download = `case_${caseData?.case_number}_report_${format(new Date(), 'yyyyMMdd')}.pdf`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Failed to generate report:', error)
      alert('Failed to generate report. Please try again.')
    } finally {
      setDownloading(false)
    }
  }

  if (loading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <div className="text-lg">Loading case details...</div>
          </div>
        </div>
      </ProtectedRoute>
    )
  }

  if (!caseData) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <div className="text-lg text-red-500">Case not found</div>
            <Button onClick={() => router.back()} className="mt-4">
              Go Back
            </Button>
          </div>
        </div>
      </ProtectedRoute>
    )
  }

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
    <ProtectedRoute>
      <div className="min-h-screen">
        <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-6">
            <Button 
              variant="ghost" 
              onClick={() => router.back()}
              className="mb-4"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Cases
            </Button>

            <Card className="bg-black/40 border-white/10">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-2xl mb-2">{caseData.title}</CardTitle>
                    <CardDescription className="flex items-center gap-2 text-base">
                      <span className="font-mono">{caseData.case_number}</span>
                      <Badge className={statusColors[caseData.status]}>
                        {caseData.status.replace('_', ' ').toUpperCase()}
                      </Badge>
                      <Badge className={priorityColors[caseData.priority]}>
                        {caseData.priority.toUpperCase()}
                      </Badge>
                      <Badge variant="outline">
                        Risk: {caseData.risk_level.toUpperCase()}
                      </Badge>
                    </CardDescription>
                  </div>
                  <Button onClick={downloadDetailedReport} disabled={downloading}>
                    <Download className="w-4 h-4 mr-2" />
                    {downloading ? 'Generating...' : 'Download PDF Report'}
                  </Button>
                </div>
              </CardHeader>
            </Card>
          </div>

          {/* Activities Summary */}
          <div className="mb-6">
            <CaseActivitiesSummary caseId={caseId} />
          </div>

          {/* Tabs */}
          <Tabs defaultValue="overview" className="space-y-4">
            <TabsList className="bg-black/40 border-white/10">
              <TabsTrigger value="overview" className="data-[state=active]:bg-white/10">
                <Info className="w-4 h-4 mr-2" />
                Overview
              </TabsTrigger>
              <TabsTrigger value="activities" className="data-[state=active]:bg-white/10">
                <Activity className="w-4 h-4 mr-2" />
                Activities
              </TabsTrigger>
              <TabsTrigger value="details" className="data-[state=active]:bg-white/10">
                <FileText className="w-4 h-4 mr-2" />
                Details
              </TabsTrigger>
            </TabsList>

            {/* Overview Tab */}
            <TabsContent value="overview" className="space-y-4">
              <Card className="bg-black/40 border-white/10">
                <CardHeader>
                  <CardTitle>Case Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-sm text-muted-foreground">Type</div>
                      <div className="font-medium">{caseData.type.replace(/_/g, ' ')}</div>
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground">Progress</div>
                      <div className="font-medium">{caseData.progress_percentage}%</div>
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground">Start Date</div>
                      <div className="font-medium">{format(new Date(caseData.start_date), 'MMM dd, yyyy')}</div>
                    </div>
                    {caseData.due_date && (
                      <div>
                        <div className="text-sm text-muted-foreground">Due Date</div>
                        <div className="font-medium">{format(new Date(caseData.due_date), 'MMM dd, yyyy')}</div>
                      </div>
                    )}
                  </div>

                  {caseData.description && (
                    <div>
                      <div className="text-sm text-muted-foreground mb-1">Description</div>
                      <p className="text-sm">{caseData.description}</p>
                    </div>
                  )}

                  {caseData.summary && (
                    <div>
                      <div className="text-sm text-muted-foreground mb-1">Summary</div>
                      <p className="text-sm whitespace-pre-wrap">{caseData.summary}</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* Activities Tab */}
            <TabsContent value="activities">
              <CaseActivities caseId={caseId} />
            </TabsContent>

            {/* Details Tab */}
            <TabsContent value="details" className="space-y-4">
              {caseData.objectives && (
                <Card className="bg-black/40 border-white/10">
                  <CardHeader>
                    <CardTitle>Objectives</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm whitespace-pre-wrap">{caseData.objectives}</p>
                  </CardContent>
                </Card>
              )}

              {caseData.methodology && (
                <Card className="bg-black/40 border-white/10">
                  <CardHeader>
                    <CardTitle>Methodology</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm whitespace-pre-wrap">{caseData.methodology}</p>
                  </CardContent>
                </Card>
              )}

              {caseData.findings && (
                <Card className="bg-black/40 border-white/10">
                  <CardHeader>
                    <CardTitle>Findings</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm whitespace-pre-wrap">{caseData.findings}</p>
                  </CardContent>
                </Card>
              )}

              {caseData.recommendations && (
                <Card className="bg-black/40 border-white/10">
                  <CardHeader>
                    <CardTitle>Recommendations</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm whitespace-pre-wrap">{caseData.recommendations}</p>
                  </CardContent>
                </Card>
              )}
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </ProtectedRoute>
  )
}

