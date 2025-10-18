'use client'

import { useEffect, useState } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'
import { toast } from '@/hooks/use-toast'
import apiClient from '@/lib/api'

interface LinkContentDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  caseId: number
  onLinked: () => void
}

interface ContentItem {
  id: number
  title?: string
  text?: string
  risk_level?: string
  status?: string
  created_at?: string
}

export default function LinkContentDialog({ open, onOpenChange, caseId, onLinked }: LinkContentDialogProps) {
  const [items, setItems] = useState<ContentItem[]>([])
  const [selected, setSelected] = useState<Record<number, boolean>>({})
  const [loading, setLoading] = useState(false)
  const [search, setSearch] = useState('')

  const fetchContent = async () => {
    try {
      setLoading(true)
      const res = await apiClient.get('/api/content')
      if ((res as any)?.status === 'success') {
        setItems((res as any).data || [])
      } else {
        toast({ title: 'Error', description: 'Failed to load content', variant: 'destructive' })
      }
    } catch (e) {
      toast({ title: 'Error', description: 'Failed to load content', variant: 'destructive' })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (open) fetchContent()
  }, [open])

  const filtered = items.filter(i => {
    if (!search.trim()) return true
    const q = search.toLowerCase()
    return (i.title || '').toLowerCase().includes(q) || (i.text || '').toLowerCase().includes(q)
  })

  const toggle = (id: number) => {
    setSelected(prev => ({ ...prev, [id]: !prev[id] }))
  }

  const linkSelected = async () => {
    const ids = Object.entries(selected).filter(([, v]) => v).map(([k]) => Number(k))
    if (ids.length === 0) {
      toast({ title: 'Select content', description: 'Choose at least one content item' })
      return
    }
    try {
      setLoading(true)
      const res = await apiClient.linkContentToCase(caseId, ids)
      if ((res as any)?.status === 'success') {
        toast({ title: 'Content linked', description: `Linked ${ids.length} item(s)` })
        setSelected({})
        onLinked()
        onOpenChange(false)
      } else {
        toast({ title: 'Failed to link content', variant: 'destructive' })
      }
    } catch (e) {
      toast({ title: 'Failed to link content', variant: 'destructive' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>Link Scraped Content</DialogTitle>
          <DialogDescription>Select one or more content items to attach to this case.</DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label>Search</Label>
            <Input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search content..." />
          </div>

          <div className="max-h-96 overflow-y-auto border rounded">
            {loading ? (
              <div className="p-6 text-center text-muted-foreground">Loading content...</div>
            ) : filtered.length === 0 ? (
              <div className="p-6 text-center text-muted-foreground">No content found</div>
            ) : (
              <div className="divide-y">
                {filtered.map(item => (
                  <label key={item.id} className="flex items-start gap-3 p-3 cursor-pointer">
                    <Checkbox checked={!!selected[item.id]} onCheckedChange={() => toggle(item.id)} />
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <div className="font-medium">{item.title || `Content #${item.id}`}</div>
                        {item.risk_level && (
                          <Badge variant="outline">{item.risk_level}</Badge>
                        )}
                        {item.status && (
                          <Badge variant="secondary">{item.status}</Badge>
                        )}
                      </div>
                      {item.text && (
                        <div className="text-sm text-muted-foreground line-clamp-2">{item.text}</div>
                      )}
                    </div>
                  </label>
                ))}
              </div>
            )}
          </div>

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => onOpenChange(false)} disabled={loading}>Cancel</Button>
            <Button onClick={linkSelected} disabled={loading}>Link Selected</Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}


