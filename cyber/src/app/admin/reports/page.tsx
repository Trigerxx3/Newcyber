'use client'

import { useEffect, useMemo, useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import { useAuth } from '@/contexts/AuthContext'
import { useToast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { AlertTriangle, FileText, Search, Filter, Eye, Download, Calendar, FileBarChart } from 'lucide-react'

type CaseRow = {
  id: number
  title: string
  case_number: string
  status: string
  priority: string
  type: string
  created_at: string
  updated_at: string
}

export default function AdminReportsOversightPage() {
  const { systemUser } = useAuth()
  const { toast } = useToast()
  const [cases, setCases] = useState<CaseRow[]>([])
  const [loading, setLoading] = useState(false)
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('all')
  const [priority, setPriority] = useState('all')
  const [previewCaseId, setPreviewCaseId] = useState<number | null>(null)
  const [previewLoading, setPreviewLoading] = useState(false)
  const [previewData, setPreviewData] = useState<any | null>(null)
  const [downloading, setDownloading] = useState<number | null>(null)

  const isAdmin = systemUser?.role === 'Admin'

  useEffect(() => {
    load()
  }, [status, priority])

  const filtered = useMemo(() => {
    const term = search.trim().toLowerCase()
    return cases.filter(c =>
      (!term || c.title.toLowerCase().includes(term) || c.case_number.toLowerCase().includes(term))
    )
  }, [cases, search])

  async function load() {
    try {
      setLoading(true)
      const res = await apiClient.getCasesForReports({ status: status !== 'all' ? status : undefined, priority: priority !== 'all' ? priority : undefined }) as any
      const items: CaseRow[] = res?.data?.data?.cases || []
      setCases(items)
    } catch (e: any) {
      console.error('Failed to load cases:', e)
      toast({ 
        title: 'Failed to load cases', 
        description: e?.message || 'Please check backend connection',
        variant: 'destructive' 
      })
      setCases([]) // Set empty to avoid crashes
    } finally {
      setLoading(false)
    }
  }

  async function download(caseId: number) {
    try {
      setDownloading(caseId)
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000'
      const resp = await fetch(`${apiBaseUrl}/api/reports/${caseId}/generate`, {
        method: 'GET',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` },
      })
      if (!resp.ok) throw new Error('Download failed')
      const contentDisposition = resp.headers.get('content-disposition')
      const filename = contentDisposition ? contentDisposition.split('filename=')[1]?.replace(/"/g, '') : `Case_${caseId}_Report.pdf`
      const blob = await resp.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      toast({ title: 'Report downloaded' })
    } catch (e) {
      toast({ title: 'Failed to download report', variant: 'destructive' })
    } finally {
      setDownloading(null)
    }
  }

  async function downloadDetailed(caseId: number) {
    try {
      setDownloading(caseId)
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
      toast({ title: 'Detailed report with activities downloaded' })
    } catch (e: any) {
      console.error('Download error:', e)
      toast({ title: 'Failed to download detailed report', description: e.message, variant: 'destructive' })
    } finally {
      setDownloading(null)
    }
  }

  // Load preview when a case is selected
  useEffect(() => {
    async function loadPreview(caseId: number) {
      try {
        setPreviewLoading(true)
        setPreviewData(null)
        const res = await apiClient.previewCaseReport(caseId) as any
        // The reports API returns nested data; accept either res.data.data or res.data
        const data = res?.data?.data || res?.data || null
        setPreviewData(data)
      } catch (e) {
        setPreviewData(null)
        toast({ title: 'Failed to load preview', variant: 'destructive' })
      } finally {
        setPreviewLoading(false)
      }
    }

    if (previewCaseId) {
      loadPreview(previewCaseId)
    } else {
      setPreviewData(null)
    }
  }, [previewCaseId, toast])

  return (
    <ProtectedRoute>
      <div className="min-h-screen">
        <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
          <div className="mb-6">
            <Card className="bg-black/40 border-white/10">
              <CardHeader className="flex flex-row items-center justify-between">
                <div className="flex items-center gap-2">
                  <FileText className="h-6 w-6 text-white/80" />
                  <CardTitle className="text-xl">Admin Reports Oversight</CardTitle>
                </div>
              </CardHeader>
              {!isAdmin && (
                <CardContent>
                  <div className="flex items-center gap-2 text-red-400">
                    <AlertTriangle className="h-4 w-4" />
                    Admin role required. Limited actions available.
                  </div>
                </CardContent>
              )}
            </Card>
          </div>

          <Card className="bg-black/40 border-white/10 mb-6">
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Filter className="h-4 w-4" /> Filters
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input className="pl-9" placeholder="Search title or case #" value={search} onChange={(e) => setSearch(e.target.value)} />
                </div>
                <Select value={status} onValueChange={setStatus}>
                  <SelectTrigger>
                    <SelectValue placeholder="Status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All</SelectItem>
                    <SelectItem value="open">Open</SelectItem>
                    <SelectItem value="in_progress">In Progress</SelectItem>
                    <SelectItem value="resolved">Resolved</SelectItem>
                    <SelectItem value="closed">Closed</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={priority} onValueChange={setPriority}>
                  <SelectTrigger>
                    <SelectValue placeholder="Priority" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All</SelectItem>
                    <SelectItem value="critical">Critical</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="low">Low</SelectItem>
                  </SelectContent>
                </Select>
                <div className="flex gap-2">
                  <Button variant="outline" className="border-white/10" onClick={load} disabled={loading}>{loading ? 'Loading…' : 'Apply'}</Button>
                  <Button variant="outline" className="border-white/10" onClick={() => { setSearch(''); setStatus('all'); setPriority('all'); }}>Reset</Button>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-black/40 border-white/10">
            <CardHeader>
              <CardTitle className="text-base">Cases Eligible For Reports ({filtered.length})</CardTitle>
            </CardHeader>
            <CardContent>
              {filtered.length === 0 ? (
                <div className="text-muted-foreground text-sm py-10 text-center">No cases match current filters.</div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Case</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Priority</TableHead>
                      <TableHead>Last Updated</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filtered.map(item => (
                      <TableRow key={item.id}>
                        <TableCell>
                          <div className="font-medium">{item.title}</div>
                          <div className="text-xs text-muted-foreground">#{item.case_number} • {item.type?.replace(/_/g, ' ')}</div>
                        </TableCell>
                        <TableCell className="capitalize">{item.status?.replace('_', ' ')}</TableCell>
                        <TableCell className="capitalize">{item.priority}</TableCell>
                        <TableCell>
                          <div className="flex items-center gap-1 text-xs text-muted-foreground">
                            <Calendar className="h-3 w-3" /> {new Date(item.updated_at).toLocaleString()}
                          </div>
                        </TableCell>
                        <TableCell className="text-right">
                          <div className="flex justify-end gap-2">
                            <Button variant="outline" size="sm" className="border-white/10" onClick={() => setPreviewCaseId(item.id)}>
                              <Eye className="h-4 w-4" />
                            </Button>
                            <Button 
                              variant="outline" 
                              size="sm" 
                              onClick={() => download(item.id)} 
                              disabled={downloading === item.id}
                              title="Download basic report"
                            >
                              {downloading === item.id ? '...' : <Download className="h-4 w-4" />}
                            </Button>
                            <Button 
                              size="sm" 
                              onClick={() => downloadDetailed(item.id)} 
                              disabled={downloading === item.id}
                              title="Download detailed report with activities"
                            >
                              {downloading === item.id ? '...' : <FileBarChart className="h-4 w-4" />}
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      <Dialog open={!!previewCaseId} onOpenChange={(open) => !open && setPreviewCaseId(null)}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Eye className="h-4 w-4" /> Report Preview (summary)
            </DialogTitle>
          </DialogHeader>
          {previewLoading && (
            <div className="text-sm text-muted-foreground">Loading preview…</div>
          )}
          {!previewLoading && !previewData && (
            <div className="text-sm text-muted-foreground">No preview available.</div>
          )}
          {!previewLoading && previewData && (
            <div className="space-y-4">
              <div>
                <div className="text-xs text-muted-foreground">Case</div>
                <div className="text-foreground font-medium">
                  {previewData.case?.title} <span className="text-xs text-muted-foreground">#{previewData.case?.case_number}</span>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="text-xs text-muted-foreground">Status</div>
                  <div className="capitalize">{previewData.case?.status?.replace('_', ' ')}</div>
                </div>
                <div>
                  <div className="text-xs text-muted-foreground">Priority</div>
                  <div className="capitalize">{previewData.case?.priority}</div>
                </div>
              </div>
              {previewData.statistics && (
                <div className="text-sm">
                  <div className="text-xs text-muted-foreground">Statistics</div>
                  <div className="grid grid-cols-3 gap-3">
                    <div>Flagged Posts: {previewData.statistics.flagged_posts}</div>
                    <div>Flagged Users: {previewData.statistics.flagged_users}</div>
                    <div>OSINT Results: {previewData.statistics.osint_results}</div>
                  </div>
                </div>
              )}
              {!!previewData.flagged_content_summary?.length && (
                <div className="text-sm">
                  <div className="text-xs text-muted-foreground mb-1">Flagged Content (top)</div>
                  <ul className="space-y-1">
                    {previewData.flagged_content_summary.slice(0, 5).map((c: any) => (
                      <li key={c.id} className="border border-white/10 rounded p-2">
                        <div className="font-medium">{c.author} • {c.platform}</div>
                        <div className="text-xs text-muted-foreground">Risk: {c.risk_level} • Score: {c.suspicion_score}</div>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </ProtectedRoute>
  )
}


