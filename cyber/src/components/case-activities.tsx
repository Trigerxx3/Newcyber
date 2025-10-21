"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { apiClient } from '@/lib/api'
import { 
  Plus, Edit2, Trash2, FileText, Clock, Tag, AlertCircle, 
  CheckCircle, Eye, EyeOff, MessageSquare, Search, Calendar 
} from 'lucide-react'
import { format } from 'date-fns'

interface CaseActivity {
  id: number
  case_id: number
  analyst_id: number
  activity_type: string
  title: string
  description: string
  status: string
  tags: string[]
  priority: string
  activity_date: string
  time_spent_minutes: number
  include_in_report: boolean
  is_confidential: boolean
  visibility_level: string
  edit_count: number
  analyst?: {
    id: number
    username: string
    email: string
  }
  created_at: string
  updated_at: string
}

const ACTIVITY_TYPES = [
  { value: 'note', label: 'Note', icon: MessageSquare },
  { value: 'finding', label: 'Finding', icon: Search },
  { value: 'evidence', label: 'Evidence', icon: FileText },
  { value: 'interview', label: 'Interview', icon: MessageSquare },
  { value: 'analysis', label: 'Analysis', icon: Search },
  { value: 'action', label: 'Action', icon: CheckCircle },
  { value: 'meeting', label: 'Meeting', icon: Calendar },
  { value: 'observation', label: 'Observation', icon: Eye },
  { value: 'recommendation', label: 'Recommendation', icon: AlertCircle },
  { value: 'other', label: 'Other', icon: FileText }
]

const PRIORITY_COLORS = {
  low: 'bg-green-100 text-green-800',
  medium: 'bg-yellow-100 text-yellow-800',
  high: 'bg-orange-100 text-orange-800',
  critical: 'bg-red-100 text-red-800'
}

