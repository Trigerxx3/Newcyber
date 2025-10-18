'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
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
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Switch } from '@/components/ui/switch'
import { 
  Download,
  Upload,
  Play,
  Pause,
  Square,
  RefreshCw,
  Settings,
  Eye,
  Calendar,
  Clock,
  Globe,
  Search,
  Plus,
  Edit,
  Trash2,
  AlertTriangle,
  CheckCircle,
  Activity,
  BarChart3,
  Filter,
  ExternalLink
} from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api'
import { useAuth } from '@/contexts/AuthContext'

interface ScrapingJob {
  id: string
  name: string
  platform: 'telegram' | 'instagram' | 'whatsapp'
  target: string
  targetType: 'channel' | 'group' | 'profile' | 'hashtag'
  status: 'running' | 'paused' | 'stopped' | 'error' | 'completed'
  schedule: string
  lastRun: string
  nextRun: string
  totalScraped: number
  newItems: number
  errors: number
  isActive: boolean
  settings: {
    maxItems: number
    interval: number
    keywords: string[]
    includeMedia: boolean
    includeComments: boolean
  }
  createdAt: string
  updatedAt: string
}

interface ScrapedContent {
  id: string
  jobId: string
  platform: string
  author: string
  text: string
  url: string
  mediaUrls: string[]
  timestamp: string
  scrapedAt: string
  keywordMatches: string[]
  sentiment: number
  engagement: {
    likes: number
    shares: number
    comments: number
  }
  processed: boolean
  flagged: boolean
}

interface ScrapingStats {
  totalJobs: number
  activeJobs: number
  pausedJobs: number
  totalContent: number
  todayScraped: number
  averagePerDay: number
  platforms: {
    telegram: { jobs: number; content: number }
    instagram: { jobs: number; content: number }
    whatsapp: { jobs: number; content: number }
  }
  topSources: Array<{
    name: string
    platform: string
    content: number
  }>
}

