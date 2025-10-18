'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Clock, 
  CheckCircle, 
  XCircle, 
  FileText, 
  RefreshCw,
  AlertTriangle
} from 'lucide-react'
import apiClient from '@/lib/api'
import { toast } from '@/hooks/use-toast'

interface CaseRequest {
  id: number
  title: string
  description?: string
  case_type?: string
  priority?: string
  summary?: string
  objectives?: string
  methodology?: string
  tags?: string[]
  status: 'pending' | 'approved' | 'rejected' | 'cancelled'
  requested_by_id: number
  reviewed_by_id?: number
  review_notes?: string
  requested_at: string
  reviewed_at?: string
  created_at: string
  updated_at: string
  requested_by?: {
    id: number
    username: string
    email: string
  }
  reviewed_by?: {
    id: number
    username: string
    email: string
  }
}

export default function CaseRequestStatus() {
  const [requests, setRequests] = useState<CaseRequest[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchRequests = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await apiClient.getCaseRequests()
      
      if (response.status === 'success') {
        setRequests(response.data || [])
      } else {
        setError('Failed to fetch case requests')
      }
    } catch (error) {
      console.error('Error fetching case requests:', error)
      setError('Error fetching case requests')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchRequests()
  }, [])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-600" />
      case 'approved':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'rejected':
        return <XCircle className="h-4 w-4 text-red-600" />
      case 'cancelled':
        return <XCircle className="h-4 w-4 text-gray-600" />
      default:
        return <Clock className="h-4 w-4 text-gray-600" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">Pending Review</Badge>
      case 'approved':
        return <Badge variant="default" className="bg-green-100 text-green-800">Approved</Badge>
      case 'rejected':
        return <Badge variant="destructive">Rejected</Badge>
      case 'cancelled':
        return <Badge variant="outline">Cancelled</Badge>
      default:
        return <Badge variant="outline">{status}</Badge>
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Case Request Status
          </CardTitle>
          <CardDescription>
            Track your submitted case creation requests
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
            <span className="ml-2 text-muted-foreground">Loading requests...</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Case Request Status
          </CardTitle>
          <CardDescription>
            Track your submitted case creation requests
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              {error}
              <Button 
                variant="outline" 
                size="sm" 
                className="ml-2"
                onClick={fetchRequests}
              >
                <RefreshCw className="h-4 w-4 mr-1" />
                Retry
              </Button>
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    )
  }

  if (requests.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Case Request Status
          </CardTitle>
          <CardDescription>
            Track your submitted case creation requests
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium text-muted-foreground mb-2">
              No Case Requests Found
            </h3>
            <p className="text-sm text-muted-foreground">
              You haven't submitted any case creation requests yet.
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Case Request Status
          </div>
          <Button 
            variant="outline" 
            size="sm"
            onClick={fetchRequests}
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 mr-1 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </CardTitle>
        <CardDescription>
          Track your submitted case creation requests and their approval status
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {requests.map((request) => (
            <div 
              key={request.id}
              className="border rounded-lg p-4 space-y-3"
            >
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <h4 className="font-medium">{request.title}</h4>
                  {request.description && (
                    <p className="text-sm text-muted-foreground line-clamp-2">
                      {request.description}
                    </p>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  {getStatusIcon(request.status)}
                  {getStatusBadge(request.status)}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium">Request ID:</span> #{request.id}
                </div>
                <div>
                  <span className="font-medium">Type:</span> {request.case_type || 'N/A'}
                </div>
                <div>
                  <span className="font-medium">Priority:</span> {request.priority || 'N/A'}
                </div>
                <div>
                  <span className="font-medium">Submitted:</span> {formatDate(request.requested_at)}
                </div>
                {request.reviewed_at && (
                  <div>
                    <span className="font-medium">Reviewed:</span> {formatDate(request.reviewed_at)}
                  </div>
                )}
                {request.reviewed_by && (
                  <div>
                    <span className="font-medium">Reviewed by:</span> {request.reviewed_by.username}
                  </div>
                )}
              </div>

              {request.tags && request.tags.length > 0 && (
                <div>
                  <span className="text-sm font-medium">Tags:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {request.tags.map((tag, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {request.review_notes && (
                <div>
                  <span className="text-sm font-medium">Review Notes:</span>
                  <p className="text-sm text-muted-foreground mt-1 p-2 bg-muted rounded">
                    {request.review_notes}
                  </p>
                </div>
              )}

              {request.status === 'pending' && (
                <Alert>
                  <Clock className="h-4 w-4" />
                  <AlertDescription>
                    Your case request is pending admin review. You'll be notified once it's processed.
                  </AlertDescription>
                </Alert>
              )}

              {request.status === 'approved' && (
                <Alert className="border-green-200 bg-green-50">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <AlertDescription className="text-green-800">
                    Your case request has been approved! The case should now be available in your cases list.
                  </AlertDescription>
                </Alert>
              )}

              {request.status === 'rejected' && (
                <Alert variant="destructive">
                  <XCircle className="h-4 w-4" />
                  <AlertDescription>
                    Your case request was rejected. Please review the feedback and consider submitting a new request with modifications.
                  </AlertDescription>
                </Alert>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
