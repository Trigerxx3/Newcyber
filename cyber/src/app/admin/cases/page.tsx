'use client'

import { useEffect, useMemo, useState } from 'react'
import { useRouter } from 'next/navigation'
import ProtectedRoute from '@/components/ProtectedRoute'
import { useToast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Filter, Search, Calendar, Eye } from 'lucide-react'

type AdminCaseRow = {
  id: number
  title: string
  case_number: string
  status: string
  priority: string
  type: string
  created_at: string
  updated_at: string
}

export default function AdminCasesOversightPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [cases, setCases] = useState<AdminCaseRow[]>([])
  const [loading, setLoading] = useState(false)
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('all')
  const [priority, setPriority] = useState('all')
  const [type, setType] = useState('all')

  useEffect(() => {
    load()
  }, [status, priority, type])

  const filtered = useMemo(() => {
    const term = search.trim().toLowerCase()
    return cases.filter(c =>
      (!term || c.title.toLowerCase().includes(term) || c.case_number.toLowerCase().includes(term))
    )
  }, [cases, search])

  async function load() {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (status !== 'all') params.append('status', status)
      if (priority !== 'all') params.append('priority', priority)
      if (type !== 'all') params.append('type', type)
      params.append('per_page', '50')
      const res = await apiClient.get<any>(`/api/cases?${params.toString()}`)
      const items: AdminCaseRow[] = res?.data || []
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

  return (
    <ProtectedRoute>
      <div className="min-h-screen">
        <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
          <div className="mb-6">
            <Card className="bg-black/40 border-white/10">
              <CardHeader>
                <CardTitle className="text-xl">Admin Cases Oversight</CardTitle>
              </CardHeader>
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
                <Select value={type} onValueChange={setType}>
                  <SelectTrigger>
                    <SelectValue placeholder="Type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All</SelectItem>
                    <SelectItem value="fraud">Fraud</SelectItem>
                    <SelectItem value="harassment">Harassment</SelectItem>
                    <SelectItem value="extremism">Extremism</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="mt-3 flex gap-2">
                <Button variant="outline" className="border-white/10" onClick={load} disabled={loading}>{loading ? 'Loading…' : 'Apply'}</Button>
                <Button variant="outline" className="border-white/10" onClick={() => { setSearch(''); setStatus('all'); setPriority('all'); setType('all'); }}>Reset</Button>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-black/40 border-white/10">
            <CardHeader>
              <CardTitle className="text-base">Cases ({filtered.length})</CardTitle>
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
                      <TableHead>Type</TableHead>
                      <TableHead>Created</TableHead>
                      <TableHead>Updated</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filtered.map(item => (
                      <TableRow key={item.id}>
                        <TableCell>
                          <div className="font-medium">{item.title}</div>
                          <div className="text-xs text-muted-foreground">#{item.case_number}</div>
                        </TableCell>
                        <TableCell className="capitalize">{item.status?.replace('_', ' ')}</TableCell>
                        <TableCell className="capitalize">{item.priority}</TableCell>
                        <TableCell className="capitalize">{item.type?.replace('_', ' ')}</TableCell>
                        <TableCell>
                          <div className="flex items-center gap-1 text-xs text-muted-foreground">
                            <Calendar className="h-3 w-3" /> {new Date(item.created_at).toLocaleString()}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-1 text-xs text-muted-foreground">
                            <Calendar className="h-3 w-3" /> {new Date(item.updated_at).toLocaleString()}
                          </div>
                        </TableCell>
                        <TableCell className="text-right">
                          <Button 
                            variant="outline" 
                            size="sm" 
                            className="border-white/10"
                            onClick={() => router.push(`/admin/cases/${item.id}`)}
                          >
                            <Eye className="h-4 w-4 mr-1" />
                            View
                          </Button>
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
    </ProtectedRoute>
  )
}


