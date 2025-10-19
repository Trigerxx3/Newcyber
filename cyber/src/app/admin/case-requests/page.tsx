'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { 
  FileText, 
  Search, 
  CheckCircle, 
  XCircle, 
  Clock,
  Eye,
  RefreshCw,
  AlertTriangle,
  Filter
} from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import apiClient from '@/lib/api'
import { useAuth } from '@/contexts/AuthContext'

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

export default function CaseRequestManagement() {
  const { toast } = useToast()
  const { systemUser } = useAuth()
  const [requests, setRequests] = useState<CaseRequest[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  
  // Dialog states
  const [showDetailsDialog, setShowDetailsDialog] = useState(false)
  const [showApprovalDialog, setShowApprovalDialog] = useState(false)
  const [showRejectionDialog, setShowRejectionDialog] = useState(false)
  const [selectedRequest, setSelectedRequest] = useState<CaseRequest | null>(null)
  
  // Form states
  const [reviewNotes, setReviewNotes] = useState('')

  useEffect(() => {
    if (systemUser?.role === 'Admin') {
      fetchRequests()
    }
  }, [systemUser])

  const fetchRequests = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await apiClient.getCaseRequests() as any
      
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

  const handleViewDetails = (request: CaseRequest) => {
    setSelectedRequest(request)
    setShowDetailsDialog(true)
  }

  const handleApprove = (request: CaseRequest) => {
    setSelectedRequest(request)
    setReviewNotes('')
    setShowApprovalDialog(true)
  }

  const handleReject = (request: CaseRequest) => {
    setSelectedRequest(request)
    setReviewNotes('')
    setShowRejectionDialog(true)
  }

  const confirmApproval = async () => {
    if (!selectedRequest) return

    try {
      const response = await apiClient.approveCaseRequest(selectedRequest.id, reviewNotes) as any
      
      if (response.status === 'success') {
        toast({
          title: "Request Approved",
          description: `Case request "${selectedRequest.title}" has been approved and the case has been created.`,
          variant: "default"
        })
        setShowApprovalDialog(false)
        fetchRequests()
      } else {
        toast({
          title: "Approval Failed",
          description: response.message || "Failed to approve case request",
          variant: "destructive"
        })
      }
    } catch (error) {
      console.error('Error approving case request:', error)
      toast({
        title: "Error",
        description: "Failed to approve case request. Please try again.",
        variant: "destructive"
      })
    }
  }

  const confirmRejection = async () => {
    if (!selectedRequest) return

    try {
      const response = await apiClient.rejectCaseRequest(selectedRequest.id, reviewNotes) as any
      
      if (response.status === 'success') {
        toast({
          title: "Request Rejected",
          description: `Case request "${selectedRequest.title}" has been rejected.`,
          variant: "default"
        })
        setShowRejectionDialog(false)
        fetchRequests()
      } else {
        toast({
          title: "Rejection Failed",
          description: response.message || "Failed to reject case request",
          variant: "destructive"
        })
      }
    } catch (error) {
      console.error('Error rejecting case request:', error)
      toast({
        title: "Error",
        description: "Failed to reject case request. Please try again.",
        variant: "destructive"
      })
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">Pending</Badge>
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

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  // Filter requests based on search and status
  const filteredRequests = requests.filter(request => {
    const matchesSearch = request.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         request.requested_by?.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         request.requested_by?.email.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesStatus = statusFilter === 'all' || request.status === statusFilter
    
    return matchesSearch && matchesStatus
  })

  // Check if user is admin
  if (systemUser?.role !== 'Admin') {
    return (
      <div className="container mx-auto py-6">
        <Card>
          <CardContent className="flex items-center justify-center py-12">
            <div className="text-center">
              <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
              <h2 className="text-xl font-semibold mb-2">Access Denied</h2>
              <p className="text-muted-foreground">
                Only administrators can access case request management.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Case Request Management</h1>
          <p className="text-muted-foreground">
            Review and approve case creation requests from analysts
          </p>
        </div>
        <Button onClick={fetchRequests} disabled={loading} variant="outline">
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Requests</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{requests.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Pending</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">
              {requests.filter(r => r.status === 'pending').length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Approved</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {requests.filter(r => r.status === 'approved').length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Rejected</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {requests.filter(r => r.status === 'rejected').length}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-4 w-4" />
            Filters
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="search">Search</Label>
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  id="search"
                  placeholder="Search by title, username, or email..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="status">Status</Label>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="All statuses" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All statuses</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="approved">Approved</SelectItem>
                  <SelectItem value="rejected">Rejected</SelectItem>
                  <SelectItem value="cancelled">Cancelled</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Requests Table */}
      <Card>
        <CardHeader>
          <CardTitle>Case Requests</CardTitle>
          <CardDescription>
            {filteredRequests.length} request(s) found
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
              <span className="ml-2 text-muted-foreground">Loading requests...</span>
            </div>
          ) : error ? (
            <div className="text-center py-8">
              <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-red-600 mb-2">Error</h3>
              <p className="text-muted-foreground mb-4">{error}</p>
              <Button onClick={fetchRequests} variant="outline">
                Try Again
              </Button>
            </div>
          ) : filteredRequests.length === 0 ? (
            <div className="text-center py-8">
              <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium text-muted-foreground mb-2">
                No Case Requests Found
              </h3>
              <p className="text-sm text-muted-foreground">
                {searchTerm || statusFilter !== 'all' 
                  ? 'No requests match your current filters.' 
                  : 'No case requests have been submitted yet.'}
              </p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Request</TableHead>
                  <TableHead>Requested By</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Priority</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Submitted</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredRequests.map((request) => (
                  <TableRow key={request.id}>
                    <TableCell>
                      <div>
                        <div className="font-medium">{request.title}</div>
                        {request.description && (
                          <div className="text-sm text-muted-foreground line-clamp-1">
                            {request.description}
                          </div>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div>
                        <div className="font-medium">{request.requested_by?.username}</div>
                        <div className="text-sm text-muted-foreground">
                          {request.requested_by?.email}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>{request.case_type || 'N/A'}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{request.priority || 'N/A'}</Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {getStatusIcon(request.status)}
                        {getStatusBadge(request.status)}
                      </div>
                    </TableCell>
                    <TableCell>{formatDate(request.requested_at)}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleViewDetails(request)}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        {request.status === 'pending' && (
                          <>
                            <Button
                              variant="default"
                              size="sm"
                              onClick={() => handleApprove(request)}
                              className="bg-green-600 hover:bg-green-700"
                            >
                              <CheckCircle className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="destructive"
                              size="sm"
                              onClick={() => handleReject(request)}
                            >
                              <XCircle className="h-4 w-4" />
                            </Button>
                          </>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Request Details Dialog */}
      <Dialog open={showDetailsDialog} onOpenChange={setShowDetailsDialog}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Case Request Details</DialogTitle>
            <DialogDescription>
              Detailed information about the case request
            </DialogDescription>
          </DialogHeader>
          
          {selectedRequest && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="font-medium">Title</Label>
                  <p className="text-sm text-muted-foreground">{selectedRequest.title}</p>
                </div>
                <div>
                  <Label className="font-medium">Request ID</Label>
                  <p className="text-sm text-muted-foreground">#{selectedRequest.id}</p>
                </div>
              </div>

              <div>
                <Label className="font-medium">Description</Label>
                <p className="text-sm text-muted-foreground">
                  {selectedRequest.description || 'No description provided'}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="font-medium">Type</Label>
                  <p className="text-sm text-muted-foreground">{selectedRequest.case_type || 'N/A'}</p>
                </div>
                <div>
                  <Label className="font-medium">Priority</Label>
                  <p className="text-sm text-muted-foreground">{selectedRequest.priority || 'N/A'}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="font-medium">Requested By</Label>
                  <p className="text-sm text-muted-foreground">
                    {selectedRequest.requested_by?.username} ({selectedRequest.requested_by?.email})
                  </p>
                </div>
                <div>
                  <Label className="font-medium">Submitted</Label>
                  <p className="text-sm text-muted-foreground">
                    {formatDate(selectedRequest.requested_at)}
                  </p>
                </div>
              </div>

              {selectedRequest.summary && (
                <div>
                  <Label className="font-medium">Summary</Label>
                  <p className="text-sm text-muted-foreground">{selectedRequest.summary}</p>
                </div>
              )}

              {selectedRequest.objectives && (
                <div>
                  <Label className="font-medium">Objectives</Label>
                  <p className="text-sm text-muted-foreground">{selectedRequest.objectives}</p>
                </div>
              )}

              {selectedRequest.methodology && (
                <div>
                  <Label className="font-medium">Methodology</Label>
                  <p className="text-sm text-muted-foreground">{selectedRequest.methodology}</p>
                </div>
              )}

              {selectedRequest.tags && selectedRequest.tags.length > 0 && (
                <div>
                  <Label className="font-medium">Tags</Label>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {selectedRequest.tags.map((tag, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex items-center gap-2">
                {getStatusIcon(selectedRequest.status)}
                <Label className="font-medium">Status</Label>
                {getStatusBadge(selectedRequest.status)}
              </div>

              {selectedRequest.review_notes && (
                <div>
                  <Label className="font-medium">Review Notes</Label>
                  <p className="text-sm text-muted-foreground p-2 bg-muted rounded">
                    {selectedRequest.review_notes}
                  </p>
                </div>
              )}
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDetailsDialog(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Approval Dialog */}
      <Dialog open={showApprovalDialog} onOpenChange={setShowApprovalDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Approve Case Request</DialogTitle>
            <DialogDescription>
              Approve the case request "{selectedRequest?.title}" and create the case.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div>
              <Label htmlFor="approval-notes">Review Notes (Optional)</Label>
              <Textarea
                id="approval-notes"
                placeholder="Add any notes about the approval..."
                value={reviewNotes}
                onChange={(e) => setReviewNotes(e.target.value)}
                rows={3}
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowApprovalDialog(false)}>
              Cancel
            </Button>
            <Button 
              onClick={confirmApproval}
              className="bg-green-600 hover:bg-green-700"
            >
              <CheckCircle className="h-4 w-4 mr-2" />
              Approve Request
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Rejection Dialog */}
      <Dialog open={showRejectionDialog} onOpenChange={setShowRejectionDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Reject Case Request</DialogTitle>
            <DialogDescription>
              Reject the case request "{selectedRequest?.title}".
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div>
              <Label htmlFor="rejection-notes">Rejection Reason (Required)</Label>
              <Textarea
                id="rejection-notes"
                placeholder="Please provide a reason for rejection..."
                value={reviewNotes}
                onChange={(e) => setReviewNotes(e.target.value)}
                rows={3}
                required
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowRejectionDialog(false)}>
              Cancel
            </Button>
            <Button 
              variant="destructive"
              onClick={confirmRejection}
              disabled={!reviewNotes.trim()}
            >
              <XCircle className="h-4 w-4 mr-2" />
              Reject Request
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