export default function DataScraping() {
  const { toast } = useToast()
  const { systemUser } = useAuth()
  const [activeTab, setActiveTab] = useState('content')
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedPlatform, setSelectedPlatform] = useState('all')
  const [selectedStatus, setSelectedStatus] = useState('all')
  
  // Data states
  const [stats, setStats] = useState<ScrapingStats | null>(null)
  const [jobs, setJobs] = useState<ScrapingJob[]>([])
  const [content, setContent] = useState<ScrapedContent[]>([])
  const [deleteTarget, setDeleteTarget] = useState<ScrapedContent | null>(null)
  
  // Dialog states
  const [showJobDialog, setShowJobDialog] = useState(false)
  const [showContentDialog, setShowContentDialog] = useState(false)
  const [selectedContent, setSelectedContent] = useState<ScrapedContent | null>(null)
  
  // Form states
  const [newJob, setNewJob] = useState({
    name: '',
    platform: 'telegram' as 'telegram' | 'instagram' | 'whatsapp',
    target: '',
    targetType: 'channel' as 'channel' | 'group' | 'profile' | 'hashtag',
    schedule: 'hourly',
    maxItems: 100,
    interval: 60,
    keywords: '',
    includeMedia: true,
    includeComments: false
  })

  // Real scraping states
  const [realScrapePlatform, setRealScrapePlatform] = useState<'telegram' | 'instagram'>('telegram')
  const [realScrapeChannel, setRealScrapeChannel] = useState('')
  const [realScrapeLimit, setRealScrapeLimit] = useState('10')
  const [realScrapeLoading, setRealScrapeLoading] = useState(false)
  const [realScrapeResult, setRealScrapeResult] = useState<any>(null)

  useEffect(() => {
    loadData()
    // Set up auto-refresh every 30 seconds
    const interval = setInterval(loadData, 30000)
    return () => clearInterval(interval)
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      
      const [statsResponse, jobsResponse, contentResponse] = await Promise.all([
        apiClient.getScrapingStats(),
        apiClient.getScrapingJobs(),
        apiClient.getScrapedContent({ limit: 100 })
      ])
      
      setStats(statsResponse as ScrapingStats)
      setJobs(jobsResponse as ScrapingJob[])
      setContent(contentResponse as ScrapedContent[])
      
    } catch (error: any) {
      console.error('Failed to load scraping data:', error)
      
      // Set default data on error
      setStats({
        totalJobs: 0,
        activeJobs: 0,
        pausedJobs: 0,
        totalContent: 0,
        todayScraped: 0,
        averagePerDay: 0,
        platforms: {
          telegram: { jobs: 0, content: 0 },
          instagram: { jobs: 0, content: 0 },
          whatsapp: { jobs: 0, content: 0 }
        },
        topSources: []
      })
      setJobs([])
      setContent([])
      
      toast({
        title: 'Warning',
        description: 'Failed to load scraping data. Using empty state.',
        variant: 'destructive'
      })
    } finally {
      setLoading(false)
    }
  }

  const handleCreateJob = async () => {
    try {
      if (!newJob.name || !newJob.target) {
        toast({
          title: 'Validation Error',
          description: 'Please fill in all required fields',
          variant: 'destructive'
        })
        return
      }

      const jobData = {
        ...newJob,
        keywords: newJob.keywords.split(',').map(k => k.trim()).filter(k => k),
        settings: {
          maxItems: newJob.maxItems,
          interval: newJob.interval,
          keywords: newJob.keywords.split(',').map(k => k.trim()).filter(k => k),
          includeMedia: newJob.includeMedia,
          includeComments: newJob.includeComments
        }
      }
      
      const response = await apiClient.createScrapingJob(jobData)
      setJobs(prev => [...prev, response as ScrapingJob])
      setShowJobDialog(false)
      setNewJob({
        name: '',
        platform: 'telegram',
        target: '',
        targetType: 'channel',
        schedule: 'hourly',
        maxItems: 100,
        interval: 60,
        keywords: '',
        includeMedia: true,
        includeComments: false
      })
      
      toast({
        title: 'Success',
        description: 'Scraping job created successfully'
      })
      
      loadData()
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to create scraping job',
        variant: 'destructive'
      })
    }
  }

  const handleRealScrape = async () => {
    if (!realScrapeChannel.trim()) {
      toast({
        title: 'Validation Error',
        description: realScrapePlatform === 'telegram' ? 'Please enter a channel name' : 'Please enter an Instagram username',
        variant: 'destructive'
      })
      return
    }

    setRealScrapeLoading(true)
    setRealScrapeResult(null)

    try {
      let response: any
      if (realScrapePlatform === 'telegram') {
        response = await apiClient.scrapeTelegramChannel(
          realScrapeChannel.trim(),
          parseInt(realScrapeLimit) || 10
        )
        setRealScrapeResult(response)
        toast({
          title: 'Scraping Complete!',
          description: `Successfully scraped ${response.saved_to_db} new messages from @${response.channel}`,
        })
      } else {
        response = await apiClient.scrapeInstagramProfile(
          realScrapeChannel.trim(),
          parseInt(realScrapeLimit) || 10
        )
        setRealScrapeResult(response)
        toast({
          title: 'Instagram Scrape Complete!',
          description: `Fetched ${response.saved_to_db ?? response.total_scraped ?? 'some'} posts from @${realScrapeChannel.trim()}`,
        })
      }

      // Reload the content to show new scraped data
      loadData()
      
    } catch (error: any) {
      console.error('Real scraping error:', error)
      toast({
        title: 'Scraping Failed',
        description: error.message || (realScrapePlatform === 'telegram' ? 'Failed to scrape channel. Please check the channel name and try again.' : 'Failed to scrape Instagram profile. Please check the username and try again.'),
        variant: 'destructive'
      })
    } finally {
      setRealScrapeLoading(false)
    }
  }

  const handleJobAction = async (jobId: string, action: 'start' | 'pause' | 'stop' | 'delete') => {
    try {
      await apiClient.controlScrapingJob(jobId, action)
      
      if (action === 'delete') {
        setJobs(prev => prev.filter(job => job.id !== jobId))
      } else {
        setJobs(prev => prev.map(job => 
          job.id === jobId 
            ? { 
                ...job, 
                status: action === 'start' ? 'running' : action === 'pause' ? 'paused' : 'stopped' 
              }
            : job
        ))
      }
      
      toast({
        title: 'Success',
        description: `Job ${action}ed successfully`
      })
      
      loadData()
    } catch (error) {
      toast({
        title: 'Error',
        description: `Failed to ${action} job`,
        variant: 'destructive'
      })
    }
  }

  const handleToggleJob = async (jobId: string) => {
    try {
      await apiClient.toggleScrapingJob(jobId)
      
      setJobs(prev => prev.map(job => 
        job.id === jobId ? { ...job, isActive: !job.isActive } : job
      ))
      
      toast({
        title: 'Success',
        description: 'Job status updated'
      })
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to toggle job status',
        variant: 'destructive'
      })
    }
  }

  const handleRunJobNow = async (jobId: string) => {
    try {
      await apiClient.runScrapingJobNow(jobId)
      
      setJobs(prev => prev.map(job => 
        job.id === jobId ? { ...job, status: 'running' } : job
      ))
      
      toast({
        title: 'Success',
        description: 'Job started manually'
      })
      
      loadData()
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to start job',
        variant: 'destructive'
      })
    }
  }

  const handleExportData = async (type: 'jobs' | 'content') => {
    try {
      const response = await apiClient.exportScrapingData(type)
      
      const blob = new Blob([JSON.stringify(response, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${type}_export_${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      
      toast({
        title: 'Success',
        description: `${type} data exported successfully`
      })
    } catch (error) {
      toast({
        title: 'Error',
        description: `Failed to export ${type} data`,
        variant: 'destructive'
      })
    }
  }

  const handleDeleteContent = async (contentId: string) => {
    try {
      await apiClient.deleteScrapedContent(contentId)
      setContent(prev => prev.filter(item => item.id !== contentId))
      toast({
        title: 'Deleted',
        description: 'Scraped content removed successfully.'
      })
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to delete content',
        variant: 'destructive'
      })
    } finally {
      setDeleteTarget(null)
    }
  }

  const filteredJobs = jobs.filter(job => {
    const jobName = (job?.name || '').toString().toLowerCase()
    const jobTarget = (job?.target || '').toString().toLowerCase()
    const q = (searchTerm || '').toString().toLowerCase()
    const matchesSearch = jobName.includes(q) || jobTarget.includes(q)
    const matchesPlatform = selectedPlatform === 'all' || job.platform === selectedPlatform
    const matchesStatus = selectedStatus === 'all' || job.status === selectedStatus
    return matchesSearch && matchesPlatform && matchesStatus
  })

  const filteredContent = content.filter(item => {
    const text = (item?.text || '').toString().toLowerCase()
    const author = (item?.author || '').toString().toLowerCase()
    const q = (searchTerm || '').toString().toLowerCase()
    const matchesSearch = text.includes(q) || author.includes(q)
    const matchesPlatform = selectedPlatform === 'all' || item.platform === selectedPlatform
    return matchesSearch && matchesPlatform
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'text-green-400 border-green-400/50'
      case 'paused': return 'text-yellow-400 border-yellow-400/50'
      case 'stopped': return 'text-gray-400 border-gray-400/50'
      case 'error': return 'text-red-400 border-red-400/50'
      case 'completed': return 'text-blue-400 border-blue-400/50'
      default: return 'text-gray-400 border-gray-400/50'
    }
  }

  const getPlatformColor = (platform: string) => {
    switch (platform) {
      case 'telegram': return 'text-blue-400 border-blue-400/50'
      case 'instagram': return 'text-pink-400 border-pink-400/50'
      case 'whatsapp': return 'text-green-400 border-green-400/50'
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
          <h1 className="text-2xl font-bold text-white">Data Scraping</h1>
          <p className="text-gray-400">Manage automated data collection from social platforms</p>
        </div>
        
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => loadData()}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          {/* New Scraping Job button/dialog temporarily disabled */}
        </div>
      </div>

      {/* Stats Overview */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Total Jobs card temporarily disabled */}

          <Card className="bg-white/5 border-white/10">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-400">Total Content</CardTitle>
              <BarChart3 className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.totalContent.toLocaleString()}</div>
              <div className="text-sm text-gray-400">
                {stats.todayScraped} today
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white/5 border-white/10">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-400">Daily Average</CardTitle>
              <Clock className="h-4 w-4 text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.averagePerDay}</div>
              <div className="text-sm text-gray-400">
                items per day
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white/5 border-white/10">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-400">Top Platform</CardTitle>
              <Globe className="h-4 w-4 text-yellow-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {Object.entries(stats.platforms).reduce((a, b) => 
                  stats.platforms[a[0] as keyof typeof stats.platforms].content > 
                  stats.platforms[b[0] as keyof typeof stats.platforms].content ? a : b
                )[0]}
              </div>
              <div className="text-sm text-gray-400">
                most content
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Content */}
      <Card className="bg-white/5 border-white/10">
        <CardHeader>
          <CardTitle className="text-white">Scraping Management</CardTitle>
          <CardDescription className="text-gray-400">
            Monitor and control data collection jobs
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-2 bg-white/10">
              {/* <TabsTrigger value="jobs" className="text-white">Scraping Jobs</TabsTrigger> */}
              <TabsTrigger value="content" className="text-white">Scraped Content</TabsTrigger>
              <TabsTrigger value="analytics" className="text-white">Analytics</TabsTrigger>
            </TabsList>

            {/* Real Scraping Section */}
            <Card className="bg-blue-500/10 border-blue-500/20 my-6">
              <CardHeader>
                <CardTitle className="text-blue-400 text-lg">🔴 Live Scraping</CardTitle>
                <CardDescription className="text-gray-300">
                  Scrape real data from Telegram channels or Instagram profiles and save to database
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex gap-4 items-end">
                  <div>
                    <Label className="text-white text-sm">Platform</Label>
                    <Select value={realScrapePlatform} onValueChange={(v: 'telegram' | 'instagram') => setRealScrapePlatform(v)}>
                      <SelectTrigger className="w-40 bg-white/10 border-white/20 text-white">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-black border-white/20">
                        <SelectItem value="telegram">Telegram</SelectItem>
                        <SelectItem value="instagram">Instagram</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="flex-1">
                    <Label htmlFor="channel-input" className="text-white text-sm">
                      {realScrapePlatform === 'telegram' ? 'Telegram Channel' : 'Instagram Username'}
                    </Label>
                    <Input
                      id="channel-input"
                      placeholder={realScrapePlatform === 'telegram' ? 'durov, telegram, news, etc.' : 'instagram, natgeo, nasa, etc.'}
                      value={realScrapeChannel}
                      onChange={(e) => setRealScrapeChannel(e.target.value)}
                      className="bg-white/10 border-white/20 text-white mt-1"
                    />
                    <p className="text-xs text-gray-400 mt-1">
                      {realScrapePlatform === 'telegram' ? 'Enter channel name without @ symbol' : 'Enter profile username without @ symbol'}
                    </p>
                  </div>
                  <div className="w-32">
                    <Label htmlFor="limit-input" className="text-white text-sm">Messages</Label>
                    <Input
                      id="limit-input"
                      type="number"
                      placeholder="10"
                      value={realScrapeLimit}
                      onChange={(e) => setRealScrapeLimit(e.target.value)}
                      className="bg-white/10 border-white/20 text-white mt-1"
                      min="1"
                      max="100"
                    />
                  </div>
                  <Button
                    onClick={handleRealScrape}
                    disabled={!realScrapeChannel || realScrapeLoading}
                    className="bg-green-600 hover:bg-green-700 text-white h-10"
                  >
                    {realScrapeLoading ? (
                      <>
                        <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                        Scraping...
                      </>
                    ) : (
                      <>
                        <Download className="h-4 w-4 mr-2" />
                        {realScrapePlatform === 'telegram' ? 'Scrape Telegram' : 'Scrape Instagram'}
                      </>
                    )}
                  </Button>
                </div>
                {realScrapeResult && (
                  <div className="mt-4 p-3 bg-green-500/10 border border-green-500/20 rounded-lg">
                    <p className="text-green-400 text-sm font-medium">
                      {realScrapePlatform === 'telegram'
                        ? `✅ Successfully scraped ${realScrapeResult.saved_to_db} new messages from @${realScrapeResult.channel}`
                        : `✅ Successfully scraped posts from @${realScrapeChannel.trim()}`}
                    </p>
                    <p className="text-gray-300 text-xs mt-1">
                      {realScrapePlatform === 'telegram'
                        ? `Total found: ${realScrapeResult.total_scraped} | Saved to database: ${realScrapeResult.saved_to_db}`
                        : `Saved to database: ${realScrapeResult.saved_to_db ?? 'N/A'}`}
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Common Controls */}
            <div className="flex gap-4 my-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Search..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 bg-white/10 border-white/20 text-white"
                  />
                </div>
              </div>
              <Select value={selectedPlatform} onValueChange={setSelectedPlatform}>
                <SelectTrigger className="w-40 bg-white/10 border-white/20 text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-black border-white/20">
                  <SelectItem value="all">All Platforms</SelectItem>
                  <SelectItem value="telegram">Telegram</SelectItem>
                  <SelectItem value="instagram">Instagram</SelectItem>
                  <SelectItem value="whatsapp">WhatsApp</SelectItem>
                </SelectContent>
              </Select>
              {/* Jobs status filter temporarily disabled */}
            </div>

            {/* Scraping Jobs Tab temporarily disabled */}

            {/* Scraped Content Tab */}
            <TabsContent value="content" className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold text-white">Scraped Content ({filteredContent.length})</h3>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleExportData('content')}
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
                      <TableHead className="text-gray-400">Content</TableHead>
                      <TableHead className="text-gray-400">Platform</TableHead>
                      <TableHead className="text-gray-400">Author</TableHead>
                      <TableHead className="text-gray-400">Keywords</TableHead>
                      <TableHead className="text-gray-400">Engagement</TableHead>
                      <TableHead className="text-gray-400">Scraped</TableHead>
                      <TableHead className="text-gray-400">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredContent.map((item) => (
                      <TableRow key={item.id} className="border-white/10">
                        <TableCell>
                          <div className="max-w-xs">
                            <div className="text-white truncate">{item.text.substring(0, 100)}...</div>
                            <div className="text-sm text-gray-400">
                              {new Date(item.timestamp).toLocaleDateString()}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge 
                            variant="outline" 
                            className={getPlatformColor(item.platform)}
                          >
                            {item.platform}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-gray-400">{item.author}</TableCell>
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
                          <div className="text-sm text-gray-400">
                            👍 {item.engagement.likes} • 
                            💬 {item.engagement.comments} • 
                            🔄 {item.engagement.shares}
                          </div>
                        </TableCell>
                        <TableCell className="text-gray-400">
                          {new Date(item.scrapedAt).toLocaleDateString()}
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-1">
                            <Button 
                              variant="ghost" 
                              size="sm"
                              onClick={() => {
                                setSelectedContent(item)
                                setShowContentDialog(true)
                              }}
                            >
                              <Eye className="h-4 w-4" />
                            </Button>
                            {item.url && (
                              <Button 
                                variant="ghost" 
                                size="sm"
                                onClick={() => window.open(item.url, '_blank')}
                              >
                                <ExternalLink className="h-4 w-4" />
                              </Button>
                            )}
                            <Button 
                              variant="ghost" 
                              size="sm"
                              className={item.flagged ? "text-red-400" : "text-yellow-400"}
                            >
                              {item.flagged ? <AlertTriangle className="h-4 w-4" /> : <CheckCircle className="h-4 w-4" />}
                            </Button>
                            <Button 
                              variant="ghost" 
                              size="sm"
                              onClick={() => setDeleteTarget(item)}
                            >
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

            {/* Analytics Tab */}
            <TabsContent value="analytics" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card className="bg-white/5 border-white/10">
                  <CardHeader>
                    <CardTitle className="text-white">Platform Distribution</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {stats && Object.entries(stats.platforms).map(([platform, data]) => (
                      <div key={platform} className="flex justify-between items-center mb-2">
                        <span className="text-gray-400 capitalize">{platform}</span>
                        <div className="text-white">
                          {data.jobs} jobs • {data.content} items
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>

                <Card className="bg-white/5 border-white/10">
                  <CardHeader>
                    <CardTitle className="text-white">Top Sources</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {stats?.topSources.map((source, idx) => (
                      <div key={idx} className="flex justify-between items-center mb-2">
                        <div>
                          <span className="text-white">{source.name}</span>
                          <Badge variant="outline" className={`ml-2 ${getPlatformColor(source.platform)}`}>
                            {source.platform}
                          </Badge>
                        </div>
                        <span className="text-gray-400">{source.content} items</span>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Content Detail Dialog */}
      <Dialog open={showContentDialog} onOpenChange={setShowContentDialog}>
        <DialogContent className="bg-black border-white/20 max-w-4xl">
          <DialogHeader>
            <DialogTitle className="text-white">Content Details</DialogTitle>
          </DialogHeader>
          {selectedContent && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-gray-400">Platform</Label>
                  <Badge variant="outline" className={getPlatformColor(selectedContent.platform)}>
                    {selectedContent.platform}
                  </Badge>
                </div>
                <div>
                  <Label className="text-gray-400">Author</Label>
                  <div className="text-white">{selectedContent.author}</div>
                </div>
              </div>
              
              <div>
                <Label className="text-gray-400">Content</Label>
                <div className="bg-white/5 p-4 rounded-lg text-white">
                  {selectedContent.text}
                </div>
              </div>
              
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <Label className="text-gray-400">Likes</Label>
                  <div className="text-white">{selectedContent.engagement.likes}</div>
                </div>
                <div>
                  <Label className="text-gray-400">Comments</Label>
                  <div className="text-white">{selectedContent.engagement.comments}</div>
                </div>
                <div>
                  <Label className="text-gray-400">Shares</Label>
                  <div className="text-white">{selectedContent.engagement.shares}</div>
                </div>
              </div>
              
              <div>
                <Label className="text-gray-400">Keyword Matches</Label>
                <div className="flex flex-wrap gap-2 mt-2">
                  {selectedContent.keywordMatches.map((keyword: string, idx: number) => (
                    <Badge key={idx} variant="outline" className="text-purple-400 border-purple-400/50">
                      {keyword}
                    </Badge>
                  ))}
                </div>
              </div>
              
              {selectedContent.mediaUrls.length > 0 && (
                <div>
                  <Label className="text-gray-400">Media</Label>
                  <div className="text-sm text-gray-400">
                    {selectedContent.mediaUrls.length} media files attached
                  </div>
                </div>
              )}
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowContentDialog(false)}>
              Close
            </Button>
            {selectedContent?.url && (
              <Button onClick={() => window.open(selectedContent.url, '_blank')}>
                <ExternalLink className="h-4 w-4 mr-2" />
                View Original
              </Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation */}
      <AlertDialog open={!!deleteTarget} onOpenChange={(open) => !open && setDeleteTarget(null)}>
        <AlertDialogContent className="bg-black border-white/20">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-white">Delete scraped content?</AlertDialogTitle>
            <AlertDialogDescription className="text-gray-400">
              This action cannot be undone. This will permanently delete the selected content item.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={() => deleteTarget && handleDeleteContent(deleteTarget.id)}>
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
