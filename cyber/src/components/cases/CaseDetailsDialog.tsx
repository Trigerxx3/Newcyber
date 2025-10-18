'use client'

import { useEffect, useState } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import apiClient from '@/lib/api'
import { toast } from '@/hooks/use-toast'
import { Users, FileText, UserPlus, Search, Trash2, AlertTriangle, Link as LinkIcon, Unlink } from 'lucide-react'
import LinkUserDialog from './LinkUserDialog'
import LinkContentDialog from './LinkContentDialog'

interface CaseDetails {
  id: number
  title: string
  description?: string
  case_number: string
  status: string
  priority: string
  linked_users: Array<{
    id: number
    user_id: number
    role: string
    user: {
      id: number
      username: string
      full_name?: string
      is_flagged: boolean
    }
  }>
  linked_content?: Array<{
    id: number
    title?: string
    text?: string
    risk_level?: string
    status?: string
    link_id?: number
  }>
  statistics: {
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
  const [closingNotes, setClosingNotes] = useState('')
  const [showLinkUserDialog, setShowLinkUserDialog] = useState(false)
  const [showLinkContentDialog, setShowLinkContentDialog] = useState(false)

  const fetchCaseDetails = async () => {
    try {
      setLoading(true)
      console.log('🔍 Fetching case details for ID:', caseId)
      const response = await apiClient.get(`/api/cases/${caseId}`)
      console.log('📡 Case details response:', response)
      
      if (response.status === 'success') {
        setCaseDetails(response.data)
        console.log('✅ Case details loaded successfully')
      } else {
        console.error('❌ Failed to fetch case details:', response)
        toast({
          title: "Error",
          description: response.message || "Failed to fetch case details",
          variant: "destructive"
        })
        if ((response as any)?.statusCode === 404 || (response as any)?.error === 'Not found') {
          onOpenChange(false)
        }
      }
    } catch (error) {
      console.error('❌ Error fetching case details:', error)
      const message = error instanceof Error ? error.message : 'Failed to fetch case details'
      toast({ title: 'Error', description: message, variant: 'destructive' })
      if (message.includes('HTTP 404')) {
        onOpenChange(false)
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    console.log('🔍 CaseDetailsDialog useEffect triggered:', { open, caseId })
    if (open && caseId) {
      fetchCaseDetails()
    }
  }, [open, caseId])

  const handleCloseCase = async () => {
    try {
      await apiClient.put(`/api/cases/${caseId}/close`, { notes: closingNotes })
      toast({ title: "Success", description: "Case closed successfully" })
      fetchCaseDetails()
      onCaseUpdate()
    } catch (error) {
      toast({ title: "Error", description: "Failed to close case", variant: "destructive" })
    }
  }

  const handleUnlinkUser = async (userId: number) => {
    try {
      await apiClient.delete(`/api/cases/${caseId}/users/${userId}`)
      toast({ title: "Success", description: "User unlinked from case" })
      fetchCaseDetails()
    } catch (error) {
      toast({ title: "Error", description: "Failed to unlink user", variant: "destructive" })
    }
  }

  const runOSINT = async (username: string) => {
    try {
      await apiClient.post(`/api/osint/username/${username}`)
      toast({ title: "Success", description: "OSINT investigation started" })
    } catch (error) {
      toast({ title: "Error", description: "Failed to start OSINT investigation", variant: "destructive" })
    }
  }

  if (loading) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-4xl">
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

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            {caseDetails.title}
            <Badge variant={caseDetails.status === 'closed' ? 'destructive' : 'default'}>
              {caseDetails.status.toUpperCase()}
            </Badge>
            <Badge variant="outline">{caseDetails.priority.toUpperCase()}</Badge>
          </DialogTitle>
          <DialogDescription>
            View case details, linked users, and linked content.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Stats */}
          <div className="grid grid-cols-3 gap-4">
            <Card>
              <CardContent className="p-4 text-center">
                <Users className="w-6 h-6 mx-auto mb-2" />
                <div className="text-2xl font-bold">{caseDetails.statistics.user_count}</div>
                <div className="text-sm text-muted-foreground">Users</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <FileText className="w-6 h-6 mx-auto mb-2" />
                <div className="text-2xl font-bold">{caseDetails.statistics.days_open}</div>
                <div className="text-sm text-muted-foreground">Days Open</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <div className="text-sm text-muted-foreground">Case #</div>
                <div className="text-lg font-bold">{caseDetails.case_number}</div>
              </CardContent>
            </Card>
          </div>

          {/* Description */}
          {caseDetails.description && (
            <Card>
              <CardHeader>
                <CardTitle>Description</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">{caseDetails.description}</p>
              </CardContent>
            </Card>
          )}

          {/* Linked Users */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Linked Users</span>
                <Button size="sm" onClick={() => setShowLinkUserDialog(true)}>
                  <UserPlus className="w-4 h-4 mr-2" />
                  Link User
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {caseDetails.linked_users.length === 0 ? (
                <p className="text-muted-foreground text-center py-8">No users linked to this case</p>
              ) : (
                <div className="space-y-3">
                  {caseDetails.linked_users.map((userLink) => (
                    <div key={userLink.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-3">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-medium">@{userLink.user?.username || 'Unknown User'}</span>
                            {userLink.user?.is_flagged && (
                              <Badge variant="destructive" className="text-xs">
                                <AlertTriangle className="w-3 h-3 mr-1" />
                                FLAGGED
                              </Badge>
                            )}
                            <Badge variant="outline">{userLink.role}</Badge>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            {userLink.user?.full_name || 'No name provided'}
                          </p>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => runOSINT(userLink.user?.username || 'unknown')}
                        >
                          <Search className="w-4 h-4 mr-2" />
                          OSINT
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleUnlinkUser(userLink.user_id)}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Linked Content */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Linked Content</span>
                <Button size="sm" onClick={() => setShowLinkContentDialog(true)}>
                  <LinkIcon className="w-4 h-4 mr-2" />
                  Link Content
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {!caseDetails.linked_content || caseDetails.linked_content.length === 0 ? (
                <p className="text-muted-foreground text-center py-8">No content linked to this case</p>
              ) : (
                <div className="space-y-3">
                  {caseDetails.linked_content.map((c) => (
                    <div key={c.id} className="flex items-start justify-between p-3 border rounded-lg">
                      <div className="pr-3">
                        <div className="font-medium">{c.title || `Content #${c.id}`}</div>
                        {c.text && (
                          <div className="text-sm text-muted-foreground line-clamp-2">{c.text}</div>
                        )}
                        <div className="text-xs text-muted-foreground mt-1">Risk: {c.risk_level || 'N/A'} • Status: {c.status || 'N/A'}</div>
                      </div>
                      <div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={async () => {
                            try {
                              await apiClient.unlinkContentFromCase(caseId, c.id)
                              toast({ title: 'Content unlinked from case' })
                              await fetchCaseDetails()
                              onCaseUpdate()
                            } catch (error) {
                              toast({ title: 'Failed to unlink content', variant: 'destructive' })
                            }
                          }}
                        >
                          <Unlink className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Close Case */}
          {caseDetails.status !== 'closed' && (
            <Card>
              <CardHeader>
                <CardTitle>Close Case</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Textarea
                  placeholder="Enter closing notes..."
                  value={closingNotes}
                  onChange={(e) => setClosingNotes(e.target.value)}
                  rows={3}
                />
                <Button onClick={handleCloseCase} variant="destructive">
                  Close Case
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </DialogContent>
      
      <LinkUserDialog
        open={showLinkUserDialog}
        onOpenChange={setShowLinkUserDialog}
        caseId={caseId}
        onUserLinked={fetchCaseDetails}
      />
      <LinkContentDialog
        open={showLinkContentDialog}
        onOpenChange={setShowLinkContentDialog}
        caseId={caseId}
        onLinked={async () => { await fetchCaseDetails(); onCaseUpdate() }}
      />
    </Dialog>
  )
}
