'use client'

import { useEffect, useState } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import apiClient from '@/lib/api'
import { toast } from '@/hooks/use-toast'
import { Download, Info, Activity, FileText, Link, Plus, ExternalLink, Tag } from 'lucide-react'
import { CaseActivities } from '@/components/case-activities'
import { CaseActivitiesSummary } from '@/components/case-activities-summary'
import LinkContentDialog from './LinkContentDialog'
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
  linked_content?: Array<{
    id: number
    content_id: number
    case_id: number
    linked_at: string
    content?: {
      id: number
      text: string
      author: string
      platform: string
      created_at: string
      url?: string
      keywords?: string[]
      sentiment_score?: number
      risk_level?: string
      is_flagged?: boolean
    }
    image_analysis?: {
      image_path?: string | null
      image_prediction?: string
      image_confidence?: number
      image_risk_score?: number
      text_risk_score?: number
      final_score?: number
      final_prediction?: string
    } | null
  }>
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
  const [showLinkContentDialog, setShowLinkContentDialog] = useState(false)

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

  const formatDate = (dateString: string | undefined): string => {
    if (!dateString) return 'Unknown date'
    
    const date = new Date(dateString)
    if (isNaN(date.getTime())) return 'Invalid date'
    
    return format(date, 'MMM dd, yyyy HH:mm')
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
            <div className="flex gap-2">
              <Button 
                onClick={() => setShowLinkContentDialog(true)} 
                variant="outline" 
                size="sm"
              >
                <Link className="w-4 h-4 mr-2" />
                Link Content
              </Button>
              <Button onClick={downloadDetailedReport} disabled={downloading} size="sm">
                <Download className="w-4 h-4 mr-2" />
                {downloading ? 'Generating...' : 'PDF Report'}
              </Button>
            </div>
          </div>
        </DialogHeader>

        <div className="mt-4">
          <CaseActivitiesSummary caseId={caseId} />
        </div>

        <Tabs defaultValue="overview" className="mt-4">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">
              <Info className="w-4 h-4 mr-2" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="activities">
              <Activity className="w-4 h-4 mr-2" />
              Activities
            </TabsTrigger>
            <TabsTrigger value="content">
              <Link className="w-4 h-4 mr-2" />
              Content
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

          <TabsContent value="content" className="space-y-4 mt-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold">Linked Content</h3>
                <p className="text-sm text-muted-foreground">
                  Scraped content linked to this case ({caseDetails?.linked_content?.length || 0} items)
                </p>
              </div>
              <Button 
                onClick={() => setShowLinkContentDialog(true)} 
                variant="outline" 
                size="sm"
              >
                <Plus className="w-4 h-4 mr-2" />
                Link More Content
              </Button>
            </div>
            
            {/* Display linked content */}
            {caseDetails?.linked_content && caseDetails.linked_content.length > 0 ? (
              <div className="space-y-4">
                {caseDetails.linked_content.map((link) => (
                  <Card key={link.id} className="glassmorphism">
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="border-white/20 text-muted-foreground">
                            {link.content?.platform || 'Unknown'}
                          </Badge>
                          <span className="text-sm text-foreground">
                            @{link.content?.author || 'Unknown'}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            {formatDate(link.content?.created_at)}
                          </span>
                        </div>
                        
                        <div className="flex items-center gap-2">
                          {link.content?.risk_level && (
                            <Badge variant="outline" className="text-xs border-white/20 text-muted-foreground">
                              Risk: {link.content.risk_level}
                            </Badge>
                          )}
                          {link.content?.is_flagged && (
                            <Badge variant="destructive" className="text-xs bg-destructive/20 text-destructive border-destructive/30">
                              Flagged
                            </Badge>
                          )}
                        </div>
                      </div>

                      <p className="text-sm mb-2 line-clamp-2 text-foreground">
                        {link.content?.text || 'No content text available'}
                      </p>

                      {link.content?.keywords && link.content.keywords.length > 0 && (
                        <div className="flex items-center gap-1 mb-2">
                          <Tag className="w-3 h-3 text-muted-foreground" />
                          <div className="flex flex-wrap gap-1">
                            {link.content.keywords.map((keyword, index) => (
                              <Badge key={index} variant="secondary" className="text-xs bg-white/10 text-muted-foreground border-white/20">
                                {keyword}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}

                      {link.image_analysis && (
                        <div className="mt-3 rounded-md border border-cyan-500/30 bg-cyan-500/5 p-3">
                          <div className="mb-2 flex items-center justify-between">
                            <span className="text-sm font-medium text-cyan-300">Computer Vision Analysis</span>
                            <Badge
                              variant={link.image_analysis.final_prediction === 'Drug-Related' ? 'destructive' : 'secondary'}
                              className="text-xs"
                            >
                              {link.image_analysis.final_prediction || 'Unknown'}
                            </Badge>
                          </div>

                          <div className="grid grid-cols-2 gap-3 text-xs">
                            <div>
                              <div className="text-muted-foreground">Image Prediction</div>
                              <div className="font-medium text-foreground">
                                {link.image_analysis.image_prediction || 'N/A'}
                              </div>
                            </div>
                            <div>
                              <div className="text-muted-foreground">Image Confidence</div>
                              <div className="font-medium text-foreground">
                                {link.image_analysis.image_confidence !== undefined
                                  ? `${(link.image_analysis.image_confidence * 100).toFixed(1)}%`
                                  : 'N/A'}
                              </div>
                            </div>
                            <div>
                              <div className="text-muted-foreground">Image Risk Score</div>
                              <div className="font-medium text-foreground">
                                {link.image_analysis.image_risk_score !== undefined
                                  ? `${(link.image_analysis.image_risk_score * 100).toFixed(1)}%`
                                  : 'N/A'}
                              </div>
                            </div>
                            <div>
                              <div className="text-muted-foreground">Text Risk Score</div>
                              <div className="font-medium text-foreground">
                                {link.image_analysis.text_risk_score !== undefined
                                  ? `${(link.image_analysis.text_risk_score * 100).toFixed(1)}%`
                                  : 'N/A'}
                              </div>
                            </div>
                            <div className="col-span-2">
                              <div className="text-muted-foreground">Final Fused Score (0.6 text + 0.4 image)</div>
                              <div className="font-semibold text-foreground">
                                {link.image_analysis.final_score !== undefined
                                  ? `${(link.image_analysis.final_score * 100).toFixed(1)}%`
                                  : 'N/A'}
                              </div>
                            </div>
                          </div>

                          {link.image_analysis.image_path && (
                            <div className="mt-2 text-xs text-muted-foreground">
                              Image Path: {link.image_analysis.image_path}
                            </div>
                          )}
                        </div>
                      )}

                      <div className="flex items-center gap-4 text-xs text-muted-foreground">
                        <span className="text-xs text-muted-foreground">
                          Linked: {formatDate(link.linked_at)}
                        </span>
                        {link.content?.url && (
                          <a 
                            href={link.content.url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="flex items-center gap-1 text-primary hover:text-primary/80"
                          >
                            <ExternalLink className="w-3 h-3" />
                            View Original
                          </a>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <Link className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                <p>No content linked to this case yet</p>
                <p className="text-sm">Click "Link More Content" to add scraped content</p>
              </div>
            )}
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

        {/* Link Content Dialog */}
        <LinkContentDialog
          open={showLinkContentDialog}
          onOpenChange={setShowLinkContentDialog}
          caseId={caseId}
          caseTitle={caseDetails?.title || ''}
          onContentLinked={() => {
            fetchCaseDetails()
            onCaseUpdate()
          }}
        />
      </DialogContent>
    </Dialog>
  )
}
