'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { 
  Activity, 
  Users, 
  TrendingUp, 
  Edit, 
  Trash2, 
  Plus, 
  UserCheck, 
  Timer, 
  Target,
  Calendar,
  User,
  Clock,
  BarChart3,
  FileText,
  Shield,
  RefreshCw,
  Loader2,
  Eye,
  Download
} from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

interface AnalystActivity {
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
  created_at: string
  updated_at: string
  analyst: {
    id: number
    username: string
    email: string
  }
  case?: {
    id: number
    title: string
    case_number: string
  }
}

interface AnalystActivitySummary {
  total_activities: number
  total_time_spent_minutes: number
  total_time_spent_hours: number
  by_type: Record<string, number>
  by_analyst: Record<string, number>
  report_items_count: number
  recent_activities: AnalystActivity[]
}

interface Analyst {
  id: number
  username: string
  email: string
  role: string
  total_activities: number
  total_time_spent: number
  active_cases: number
}

interface AnalystActivityDashboardProps {
  selectedAnalystId?: number
  onAnalystSelect?: (analystId: number | null) => void
}

export default function AnalystActivityDashboard({ 
  selectedAnalystId, 
  onAnalystSelect 
}: AnalystActivityDashboardProps) {
  const { toast } = useToast()
  const [analysts, setAnalysts] = useState<Analyst[]>([])
  const [activities, setActivities] = useState<AnalystActivity[]>([])
  const [summary, setSummary] = useState<AnalystActivitySummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [activityLoading, setActivityLoading] = useState(false)
  const [selectedAnalyst, setSelectedAnalyst] = useState<number | null>(selectedAnalystId || null)
  const [activityFilter, setActivityFilter] = useState('all')
  const [activityTypeFilter, setActivityTypeFilter] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [showActivityDialog, setShowActivityDialog] = useState(false)
  const [editingActivity, setEditingActivity] = useState<AnalystActivity | null>(null)
  const [previewActivity, setPreviewActivity] = useState<AnalystActivity | null>(null)
  const [showPreviewDialog, setShowPreviewDialog] = useState(false)

  useEffect(() => {
    loadAnalysts()
  }, [])

  useEffect(() => {
    if (selectedAnalyst) {
      loadAnalystActivities(selectedAnalyst)
    }
  }, [selectedAnalyst])

  const loadAnalysts = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000'}/api/users`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      })
      
      if (response.ok) {
        const data = await response.json()
        if (data.data?.users) {
          const analystData = data.data.users.map((user: any) => ({
            id: user.id,
            username: user.username,
            email: user.email,
            role: user.role,
            total_activities: 0,
            total_time_spent: 0,
            active_cases: 0
          }))
          setAnalysts(analystData)
        }
      }
    } catch (error: any) {
      console.error('Error loading analysts:', error)
      toast({
        title: "Error",
        description: "Failed to load analysts",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  const loadAnalystActivities = async (analystId: number) => {
    try {
      setActivityLoading(true)
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000'}/api/analysts/${analystId}/activities`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      })
      
      if (response.ok) {
        const data = await response.json()
        setActivities(data.activities || [])
        setSummary(data.summary || null)
      }
    } catch (error: any) {
      console.error('Error loading analyst activities:', error)
      toast({
        title: "Error",
        description: "Failed to load analyst activities",
        variant: "destructive"
      })
    } finally {
      setActivityLoading(false)
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'critical': return 'bg-red-500/20 text-red-400 border-red-400/30'
      case 'high': return 'bg-orange-500/20 text-orange-400 border-orange-400/30'
      case 'medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-400/30'
      case 'low': return 'bg-green-500/20 text-green-400 border-green-400/30'
      default: return 'bg-gray-500/20 text-gray-400 border-gray-400/30'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active': return 'bg-blue-500/20 text-blue-400 border-blue-400/30'
      case 'completed': return 'bg-green-500/20 text-green-400 border-green-400/30'
      case 'draft': return 'bg-yellow-500/20 text-yellow-400 border-yellow-400/30'
      case 'archived': return 'bg-gray-500/20 text-gray-400 border-gray-400/30'
      default: return 'bg-gray-500/20 text-gray-400 border-gray-400/30'
    }
  }

  const filteredActivities = activities.filter(activity => {
    if (activityTypeFilter !== 'all' && activity.activity_type !== activityTypeFilter) return false
    if (activityFilter !== 'all' && activity.status !== activityFilter) return false
    if (searchTerm && !activity.title.toLowerCase().includes(searchTerm.toLowerCase()) && 
        !activity.description.toLowerCase().includes(searchTerm.toLowerCase())) return false
    return true
  })

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="flex flex-col items-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-muted-foreground font-medium">Loading analyst dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="h-6 w-6 text-primary" />
          <h2 className="text-2xl font-bold bg-gradient-to-r from-primary to-cyan-400 bg-clip-text text-transparent">
            Analyst Activity Dashboard
          </h2>
        </div>
        <Button
          variant="outline"
          onClick={loadAnalysts}
          className="border-white/10 hover:bg-white/5"
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Analyst Selection */}
      <Card className="glassmorphism">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5 text-primary" />
            Select Analyst
          </CardTitle>
          <CardDescription>
            Choose an analyst to view their activity history and performance metrics
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {analysts.map((analyst) => (
              <div
                key={analyst.id}
                className={`p-4 border rounded-lg cursor-pointer transition-all hover:border-primary/50 ${
                  selectedAnalyst === analyst.id 
                    ? 'border-primary bg-primary/10' 
                    : 'border-white/10 hover:bg-white/5'
                }`}
                onClick={() => {
                  setSelectedAnalyst(analyst.id)
                  onAnalystSelect?.(analyst.id)
                }}
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
                    <User className="h-5 w-5 text-primary" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-foreground">{analyst.username}</h3>
                    <p className="text-sm text-muted-foreground">{analyst.email}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant="outline" className="text-xs">
                        {analyst.role}
                      </Badge>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Selected Analyst Activities */}
      {selectedAnalyst && (
        <div className="space-y-6">
          {/* Summary Stats */}
          {summary && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card className="glassmorphism">
                <CardContent className="p-6">
                  <div className="flex items-center gap-2">
                    <Activity className="h-5 w-5 text-primary" />
                    <div>
                      <div className="text-2xl font-bold text-primary">{summary.total_activities}</div>
                      <div className="text-sm text-muted-foreground">Total Activities</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="glassmorphism">
                <CardContent className="p-6">
                  <div className="flex items-center gap-2">
                    <Timer className="h-5 w-5 text-orange-400" />
                    <div>
                      <div className="text-2xl font-bold text-orange-400">{summary.total_time_spent_hours}h</div>
                      <div className="text-sm text-muted-foreground">Time Tracked</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="glassmorphism">
                <CardContent className="p-6">
                  <div className="flex items-center gap-2">
                    <FileText className="h-5 w-5 text-green-400" />
                    <div>
                      <div className="text-2xl font-bold text-green-400">{summary.report_items_count}</div>
                      <div className="text-sm text-muted-foreground">Report Items</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="glassmorphism">
                <CardContent className="p-6">
                  <div className="flex items-center gap-2">
                    <BarChart3 className="h-5 w-5 text-blue-400" />
                    <div>
                      <div className="text-2xl font-bold text-blue-400">{Object.keys(summary.by_type).length}</div>
                      <div className="text-sm text-muted-foreground">Activity Types</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Filters and Search */}
          <Card className="glassmorphism">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5 text-primary" />
                Activity Filters
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="relative">
                  <Input
                    placeholder="Search activities..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                  <Target className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                </div>
                
                <Select value={activityTypeFilter} onValueChange={setActivityTypeFilter}>
                  <SelectTrigger>
                    <SelectValue placeholder="Filter by type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Types</SelectItem>
                        <SelectItem value="note">Notes</SelectItem>
                        <SelectItem value="finding">Findings</SelectItem>
                        <SelectItem value="evidence">Evidence</SelectItem>
                        <SelectItem value="interview">Interviews</SelectItem>
                        <SelectItem value="analysis">Analysis</SelectItem>
                        <SelectItem value="action">Actions</SelectItem>
                        <SelectItem value="meeting">Meetings</SelectItem>
                        <SelectItem value="communication">Communication</SelectItem>
                        <SelectItem value="task">Tasks</SelectItem>
                        <SelectItem value="update">Updates</SelectItem>
                        <SelectItem value="milestone">Milestones</SelectItem>
                        <SelectItem value="observation">Observations</SelectItem>
                        <SelectItem value="recommendation">Recommendations</SelectItem>
                        <SelectItem value="decision">Decisions</SelectItem>
                        <SelectItem value="investigation">User Investigation</SelectItem>
                        <SelectItem value="content_analysis">Content Analysis</SelectItem>
                        <SelectItem value="osint_search">OSINT Search</SelectItem>
                        <SelectItem value="batch_analysis">Batch Analysis</SelectItem>
                        <SelectItem value="platform_scraping">Platform Scraping</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>

                <Select value={activityFilter} onValueChange={setActivityFilter}>
                  <SelectTrigger>
                    <SelectValue placeholder="Filter by status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Status</SelectItem>
                    <SelectItem value="active">Active</SelectItem>
                    <SelectItem value="completed">Completed</SelectItem>
                    <SelectItem value="draft">Draft</SelectItem>
                    <SelectItem value="archived">Archived</SelectItem>
                  </SelectContent>
                </Select>

                <Button 
                  onClick={() => {
                    setSearchTerm('')
                    setActivityTypeFilter('all')
                    setActivityFilter('all')
                  }}
                  variant="outline"
                  className="border-white/10 hover:bg-white/5"
                >
                  Clear Filters
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Activities List */}
          <Card className="glassmorphism">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Activity className="h-5 w-5 text-primary" />
                  <CardTitle>Analyst Activities</CardTitle>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowActivityDialog(true)}
                  className="border-white/10 hover:bg-white/5"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add Activity
                </Button>
              </div>
              <CardDescription>
                {analysts.find(a => a.id === selectedAnalyst)?.username}'s activity history
              </CardDescription>
            </CardHeader>
            <CardContent>
              {activityLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-8 w-8 animate-spin text-primary" />
                  <span className="ml-2 text-muted-foreground">Loading activities...</span>
                </div>
              ) : filteredActivities.length > 0 ? (
                <div className="space-y-4">
                  {filteredActivities.map((activity) => (
                    <div key={activity.id} className="p-4 border border-white/10 rounded-lg hover:border-white/20 transition-colors">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <Badge variant="outline" className="text-xs">
                              {activity.activity_type}
                            </Badge>
                            <Badge className={getPriorityColor(activity.priority)}>
                              {activity.priority}
                            </Badge>
                            <Badge className={getStatusColor(activity.status)}>
                              {activity.status}
                            </Badge>
                            {activity.include_in_report && (
                              <Badge variant="secondary" className="text-xs">
                                <FileText className="h-3 w-3 mr-1" />
                                In Report
                              </Badge>
                            )}
                            {activity.is_confidential && (
                              <Badge variant="destructive" className="text-xs">
                                <Shield className="h-3 w-3 mr-1" />
                                Confidential
                              </Badge>
                            )}
                          </div>
                          <h4 className="font-semibold text-foreground mb-1">{activity.title}</h4>
                          <p className="text-sm text-muted-foreground mb-2">{activity.description}</p>
                          <div className="flex items-center gap-4 text-xs text-muted-foreground">
                            <div className="flex items-center gap-1">
                              <Calendar className="h-3 w-3" />
                              {new Date(activity.activity_date).toLocaleDateString()}
                            </div>
                            <div className="flex items-center gap-1">
                              <Timer className="h-3 w-3" />
                              {activity.time_spent_minutes} min
                            </div>
                            {activity.case && (
                              <div className="flex items-center gap-1">
                                <FileText className="h-3 w-3" />
                                Case #{activity.case.case_number}
                              </div>
                            )}
                            {activity.tags && activity.tags.length > 0 && (
                              <div className="flex items-center gap-1">
                                <Target className="h-3 w-3" />
                                {activity.tags.join(', ')}
                              </div>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center gap-2 ml-4">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setEditingActivity(activity)
                              setShowActivityDialog(true)
                            }}
                            className="border-white/10 hover:bg-white/5"
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setPreviewActivity(activity)
                              setShowPreviewDialog(true)
                            }}
                            className="border-white/10 hover:bg-white/5"
                            title="Preview activity"
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              // Toggle report inclusion
                              const updatedActivities = activities.map(a => 
                                a.id === activity.id ? { ...a, include_in_report: !a.include_in_report } : a
                              )
                              setActivities(updatedActivities)
                            }}
                            className={`border-white/10 hover:bg-white/5 ${activity.include_in_report ? 'bg-green-500/20 text-green-400' : ''}`}
                            title={activity.include_in_report ? 'Remove from report' : 'Include in report'}
                          >
                            <FileText className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Activity className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground font-medium">No activities found</p>
                  <p className="text-sm text-muted-foreground/70 mt-1">
                    {searchTerm || activityTypeFilter !== 'all' || activityFilter !== 'all'
                      ? 'Try adjusting your filters'
                      : 'This analyst has no recorded activities yet'
                    }
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Activity Dialog */}
      <Dialog open={showActivityDialog} onOpenChange={setShowActivityDialog}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center space-x-2">
              <Activity className="h-5 w-5 text-primary" />
              <span>{editingActivity ? 'Edit Activity' : 'Add New Activity'}</span>
            </DialogTitle>
            <DialogDescription>
              {editingActivity ? 'Update the activity details' : 'Track analyst work and investigation activities'}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-foreground mb-2 block">Activity Type</label>
                <Select defaultValue={editingActivity?.activity_type || 'note'}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select activity type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="note">Note</SelectItem>
                    <SelectItem value="finding">Finding</SelectItem>
                    <SelectItem value="evidence">Evidence</SelectItem>
                    <SelectItem value="interview">Interview</SelectItem>
                    <SelectItem value="analysis">Analysis</SelectItem>
                    <SelectItem value="action">Action</SelectItem>
                    <SelectItem value="meeting">Meeting</SelectItem>
                    <SelectItem value="communication">Communication</SelectItem>
                    <SelectItem value="task">Task</SelectItem>
                    <SelectItem value="update">Update</SelectItem>
                    <SelectItem value="milestone">Milestone</SelectItem>
                    <SelectItem value="observation">Observation</SelectItem>
                    <SelectItem value="recommendation">Recommendation</SelectItem>
                    <SelectItem value="decision">Decision</SelectItem>
                    <SelectItem value="investigation">User Investigation</SelectItem>
                    <SelectItem value="content_analysis">Content Analysis</SelectItem>
                    <SelectItem value="osint_search">OSINT Search</SelectItem>
                    <SelectItem value="batch_analysis">Batch Analysis</SelectItem>
                    <SelectItem value="platform_scraping">Platform Scraping</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <label className="text-sm font-medium text-foreground mb-2 block">Priority</label>
                <Select defaultValue={editingActivity?.priority || 'medium'}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select priority" />
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

            <div>
              <label className="text-sm font-medium text-foreground mb-2 block">Title</label>
              <Input 
                placeholder="Activity title" 
                defaultValue={editingActivity?.title || ''}
              />
            </div>

            <div>
              <label className="text-sm font-medium text-foreground mb-2 block">Description</label>
              <textarea 
                className="w-full min-h-[100px] p-3 border border-white/10 rounded-lg bg-transparent text-foreground placeholder:text-muted-foreground focus:border-primary/50 focus:outline-none"
                placeholder="Detailed description of the activity..."
                defaultValue={editingActivity?.description || ''}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-foreground mb-2 block">Time Spent (minutes)</label>
                <Input 
                  type="number" 
                  placeholder="0" 
                  defaultValue={editingActivity?.time_spent_minutes || 0}
                />
              </div>
              
              <div>
                <label className="text-sm font-medium text-foreground mb-2 block">Activity Date</label>
                <Input 
                  type="datetime-local" 
                  defaultValue={editingActivity?.activity_date ? new Date(editingActivity.activity_date).toISOString().slice(0, 16) : new Date().toISOString().slice(0, 16)}
                />
              </div>
            </div>

            <div>
              <label className="text-sm font-medium text-foreground mb-2 block">Tags (comma-separated)</label>
              <Input 
                placeholder="investigation, suspect-a, evidence" 
                defaultValue={editingActivity?.tags?.join(', ') || ''}
              />
            </div>

            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <input 
                  type="checkbox" 
                  id="include_in_report" 
                  defaultChecked={editingActivity?.include_in_report ?? true}
                  className="rounded border-white/10"
                />
                <label htmlFor="include_in_report" className="text-sm text-foreground">
                  Include in PDF report
                </label>
              </div>
              
              <div className="flex items-center space-x-2">
                <input 
                  type="checkbox" 
                  id="is_confidential" 
                  defaultChecked={editingActivity?.is_confidential ?? false}
                  className="rounded border-white/10"
                />
                <label htmlFor="is_confidential" className="text-sm text-foreground">
                  Mark as confidential
                </label>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setShowActivityDialog(false)
                setEditingActivity(null)
              }}
            >
              Cancel
            </Button>
            <Button
              onClick={() => {
                // Handle save activity
                setShowActivityDialog(false)
                setEditingActivity(null)
                if (selectedAnalyst) {
                  loadAnalystActivities(selectedAnalyst)
                }
              }}
              className="bg-primary hover:bg-primary/90"
            >
              {editingActivity ? 'Update Activity' : 'Create Activity'}
            </Button>
          </DialogFooter>
        </DialogContent>
        </Dialog>

        {/* Activity Preview Dialog */}
        <Dialog open={showPreviewDialog} onOpenChange={setShowPreviewDialog}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle className="flex items-center space-x-2">
                <Eye className="h-5 w-5 text-primary" />
                <span>Activity Preview</span>
              </DialogTitle>
              <DialogDescription>
                Preview of the selected activity details
              </DialogDescription>
            </DialogHeader>
            
            {previewActivity && (
              <div className="space-y-6">
                {/* Activity Header */}
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-foreground">{previewActivity.title}</h3>
                    <p className="text-sm text-muted-foreground mt-1">{previewActivity.description}</p>
                  </div>
                  <div className="flex space-x-2">
                    <Badge variant={previewActivity.priority === 'high' ? 'destructive' : previewActivity.priority === 'medium' ? 'default' : 'secondary'}>
                      {previewActivity.priority}
                    </Badge>
                    <Badge variant="outline">
                      {previewActivity.activity_type}
                    </Badge>
                    {previewActivity.include_in_report && (
                      <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
                        In Report
                      </Badge>
                    )}
                  </div>
                </div>

                {/* Activity Details */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-3">
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Analyst</label>
                      <p className="text-sm text-foreground">{previewActivity.analyst_name}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Status</label>
                      <p className="text-sm text-foreground capitalize">{previewActivity.status}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Activity Date</label>
                      <p className="text-sm text-foreground">
                        {new Date(previewActivity.activity_date).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Time Spent</label>
                      <p className="text-sm text-foreground">{previewActivity.time_spent_minutes} minutes</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Created</label>
                      <p className="text-sm text-foreground">
                        {new Date(previewActivity.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Confidential</label>
                      <p className="text-sm text-foreground">
                        {previewActivity.is_confidential ? 'Yes' : 'No'}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Tags */}
                {previewActivity.tags && previewActivity.tags.length > 0 && (
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Tags</label>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {previewActivity.tags.map((tag, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {/* Activity Metadata */}
                {previewActivity.metadata && Object.keys(previewActivity.metadata).length > 0 && (
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Additional Information</label>
                    <div className="mt-2 p-3 bg-muted/50 rounded-lg">
                      <pre className="text-xs text-foreground whitespace-pre-wrap">
                        {JSON.stringify(previewActivity.metadata, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            )}

            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setShowPreviewDialog(false)}
              >
                Close
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    )
  }
