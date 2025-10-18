'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
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
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { 
  Database,
  Users,
  FileText,
  Tag,
  Globe,
  Search,
  Plus,
  Edit,
  Trash2,
  Download,
  Upload,
  Filter,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Clock,
  BarChart3,
  Settings
} from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api'
import { useAuth } from '@/contexts/AuthContext'

interface PlatformUser {
  id: string
  username: string
  fullName: string
  bio: string
  isFlagged: boolean
  sourceName: string
  platform: string
  createdAt: string
  contentCount: number
  riskScore: number
}

interface Source {
  id: string
  name: string
  platform: string
  type: string
  handle: string
  description: string
  isActive: boolean
  createdAt: string
  lastChecked: string
  userCount: number
  contentCount: number
}

interface Keyword {
  id: string
  term: string
  category: string
  weight: number
  isActive: boolean
  description: string
  createdAt: string
  detectionCount: number
  lastDetection: string
}

interface ContentItem {
  id: string
  title: string
  text: string
  author: string
  platform: string
  riskLevel: string
  status: string
  createdAt: string
  keywordMatches: string[]
  confidence: number
}

interface CaseItem {
  id: string
  title: string
  caseNumber: string
  type: string
  status: string
  priority: string
  assignedTo: string
  createdBy: string
  createdAt: string
  userCount: number
  contentCount: number
  riskScore: number
}

interface DataStats {
  platformUsers: {
    total: number
    flagged: number
    active: number
  }
  sources: {
    total: number
    active: number
    platforms: Record<string, number>
  }
  keywords: {
    total: number
    active: number
    categories: Record<string, number>
  }
  content: {
    total: number
    highRisk: number
    pending: number
    analyzed: number
  }
  cases: {
    total: number
    active: number
    pending: number
    closed: number
  }
}

