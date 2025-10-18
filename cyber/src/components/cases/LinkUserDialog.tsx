'use client'

import { useState, useEffect } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import apiClient from '@/lib/api'
import { toast } from '@/hooks/use-toast'

interface User {
  id: number
  username: string
  full_name?: string
  is_flagged: boolean
  source: {
    name: string
  }
}

interface LinkUserDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  caseId: number
  onUserLinked: () => void
}

export default function LinkUserDialog({ open, onOpenChange, caseId, onUserLinked }: LinkUserDialogProps) {
  const [users, setUsers] = useState<User[]>([])
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null)
  const [role, setRole] = useState('viewer')
  const [reason, setReason] = useState('')
  const [loading, setLoading] = useState(false)

  const fetchUsers = async () => {
    try {
      const response = await apiClient.get('/api/users/')
      if (response.data.status === 'success') {
        setUsers(response.data.data)
      }
    } catch (error) {
      toast({ title: "Error", description: "Failed to fetch users", variant: "destructive" })
    }
  }

  useEffect(() => {
    if (open) {
      fetchUsers()
    }
  }, [open])

  const handleLinkUser = async () => {
    if (!selectedUserId) return

    try {
      setLoading(true)
      await apiClient.post(`/api/cases/${caseId}/users`, {
        user_id: selectedUserId,
        role,
        assignment_reason: reason
      })
      
      toast({ title: "Success", description: "User linked to case successfully" })
      onUserLinked()
      onOpenChange(false)
      
      // Reset form
      setSelectedUserId(null)
      setRole('viewer')
      setReason('')
    } catch (error) {
      toast({ title: "Error", description: "Failed to link user", variant: "destructive" })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Link User to Case</DialogTitle>
          <DialogDescription>Select a user and role to attach to this case.</DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div>
            <Label>Select User</Label>
            <Select value={selectedUserId?.toString()} onValueChange={(value) => setSelectedUserId(Number(value))}>
              <SelectTrigger>
                <SelectValue placeholder="Choose a user..." />
              </SelectTrigger>
              <SelectContent>
                {users.map((user) => (
                  <SelectItem key={user.id} value={user.id.toString()}>
                    @{user.username} {user.full_name && `(${user.full_name})`} 
                    {user.is_flagged && ' ⚠️'}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label>Role</Label>
            <Select value={role} onValueChange={setRole}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="viewer">Viewer</SelectItem>
                <SelectItem value="investigator">Investigator</SelectItem>
                <SelectItem value="analyst">Analyst</SelectItem>
                <SelectItem value="reviewer">Reviewer</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label>Assignment Reason</Label>
            <Textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Why is this user being linked to the case?"
              rows={3}
            />
          </div>

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button onClick={handleLinkUser} disabled={loading || !selectedUserId}>
              {loading ? 'Linking...' : 'Link User'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