export function CaseActivities({ caseId }: { caseId: number }) {
  const [activities, setActivities] = useState<CaseActivity[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<string>('all')
  const [showAddDialog, setShowAddDialog] = useState(false)
  const [editingActivity, setEditingActivity] = useState<CaseActivity | null>(null)

  useEffect(() => {
    loadActivities()
  }, [caseId])

  const loadActivities = async () => {
    try {
      setLoading(true)
      const response: any = await apiClient.getCaseActivities(caseId)
      setActivities(response.activities || [])
    } catch (error) {
      console.error('Failed to load activities:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredActivities = activities.filter(activity => {
    if (filter === 'all') return true
    if (filter === 'report') return activity.include_in_report
    return activity.activity_type === filter
  })

  const toggleReportInclusion = async (activityId: number) => {
    try {
      await apiClient.toggleActivityReportInclusion(caseId, activityId)
      loadActivities()
    } catch (error) {
      console.error('Failed to toggle report inclusion:', error)
    }
  }

  const deleteActivity = async (activityId: number) => {
    if (!confirm('Are you sure you want to delete this activity?')) return
    
    try {
      await apiClient.deleteCaseActivity(caseId, activityId)
      loadActivities()
    } catch (error) {
      console.error('Failed to delete activity:', error)
    }
  }

  if (loading) {
    return <div className="text-center py-8">Loading activities...</div>
  }

  return (
    <div className="space-y-4">
      {/* Header with filters */}
      <div className="flex justify-between items-center">
        <div className="flex gap-2">
          <Button
            variant={filter === 'all' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilter('all')}
          >
            All ({activities.length})
          </Button>
          <Button
            variant={filter === 'report' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilter('report')}
          >
            In Report ({activities.filter(a => a.include_in_report).length})
          </Button>
          <Select value={filter} onValueChange={setFilter}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Filter by type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              {ACTIVITY_TYPES.map(type => (
                <SelectItem key={type.value} value={type.value}>
                  {type.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Add Activity
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <ActivityForm 
              caseId={caseId} 
              onSuccess={() => {
                setShowAddDialog(false)
                loadActivities()
              }}
              onCancel={() => setShowAddDialog(false)}
            />
          </DialogContent>
        </Dialog>
      </div>

      {/* Activities List */}
      <div className="space-y-3">
        {filteredActivities.length === 0 ? (
          <Card>
            <CardContent className="py-8 text-center text-muted-foreground">
              No activities found. Add your first activity to start tracking work.
            </CardContent>
          </Card>
        ) : (
          filteredActivities.map(activity => (
            <ActivityCard
              key={activity.id}
              activity={activity}
              onToggleReport={() => toggleReportInclusion(activity.id)}
              onEdit={() => setEditingActivity(activity)}
              onDelete={() => deleteActivity(activity.id)}
            />
          ))
        )}
      </div>

      {/* Edit Dialog */}
      {editingActivity && (
        <Dialog open={!!editingActivity} onOpenChange={() => setEditingActivity(null)}>
          <DialogContent className="max-w-2xl">
            <ActivityForm 
              caseId={caseId}
              activity={editingActivity}
              onSuccess={() => {
                setEditingActivity(null)
                loadActivities()
              }}
              onCancel={() => setEditingActivity(null)}
            />
          </DialogContent>
        </Dialog>
      )}
    </div>
  )
}

function ActivityCard({ 
  activity, 
  onToggleReport, 
  onEdit, 
  onDelete 
}: { 
  activity: CaseActivity
  onToggleReport: () => void
  onEdit: () => void
  onDelete: () => void
}) {
  const activityType = ACTIVITY_TYPES.find(t => t.value === activity.activity_type)
  const Icon = activityType?.icon || FileText

  return (
    <Card className={activity.include_in_report ? 'border-blue-300' : ''}>
      <CardHeader>
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <Icon className="w-4 h-4 text-muted-foreground" />
              <CardTitle className="text-base">{activity.title}</CardTitle>
              {activity.priority && (
                <Badge className={PRIORITY_COLORS[activity.priority as keyof typeof PRIORITY_COLORS]}>
                  {activity.priority}
                </Badge>
              )}
              {activity.is_confidential && (
                <Badge variant="destructive">Confidential</Badge>
              )}
            </div>
            <CardDescription className="flex items-center gap-3 text-xs">
              <span>{activityType?.label}</span>
              <span>•</span>
              <span>{activity.analyst?.username || 'Unknown'}</span>
              <span>•</span>
              <span>{format(new Date(activity.activity_date), 'MMM dd, yyyy HH:mm')}</span>
              {activity.time_spent_minutes > 0 && (
                <>
                  <span>•</span>
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {Math.round(activity.time_spent_minutes / 60 * 10) / 10}h
                  </span>
                </>
              )}
            </CardDescription>
          </div>
          <div className="flex gap-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={onToggleReport}
              title={activity.include_in_report ? 'Remove from report' : 'Include in report'}
            >
              {activity.include_in_report ? (
                <Eye className="w-4 h-4 text-blue-600" />
              ) : (
                <EyeOff className="w-4 h-4 text-gray-400" />
              )}
            </Button>
            <Button variant="ghost" size="sm" onClick={onEdit}>
              <Edit2 className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={onDelete}>
              <Trash2 className="w-4 h-4 text-red-600" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground whitespace-pre-wrap">{activity.description}</p>
        {activity.tags && activity.tags.length > 0 && (
          <div className="flex items-center gap-2 mt-3">
            <Tag className="w-3 h-3 text-muted-foreground" />
            <div className="flex flex-wrap gap-1">
              {activity.tags.map((tag, idx) => (
                <Badge key={idx} variant="secondary" className="text-xs">
                  {tag}
                </Badge>
              ))}
            </div>
          </div>
        )}
        {activity.edit_count > 0 && (
          <p className="text-xs text-muted-foreground mt-2">
            Edited {activity.edit_count} time{activity.edit_count !== 1 ? 's' : ''}
          </p>
        )}
      </CardContent>
    </Card>
  )
}

function ActivityForm({ 
  caseId, 
  activity, 
  onSuccess, 
  onCancel 
}: { 
  caseId: number
  activity?: CaseActivity
  onSuccess: () => void
  onCancel: () => void
}) {
  const [formData, setFormData] = useState({
    title: activity?.title || '',
    description: activity?.description || '',
    activity_type: activity?.activity_type || 'note',
    priority: activity?.priority || 'medium',
    tags: activity?.tags?.join(', ') || '',
    time_spent_minutes: activity?.time_spent_minutes || 0,
    include_in_report: activity?.include_in_report !== false,
    is_confidential: activity?.is_confidential || false
  })
  const [saving, setSaving] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)

    try {
      const data = {
        ...formData,
        tags: formData.tags.split(',').map(t => t.trim()).filter(Boolean)
      }

      if (activity) {
        await apiClient.updateCaseActivity(caseId, activity.id, data)
      } else {
        await apiClient.createCaseActivity(caseId, data)
      }

      onSuccess()
    } catch (error) {
      console.error('Failed to save activity:', error)
      alert('Failed to save activity. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <DialogHeader>
        <DialogTitle>{activity ? 'Edit Activity' : 'Add New Activity'}</DialogTitle>
        <DialogDescription>
          Record your investigation work and findings
        </DialogDescription>
      </DialogHeader>

      <div className="grid gap-4 py-4">
        <div className="grid gap-2">
          <Label htmlFor="title">Title *</Label>
          <Input
            id="title"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            placeholder="Brief title of the activity"
            required
          />
        </div>

        <div className="grid gap-2">
          <Label htmlFor="description">Description *</Label>
          <Textarea
            id="description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            placeholder="Detailed description of the work done, findings, etc."
            rows={6}
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <Label htmlFor="activity_type">Activity Type</Label>
            <Select value={formData.activity_type} onValueChange={(value) => setFormData({ ...formData, activity_type: value })}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {ACTIVITY_TYPES.map(type => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="grid gap-2">
            <Label htmlFor="priority">Priority</Label>
            <Select value={formData.priority} onValueChange={(value) => setFormData({ ...formData, priority: value })}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="low">Low</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="high">High</SelectItem>
                <SelectItem value="critical">Critical</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="grid gap-2">
          <Label htmlFor="tags">Tags (comma-separated)</Label>
          <Input
            id="tags"
            value={formData.tags}
            onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
            placeholder="suspect-1, interview, evidence"
          />
        </div>

        <div className="grid gap-2">
          <Label htmlFor="time_spent">Time Spent (minutes)</Label>
          <Input
            id="time_spent"
            type="number"
            value={formData.time_spent_minutes}
            onChange={(e) => setFormData({ ...formData, time_spent_minutes: parseInt(e.target.value) || 0 })}
            placeholder="0"
          />
        </div>

        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="include_in_report"
            checked={formData.include_in_report}
            onChange={(e) => setFormData({ ...formData, include_in_report: e.target.checked })}
            className="rounded border-gray-300"
          />
          <Label htmlFor="include_in_report" className="cursor-pointer">
            Include in PDF report
          </Label>
        </div>

        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="is_confidential"
            checked={formData.is_confidential}
            onChange={(e) => setFormData({ ...formData, is_confidential: e.target.checked })}
            className="rounded border-gray-300"
          />
          <Label htmlFor="is_confidential" className="cursor-pointer">
            Mark as confidential
          </Label>
        </div>
      </div>

      <DialogFooter>
        <Button type="button" variant="outline" onClick={onCancel} disabled={saving}>
          Cancel
        </Button>
        <Button type="submit" disabled={saving}>
          {saving ? 'Saving...' : (activity ? 'Update' : 'Create')}
        </Button>
      </DialogFooter>
    </form>
  )
}