export default function DataManagement() {
  const { toast } = useToast()
  const { systemUser } = useAuth()
  const [activeTab, setActiveTab] = useState('overview')
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedFilter, setSelectedFilter] = useState('all')
  
  // Data states
  const [stats, setStats] = useState<DataStats | null>(null)
  const [platformUsers, setPlatformUsers] = useState<PlatformUser[]>([])
  const [sources, setSources] = useState<Source[]>([])
  const [keywords, setKeywords] = useState<Keyword[]>([])
  const [content, setContent] = useState<ContentItem[]>([])
  const [cases, setCases] = useState<CaseItem[]>([])
  
  // Dialog states
  const [showSourceDialog, setShowSourceDialog] = useState(false)
  const [showKeywordDialog, setShowKeywordDialog] = useState(false)
  const [showBulkDialog, setShowBulkDialog] = useState(false)
  
  // Form states
  const [newSource, setNewSource] = useState({
    name: '',
    platform: 'telegram',
    type: 'channel',
    handle: '',
    description: ''
  })
  
  const [newKeyword, setNewKeyword] = useState({
    term: '',
    category: 'general',
    weight: 1,
    description: ''
  })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      
      // Load all data in parallel
      const [
        statsResponse,
        usersResponse,
        sourcesResponse,
        keywordsResponse,
        contentResponse,
        casesResponse
      ] = await Promise.all([
        apiClient.getDataStats(),
        apiClient.getPlatformUsers(),
        apiClient.getAdminSources(),
        apiClient.getKeywords(),
        apiClient.getContentData(),
        apiClient.getCasesData()
      ])
      
      setStats(statsResponse as DataStats)
      setPlatformUsers(usersResponse as PlatformUser[])
      setSources(sourcesResponse as Source[])
      setKeywords(keywordsResponse as Keyword[])
      setContent(contentResponse as ContentItem[])
      setCases(casesResponse as CaseItem[])
      
      toast({
        title: 'Success',
        description: 'Data loaded successfully',
        variant: 'default'
      })
    } catch (error: any) {
      console.error('Failed to load data:', error)
      
      // Set default data on error
      setStats({
        platformUsers: { total: 0, flagged: 0, active: 0 },
        sources: { total: 0, active: 0, platforms: {} },
        keywords: { total: 0, active: 0, categories: {} },
        content: { total: 0, highRisk: 0, pending: 0, analyzed: 0 },
        cases: { total: 0, active: 0, pending: 0, closed: 0 }
      })
      setPlatformUsers([])
      setSources([])
      setKeywords([])
      setContent([])
      setCases([])
      
      toast({
        title: 'Error',
        description: 'Failed to load data. Using empty state.',
        variant: 'destructive'
      })
    } finally {
      setLoading(false)
    }
  }

  const handleCreateSource = async () => {
    try {
      const response = await apiClient.createSource(newSource)
      
      setSources(prev => [...prev, response as Source])
      setShowSourceDialog(false)
      setNewSource({ name: '', platform: 'telegram', type: 'channel', handle: '', description: '' })
      
      toast({
        title: 'Success',
        description: 'Source created successfully'
      })
      
      loadData() // Refresh data
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to create source',
        variant: 'destructive'
      })
    }
  }

  const handleCreateKeyword = async () => {
    try {
      const response = await apiClient.createKeyword(newKeyword)
      
      setKeywords(prev => [...prev, response as Keyword])
      setShowKeywordDialog(false)
      setNewKeyword({ term: '', category: 'general', weight: 1, description: '' })
      
      toast({
        title: 'Success',
        description: 'Keyword created successfully'
      })
      
      loadData() // Refresh data
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to create keyword',
        variant: 'destructive'
      })
    }
  }

  const handleToggleUserFlag = async (userId: string) => {
    try {
      await apiClient.toggleUserFlag(userId)
      
      setPlatformUsers(prev => prev.map(user => 
        user.id === userId ? { ...user, isFlagged: !user.isFlagged } : user
      ))
      
      toast({
        title: 'Success',
        description: 'User flag status updated'
      })
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to update user flag',
        variant: 'destructive'
      })
    }
  }

  const handleToggleSource = async (sourceId: string) => {
    try {
      await apiClient.toggleSource(sourceId)
      
      setSources(prev => prev.map(source => 
        source.id === sourceId ? { ...source, isActive: !source.isActive } : source
      ))
      
      toast({
        title: 'Success',
        description: 'Source status updated'
      })
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to update source status',
        variant: 'destructive'
      })
    }
  }

  const handleDeleteSource = async (sourceId: string) => {
    try {
      await apiClient.deleteSource(sourceId)
      setSources(prev => prev.filter(s => s.id !== sourceId))
      toast({ title: 'Deleted', description: 'Source deleted successfully' })
    } catch (error) {
      toast({ title: 'Error', description: 'Failed to delete source', variant: 'destructive' })
    }
  }

  const handleToggleKeyword = async (keywordId: string) => {
    try {
      await apiClient.toggleKeyword(keywordId)
      
      setKeywords(prev => prev.map(keyword => 
        keyword.id === keywordId ? { ...keyword, isActive: !keyword.isActive } : keyword
      ))
      
      toast({
        title: 'Success',
        description: 'Keyword status updated'
      })
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to update keyword status',
        variant: 'destructive'
      })
    }
  }

  const handleDeleteKeyword = async (keywordId: string) => {
    try {
      await apiClient.deleteKeyword(keywordId)
      setKeywords(prev => prev.filter(k => k.id !== keywordId))
      toast({
        title: 'Deleted',
        description: 'Keyword deleted successfully'
      })
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to delete keyword',
        variant: 'destructive'
      })
    }
  }

  const handleExportData = async (dataType: string) => {
    try {
      const response = await apiClient.exportData(dataType)
      
      // Create download link
      const blob = new Blob([JSON.stringify(response, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${dataType}_export_${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      
      toast({
        title: 'Success',
        description: `${dataType} data exported successfully`
      })
    } catch (error) {
      toast({
        title: 'Error',
        description: `Failed to export ${dataType} data`,
        variant: 'destructive'
      })
    }
  }

  const filteredData = (data: any[], filterField: string) => {
    return data.filter(item => {
      const matchesSearch = Object.values(item).some(value => 
        String(value).toLowerCase().includes(searchTerm.toLowerCase())
      )
      const matchesFilter = selectedFilter === 'all' || item[filterField] === selectedFilter
      return matchesSearch && matchesFilter
    })
  }

  const getRiskLevelColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'critical': return 'text-red-400 border-red-400/50'
      case 'high': return 'text-orange-400 border-orange-400/50'
      case 'medium': return 'text-yellow-400 border-yellow-400/50'
      case 'low': return 'text-green-400 border-green-400/50'
      default: return 'text-gray-400 border-gray-400/50'
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-white/10 rounded w-1/3 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-white/5 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Data Management</h1>
          <p className="text-gray-400">Manage and monitor all system data entities</p>
        </div>
        
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => loadData()}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button variant="outline" onClick={() => setShowBulkDialog(true)}>
            <Settings className="h-4 w-4 mr-2" />
            Bulk Operations
          </Button>
        </div>
      </div>

      {/* Overview Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <Card className="bg-white/5 border-white/10">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-400">Platform Users</CardTitle>
              <Users className="h-4 w-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.platformUsers.total}</div>
              <div className="text-sm text-gray-400">
                {stats.platformUsers.flagged} flagged
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white/5 border-white/10">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-400">Sources</CardTitle>
              <Globe className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.sources.total}</div>
              <div className="text-sm text-gray-400">
                {stats.sources.active} active
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white/5 border-white/10">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-400">Keywords</CardTitle>
              <Tag className="h-4 w-4 text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.keywords.total}</div>
              <div className="text-sm text-gray-400">
                {stats.keywords.active} active
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white/5 border-white/10">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-400">Content</CardTitle>
              <FileText className="h-4 w-4 text-yellow-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.content.total}</div>
              <div className="text-sm text-gray-400">
                {stats.content.highRisk} high risk
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white/5 border-white/10">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-400">Cases</CardTitle>
              <Database className="h-4 w-4 text-red-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.cases.total}</div>
              <div className="text-sm text-gray-400">
                {stats.cases.active} active
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Data Management Tabs */}
      <Card className="bg-white/5 border-white/10">
        <CardHeader>
          <CardTitle className="text-white">Data Management</CardTitle>
          <CardDescription className="text-gray-400">
            View and manage all data entities in the system
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-5 bg-white/10">
              <TabsTrigger value="users" className="text-white">Platform Users</TabsTrigger>
              <TabsTrigger value="sources" className="text-white">Sources</TabsTrigger>
              <TabsTrigger value="keywords" className="text-white">Keywords</TabsTrigger>
              <TabsTrigger value="content" className="text-white">Content</TabsTrigger>
              <TabsTrigger value="cases" className="text-white">Cases</TabsTrigger>
            </TabsList>

            {/* Common Controls */}
            <div className="flex gap-4 my-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Search data..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 bg-white/10 border-white/20 text-white"
                  />
                </div>
              </div>
              <Select value={selectedFilter} onValueChange={setSelectedFilter}>
                <SelectTrigger className="w-40 bg-white/10 border-white/20 text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-black border-white/20">
                  <SelectItem value="all">All</SelectItem>
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="inactive">Inactive</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Platform Users Tab */}
            <TabsContent value="users" className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold text-white">Platform Users ({platformUsers.length})</h3>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleExportData('users')}
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Export
                  </Button>
                </div>
              </div>
              
              <div className="rounded-lg border border-white/10 overflow-hidden">
                <Table>
                  <TableHeader>
                    <TableRow className="border-white/10">
                      <TableHead className="text-gray-400">User</TableHead>
                      <TableHead className="text-gray-400">Platform</TableHead>
                      <TableHead className="text-gray-400">Status</TableHead>
                      <TableHead className="text-gray-400">Risk Score</TableHead>
                      <TableHead className="text-gray-400">Content</TableHead>
                      <TableHead className="text-gray-400">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredData(platformUsers, 'platform').map((user) => (
                      <TableRow key={user.id} className="border-white/10">
                        <TableCell>
                          <div>
                            <div className="font-medium text-white">{user.username}</div>
                            <div className="text-sm text-gray-400">{user.fullName}</div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className="text-blue-400 border-blue-400/50">
                            {user.platform}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge 
                            variant="outline" 
                            className={user.isFlagged ? 
                              "text-red-400 border-red-400/50" : 
                              "text-green-400 border-green-400/50"
                            }
                          >
                            {user.isFlagged ? 'Flagged' : 'Normal'}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge 
                            variant="outline" 
                            className={getRiskLevelColor(user.riskScore > 7 ? 'high' : user.riskScore > 4 ? 'medium' : 'low')}
                          >
                            {user.riskScore}/10
                          </Badge>
                        </TableCell>
                        <TableCell className="text-gray-400">{user.contentCount}</TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button 
                              variant="ghost" 
                              size="sm"
                              onClick={() => handleToggleUserFlag(user.id)}
                            >
                              {user.isFlagged ? (
                                <CheckCircle className="h-4 w-4 text-green-400" />
                              ) : (
                                <AlertTriangle className="h-4 w-4 text-red-400" />
                              )}
                            </Button>
                            {/* Edit removed */}
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </TabsContent>

            {/* Sources Tab */}
            <TabsContent value="sources" className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold text-white">Data Sources ({sources.length})</h3>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleExportData('sources')}
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Export
                  </Button>
                  <Dialog open={showSourceDialog} onOpenChange={setShowSourceDialog}>
                    <DialogTrigger asChild>
                      <Button size="sm" className="bg-blue-500 hover:bg-blue-600">
                        <Plus className="h-4 w-4 mr-2" />
                        Add Source
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="bg-black border-white/20">
                      <DialogHeader>
                        <DialogTitle className="text-white">Add New Source</DialogTitle>
                        <DialogDescription className="text-gray-400">
                          Create a new data source for monitoring.
                        </DialogDescription>
                      </DialogHeader>
                      <div className="space-y-4">
                        <div>
                          <Label className="text-white">Name</Label>
                          <Input
                            value={newSource.name}
                            onChange={(e) => setNewSource(prev => ({ ...prev, name: e.target.value }))}
                            className="bg-white/10 border-white/20 text-white"
                            placeholder="Source name"
                          />
                        </div>
                        <div>


              


                          <Label className="text-white">Platform</Label>
                          <Select 
                            value={newSource.platform} 
                            onValueChange={(value) => setNewSource(prev => ({ ...prev, platform: value }))}
                          >
                            <SelectTrigger className="bg-white/10 border-white/20 text-white">
                              <SelectValue />
                            </SelectTrigger>
                            
                            <SelectContent className="bg-black border-white/20">
                              <SelectItem value="telegram">Telegram</SelectItem>
                              <SelectItem value="instagram">Instagram</SelectItem>
                              <SelectItem value="whatsapp">WhatsApp</SelectItem>
                              <SelectItem value="twitter">Twitter</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label className="text-white">Handle</Label>
                          <Input
                            value={newSource.handle}
                            onChange={(e) => setNewSource(prev => ({ ...prev, handle: e.target.value }))}
                            className="bg-white/10 border-white/20 text-white"
                            placeholder="@channel_handle"
                          />
                        </div>
                        <div>
                          <Label className="text-white">Description</Label>
                          <Textarea
                            value={newSource.description}
                            onChange={(e) => setNewSource(prev => ({ ...prev, description: e.target.value }))}
                            className="bg-white/10 border-white/20 text-white"
                            placeholder="Source description"
                          />
                        </div>
                      </div>
                      <DialogFooter>
                        <Button variant="outline" onClick={() => setShowSourceDialog(false)}>
                          Cancel
                        </Button>
                        <Button onClick={handleCreateSource} className="bg-blue-500 hover:bg-blue-600">
                          Create Source
                        </Button>
                      </DialogFooter>
                    </DialogContent>
                  </Dialog>
                </div>
              </div>
              
              <div className="rounded-lg border border-white/10 overflow-hidden">
                <Table>
                  <TableHeader>
                    <TableRow className="border-white/10">
                      <TableHead className="text-gray-400">Source</TableHead>
                      <TableHead className="text-gray-400">Platform</TableHead>
                      <TableHead className="text-gray-400">Status</TableHead>
                      <TableHead className="text-gray-400">Users</TableHead>
                      <TableHead className="text-gray-400">Content</TableHead>
                      <TableHead className="text-gray-400">Last Checked</TableHead>
                      <TableHead className="text-gray-400">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredData(sources, 'platform').map((source) => (
                      <TableRow key={source.id} className="border-white/10">
                        <TableCell>
                          <div>
                            <div className="font-medium text-white">{source.name}</div>
                            <div className="text-sm text-gray-400">{source.handle}</div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className="text-blue-400 border-blue-400/50">
                            {source.platform}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge 
                            variant="outline" 
                            className={source.isActive ? 
                              "text-green-400 border-green-400/50" : 
                              "text-red-400 border-red-400/50"
                            }
                          >
                            {source.isActive ? 'Active' : 'Inactive'}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-gray-400">{source.userCount}</TableCell>
                        <TableCell className="text-gray-400">{source.contentCount}</TableCell>
                        <TableCell className="text-gray-400">{source.lastChecked}</TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button 
                              variant="ghost" 
                              size="sm"
                              onClick={() => handleToggleSource(source.id)}
                            >
                              {source.isActive ? (
                                <AlertTriangle className="h-4 w-4 text-red-400" />
                              ) : (
                                <CheckCircle className="h-4 w-4 text-green-400" />
                              )}
                            </Button>
                            {/* Edit removed */}
                            <AlertDialog>
                              <AlertDialogTrigger asChild>
                                <Button variant="ghost" size="sm">
                                  <Trash2 className="h-4 w-4 text-red-400" />
                                </Button>
                              </AlertDialogTrigger>
                              <AlertDialogContent className="bg-black border-white/20">
                                <AlertDialogHeader>
                                  <AlertDialogTitle className="text-white">Delete source?</AlertDialogTitle>
                                  <AlertDialogDescription className="text-gray-400">
                                    This will permanently delete the source "{source.name}" and its associated content.
                                  </AlertDialogDescription>
                                </AlertDialogHeader>
                                <AlertDialogFooter>
                                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                                  <AlertDialogAction onClick={() => handleDeleteSource(source.id)} className="bg-red-600 hover:bg-red-700">
                                    Delete
                                  </AlertDialogAction>
                                </AlertDialogFooter>
                              </AlertDialogContent>
                            </AlertDialog>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </TabsContent>

            {/* Keywords Tab */}
            <TabsContent value="keywords" className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold text-white">Detection Keywords ({keywords.length})</h3>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleExportData('keywords')}
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Export
                  </Button>
                  <Dialog open={showKeywordDialog} onOpenChange={setShowKeywordDialog}>
                    <DialogTrigger asChild>
                      <Button size="sm" className="bg-purple-500 hover:bg-purple-600">
                        <Plus className="h-4 w-4 mr-2" />
                        Add Keyword
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="bg-black border-white/20">
                      <DialogHeader>
                        <DialogTitle className="text-white">Add New Keyword</DialogTitle>
                        <DialogDescription className="text-gray-400">
                          Create a new detection keyword for content analysis.
                        </DialogDescription>
                      </DialogHeader>
                      <div className="space-y-4">
                        <div>
                          <Label className="text-white">Term</Label>
                          <Input
                            value={newKeyword.term}
                            onChange={(e) => setNewKeyword(prev => ({ ...prev, term: e.target.value }))}
                            className="bg-white/10 border-white/20 text-white"
                            placeholder="Keyword term"
                          />
                        </div>
                        <div>
                          <Label className="text-white">Category</Label>
                          <Select 
                            value={newKeyword.category} 
                            onValueChange={(value) => setNewKeyword(prev => ({ ...prev, category: value }))}
                          >
                            <SelectTrigger className="bg-white/10 border-white/20 text-white">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent className="bg-black border-white/20">
                              <SelectItem value="general">General</SelectItem>
                              <SelectItem value="drugs">Drugs</SelectItem>
                              <SelectItem value="violence">Violence</SelectItem>
                              <SelectItem value="terrorism">Terrorism</SelectItem>
                              <SelectItem value="fraud">Fraud</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label className="text-white">Weight (1-10)</Label>
                          <Input
                            type="number"
                            min="1"
                            max="10"
                            value={newKeyword.weight}
                            onChange={(e) => setNewKeyword(prev => ({ ...prev, weight: parseInt(e.target.value) }))}
                            className="bg-white/10 border-white/20 text-white"
                          />
                        </div>
                        <div>
                          <Label className="text-white">Description</Label>
                          <Textarea
                            value={newKeyword.description}
                            onChange={(e) => setNewKeyword(prev => ({ ...prev, description: e.target.value }))}
                            className="bg-white/10 border-white/20 text-white"
                            placeholder="Keyword description"
                          />
                        </div>
                      </div>
                      <DialogFooter>
                        <Button variant="outline" onClick={() => setShowKeywordDialog(false)}>
                          Cancel
                        </Button>
                        <Button onClick={handleCreateKeyword} className="bg-purple-500 hover:bg-purple-600">
                          Create Keyword
                        </Button>
                      </DialogFooter>
                    </DialogContent>
                  </Dialog>
                </div>
              </div>
              
              <div className="rounded-lg border border-white/10 overflow-hidden">
                <Table>
                  <TableHeader>
                    <TableRow className="border-white/10">
                      <TableHead className="text-gray-400">Term</TableHead>
                      <TableHead className="text-gray-400">Category</TableHead>
                      <TableHead className="text-gray-400">Weight</TableHead>
                      <TableHead className="text-gray-400">Status</TableHead>
                      <TableHead className="text-gray-400">Detections</TableHead>
                      <TableHead className="text-gray-400">Last Detection</TableHead>
                      <TableHead className="text-gray-400">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredData(keywords, 'category').map((keyword) => (
                      <TableRow key={keyword.id} className="border-white/10">
                        <TableCell>
                          <div className="font-medium text-white">{keyword.term}</div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className="text-purple-400 border-purple-400/50">
                            {keyword.category}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge 
                            variant="outline" 
                            className={keyword.weight > 7 ? 
                              "text-red-400 border-red-400/50" : 
                              keyword.weight > 4 ? 
                              "text-yellow-400 border-yellow-400/50" : 
                              "text-green-400 border-green-400/50"
                            }
                          >
                            {keyword.weight}/10
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge 
                            variant="outline" 
                            className={keyword.isActive ? 
                              "text-green-400 border-green-400/50" : 
                              "text-red-400 border-red-400/50"
                            }
                          >
                            {keyword.isActive ? 'Active' : 'Inactive'}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-gray-400">{keyword.detectionCount}</TableCell>
                        <TableCell className="text-gray-400">{keyword.lastDetection}</TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button 
                              variant="ghost" 
                              size="sm"
                              onClick={() => handleToggleKeyword(keyword.id)}
                            >
                              {keyword.isActive ? (
                                <AlertTriangle className="h-4 w-4 text-red-400" />
                              ) : (
                                <CheckCircle className="h-4 w-4 text-green-400" />
                              )}
                            </Button>
                            {/* Edit removed */}
                            <AlertDialog>
                              <AlertDialogTrigger asChild>
                                <Button variant="ghost" size="sm">
                                  <Trash2 className="h-4 w-4 text-red-400" />
                                </Button>
                              </AlertDialogTrigger>
                              <AlertDialogContent className="bg-black border-white/20">
                                <AlertDialogHeader>
                                  <AlertDialogTitle className="text-white">Delete keyword?</AlertDialogTitle>
                                  <AlertDialogDescription className="text-gray-400">
                                    This action cannot be undone. The keyword "{keyword.term}" will be permanently deleted.
                                  </AlertDialogDescription>
                                </AlertDialogHeader>
                                <AlertDialogFooter>
                                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                                  <AlertDialogAction onClick={() => handleDeleteKeyword(keyword.id)} className="bg-red-600 hover:bg-red-700">
                                    Delete
                                  </AlertDialogAction>
                                </AlertDialogFooter>
                              </AlertDialogContent>
                            </AlertDialog>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </TabsContent>

            {/* Content Tab */}
                  <TabsContent value="content" className="space-y-4">
                    <div className="flex justify-between items-center">
                      <h3 className="text-lg font-semibold text-white">Analyzed Content ({content.length})</h3>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleExportData('content')}
                        >
                          <Download className="h-4 w-4 mr-2" />
                          Export
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {/* Implement bulk analysis */}}
                        >
                          <BarChart3 className="h-4 w-4 mr-2" />
                          Analyze All
                        </Button>
                      </div>
                    </div>
                    
                    <div className="rounded-lg border border-white/10 overflow-hidden">
                      <Table>
                        <TableHeader>
                          <TableRow className="border-white/10">
                            <TableHead className="text-gray-400">Content</TableHead>
                            <TableHead className="text-gray-400">Author</TableHead>
                            <TableHead className="text-gray-400">Platform</TableHead>
                            <TableHead className="text-gray-400">Risk Level</TableHead>
                            <TableHead className="text-gray-400">Status</TableHead>
                            <TableHead className="text-gray-400">Keywords</TableHead>
                            <TableHead className="text-gray-400">Actions</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {filteredData(content, 'platform').map((item) => (
                            <TableRow key={item.id} className="border-white/10">
                              <TableCell>
                                <div>
                                  <div className="font-medium text-white max-w-xs truncate">
                                    {item.title || 'Untitled'}
                                  </div>
                                  <div className="text-sm text-gray-400 max-w-xs truncate">
                                    {item.text.substring(0, 100)}...
                                  </div>
                                </div>
                              </TableCell>
                              <TableCell className="text-gray-400">{item.author}</TableCell>
                              <TableCell>
                                <Badge variant="outline" className="text-blue-400 border-blue-400/50">
                                  {item.platform}
                                </Badge>
                              </TableCell>
                              <TableCell>
                                <Badge 
                                  variant="outline" 
                                  className={getRiskLevelColor(item.riskLevel)}
                                >
                                  {item.riskLevel}
                                </Badge>
                              </TableCell>
                              <TableCell>
                                <Badge 
                                  variant="outline" 
                                  className={item.status === 'analyzed' ? 
                                    "text-green-400 border-green-400/50" : 
                                    "text-yellow-400 border-yellow-400/50"
                                  }
                                >
                                  {item.status}
                                </Badge>
                              </TableCell>
                              <TableCell>
                                <div className="flex flex-wrap gap-1">
                                  {item.keywordMatches.slice(0, 2).map((keyword: string, idx: number) => (
                                    <Badge key={idx} variant="outline" className="text-xs text-purple-400 border-purple-400/50">
                                      {keyword}
                                    </Badge>
                                  ))}
                                  {item.keywordMatches.length > 2 && (
                                    <Badge variant="outline" className="text-xs text-gray-400 border-gray-400/50">
                                      +{item.keywordMatches.length - 2}
                                    </Badge>
                                  )}
                                </div>
                              </TableCell>
                              <TableCell>
                                <div className="flex gap-2">
                                  {/* Edit removed */}
                                  <AlertDialog>
                                    <AlertDialogTrigger asChild>
                                      <Button variant="ghost" size="sm">
                                        <Trash2 className="h-4 w-4 text-red-400" />
                                      </Button>
                                    </AlertDialogTrigger>
                                    <AlertDialogContent className="bg-black border-white/20">
                                      <AlertDialogHeader>
                                        <AlertDialogTitle className="text-white">Delete content?</AlertDialogTitle>
                                        <AlertDialogDescription className="text-gray-400">
                                          This will permanently delete this content item.
                                        </AlertDialogDescription>
                                      </AlertDialogHeader>
                                      <AlertDialogFooter>
                                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                                        <AlertDialogAction onClick={() => apiClient.deleteContentItem(item.id).then(() => setContent(prev => prev.filter(c => c.id !== item.id)))} className="bg-red-600 hover:bg-red-700">
                                          Delete
                                        </AlertDialogAction>
                                      </AlertDialogFooter>
                                    </AlertDialogContent>
                                  </AlertDialog>
                                </div>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  </TabsContent>

                  {/* Cases Tab */}
                  <TabsContent value="cases" className="space-y-4">
                    <div className="flex justify-between items-center">
                      <h3 className="text-lg font-semibold text-white">Investigation Cases ({cases.length})</h3>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleExportData('cases')}
                        >
                          <Download className="h-4 w-4 mr-2" />
                          Export
                        </Button>
                      </div>
                    </div>
                    
                    <div className="rounded-lg border border-white/10 overflow-hidden">
                      <Table>
                        <TableHeader>
                          <TableRow className="border-white/10">
                            <TableHead className="text-gray-400">Case</TableHead>
                            <TableHead className="text-gray-400">Type</TableHead>
                            <TableHead className="text-gray-400">Status</TableHead>
                            <TableHead className="text-gray-400">Priority</TableHead>
                            <TableHead className="text-gray-400">Assigned To</TableHead>
                            <TableHead className="text-gray-400">Users</TableHead>
                            <TableHead className="text-gray-400">Actions</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {filteredData(cases, 'type').map((caseItem) => (
                            <TableRow key={caseItem.id} className="border-white/10">
                              <TableCell>
                                <div>
                                  <div className="font-medium text-white">{caseItem.title}</div>
                                  <div className="text-sm text-gray-400">{caseItem.caseNumber}</div>
                                </div>
                              </TableCell>
                              <TableCell>
                                <Badge variant="outline" className="text-blue-400 border-blue-400/50">
                                  {caseItem.type}
                                </Badge>
                              </TableCell>
                              <TableCell>
                                <Badge 
                                  variant="outline" 
                                  className={caseItem.status === 'open' ? 
                                    "text-green-400 border-green-400/50" : 
                                    caseItem.status === 'pending' ?
                                    "text-yellow-400 border-yellow-400/50" :
                                    "text-gray-400 border-gray-400/50"
                                  }
                                >
                                  {caseItem.status}
                                </Badge>
                              </TableCell>
                              <TableCell>
                                <Badge 
                                  variant="outline" 
                                  className={caseItem.priority === 'high' ? 
                                    "text-red-400 border-red-400/50" : 
                                    caseItem.priority === 'medium' ?
                                    "text-yellow-400 border-yellow-400/50" :
                                    "text-green-400 border-green-400/50"
                                  }
                                >
                                  {caseItem.priority}
                                </Badge>
                              </TableCell>
                              <TableCell className="text-gray-400">{caseItem.assignedTo}</TableCell>
                              <TableCell className="text-gray-400">{caseItem.userCount}</TableCell>
                              <TableCell>
                                <div className="flex gap-2">
                                  {/* Edit removed */}
                                  <Button variant="ghost" size="sm">
                                    <Trash2 className="h-4 w-4 text-red-400" />
                                  </Button>
                                </div>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Bulk Operations Dialog */}
      <Dialog open={showBulkDialog} onOpenChange={setShowBulkDialog}>
        <DialogContent className="bg-black border-white/20 max-w-2xl">
          <DialogHeader>
            <DialogTitle className="text-white">Bulk Operations</DialogTitle>
            <DialogDescription className="text-gray-400">
              Perform bulk operations on data entities
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Card className="bg-white/5 border-white/10 p-4">
                <h4 className="font-semibold text-white mb-2">Data Export</h4>
                <p className="text-sm text-gray-400 mb-3">Export all data entities</p>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="w-full"
                  onClick={() => handleExportData('all')}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Export All Data
                </Button>
              </Card>
              <Card className="bg-white/5 border-white/10 p-4">
                <h4 className="font-semibold text-white mb-2">Data Import</h4>
                <p className="text-sm text-gray-400 mb-3">Import data from file</p>
                <Button variant="outline" size="sm" className="w-full">
                  <Upload className="h-4 w-4 mr-2" />
                  Import Data
                </Button>
              </Card>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Card className="bg-white/5 border-white/10 p-4">
                <h4 className="font-semibold text-white mb-2">Bulk Analysis</h4>
                <p className="text-sm text-gray-400 mb-3">Reanalyze all content</p>
                <Button variant="outline" size="sm" className="w-full">
                  <BarChart3 className="h-4 w-4 mr-2" />
                  Analyze All
                </Button>
              </Card>
              <Card className="bg-white/5 border-white/10 p-4">
                <h4 className="font-semibold text-white mb-2">Cleanup</h4>
                <p className="text-sm text-gray-400 mb-3">Remove old/unused data</p>
                <Button variant="outline" size="sm" className="w-full">
                  <Trash2 className="h-4 w-4 mr-2" />
                  Clean Database
                </Button>
              </Card>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowBulkDialog(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
