"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { apiClient } from '@/lib/api'
import { Clock, FileText, Users, TrendingUp } from 'lucide-react'

interface ActivitySummary {
  total_activities: number
  total_time_spent_minutes: number
  total_time_spent_hours: number
  by_type: Record<string, number>
  by_analyst: Record<string, number>
  report_items_count: number
}

export function CaseActivitiesSummary({ caseId }: { caseId: number }) {
  const [summary, setSummary] = useState<ActivitySummary | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadSummary()
  }, [caseId])

  const loadSummary = async () => {
    try {
      setLoading(true)
      const data: any = await apiClient.getCaseActivitiesSummary(caseId)
      setSummary(data)
    } catch (error) {
      console.error('Failed to load summary:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading || !summary) {
    return <div className="text-sm text-muted-foreground">Loading summary...</div>
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <FileText className="w-4 h-4" />
            Total Activities
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{summary.total_activities}</div>
          <p className="text-xs text-muted-foreground">
            {summary.report_items_count} in report
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Clock className="w-4 h-4" />
            Time Tracked
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{summary.total_time_spent_hours}h</div>
          <p className="text-xs text-muted-foreground">
            {summary.total_time_spent_minutes} minutes
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <TrendingUp className="w-4 h-4" />
            Most Common
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold capitalize">
            {summary.by_type && Object.keys(summary.by_type).length > 0
              ? Object.entries(summary.by_type).sort((a, b) => b[1] - a[1])[0][0]
              : 'N/A'}
          </div>
          <p className="text-xs text-muted-foreground">Activity type</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Users className="w-4 h-4" />
            Contributors
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {summary.by_analyst ? Object.keys(summary.by_analyst).length : 0}
          </div>
          <p className="text-xs text-muted-foreground">Analysts</p>
        </CardContent>
      </Card>
    </div>
  )
}

