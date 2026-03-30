'use client'

import { useState, useEffect } from 'react'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import apiClient from '@/lib/api'
import { toast } from '@/hooks/use-toast'
import { 
  Search, 
  Filter, 
  Link, 
  ExternalLink, 
  Calendar, 
  User, 
  Tag,
  CheckCircle,
  X,
  RefreshCw,
  FileText,
  Image,
  Video,
  MessageSquare
} from 'lucide-react'
import { format } from 'date-fns'
import { LinkContentConfirmationDialog } from '@/components/ui/confirmation-dialog'

interface ScrapedContent {
  id: string
  jobId?: string
  platform: string
  author: string
  text: string
  url?: string
  mediaUrls?: string[]
  timestamp: string
  scrapedAt?: string
  keywordMatches: string[]
  sentiment?: number
  engagement?: {
    likes: number
    comments: number
    shares: number
  }
  processed?: boolean
  flagged: boolean
  // Content analysis endpoint fields
  source_handle?: string
  posted_at?: string
  risk_level?: string
  status?: string
  analysis_summary?: string
  is_analyzed?: boolean
  suspicion_score?: number
  intent?: string
}

interface LinkContentDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  caseId: number
  caseTitle: string
  onContentLinked: () => void
}

export default function LinkContentDialog({ 
  open, 
  onOpenChange, 
  caseId, 
  caseTitle, 
  onContentLinked 
}: LinkContentDialogProps) {
  const [content, setContent] = useState<ScrapedContent[]>([])
  const [filteredContent, setFilteredContent] = useState<ScrapedContent[]>([])
  const [selectedContent, setSelectedContent] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [linking, setLinking] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [platformFilter, setPlatformFilter] = useState('all')
  const [dateFilter, setDateFilter] = useState('all')
  const [keywordFilter, setKeywordFilter] = useState('')
  const [showLinkConfirmation, setShowLinkConfirmation] = useState(false)

  // Fetch scraped content
  const fetchContent = async () => {
    try {
      setLoading(true)
      
      // Try the content analysis endpoint first (available to all authenticated users)
      let response
      try {
        response = await apiClient.getContentAnalysisScrapedContent({ limit: 100 })
      } catch (error) {
        console.log('Content analysis endpoint failed, trying scraping endpoint...')
        // Fallback to scraping endpoint (requires Admin role)
        response = await apiClient.getScrapedContent({ limit: 100 })
      }
      
      if (response && Array.isArray(response)) {
        setContent(response)
        setFilteredContent(response)
      } else if (response?.data && Array.isArray(response.data)) {
        setContent(response.data)
        setFilteredContent(response.data)
      } else {
        setContent([])
        setFilteredContent([])
      }
    } catch (error) {
      console.error('Error fetching content:', error)
      toast({
        title: "Error",
        description: "Failed to fetch scraped content. You may need Admin privileges to access this feature.",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  // Filter content based on search and filters
  useEffect(() => {
    let filtered = content

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(item => 
        getDisplayText(item).toLowerCase().includes(searchTerm.toLowerCase()) ||
        getDisplayAuthor(item).toLowerCase().includes(searchTerm.toLowerCase()) ||
        getDisplayKeywords(item).some(keyword => 
          keyword.toLowerCase().includes(searchTerm.toLowerCase())
        )
      )
    }

    // Platform filter
    if (platformFilter !== 'all') {
      filtered = filtered.filter(item => item.platform === platformFilter)
    }

    // Date filter
    if (dateFilter !== 'all') {
      const now = new Date()
      const daysAgo = parseInt(dateFilter)
      const cutoffDate = new Date(now.getTime() - (daysAgo * 24 * 60 * 60 * 1000))
      
      filtered = filtered.filter(item => {
        const timestamp = getDisplayTimestamp(item)
        return timestamp && new Date(timestamp) >= cutoffDate
      })
    }

    // Keyword filter
    if (keywordFilter) {
      filtered = filtered.filter(item => 
        getDisplayKeywords(item).some(keyword => 
          keyword.toLowerCase().includes(keywordFilter.toLowerCase())
        )
      )
    }

    setFilteredContent(filtered)
  }, [content, searchTerm, platformFilter, dateFilter, keywordFilter])

  useEffect(() => {
    if (open) {
      fetchContent()
      setSelectedContent([])
    }
  }, [open])

  const handleContentSelect = (contentId: string) => {
    setSelectedContent(prev => 
      prev.includes(contentId) 
        ? prev.filter(id => id !== contentId)
        : [...prev, contentId]
    )
  }

  const handleSelectAll = () => {
    if (selectedContent.length === filteredContent.length) {
      setSelectedContent([])
    } else {
      setSelectedContent(filteredContent.map(item => item.id))
    }
  }

  const handleLinkContent = () => {
    if (selectedContent.length === 0) {
      toast({
        title: "No Content Selected",
        description: "Please select content to link to the case",
        variant: "destructive"
      })
      return
    }
    setShowLinkConfirmation(true)
  }

  const confirmLinkContent = async () => {
    try {
      setLinking(true)
      const contentIds = selectedContent.map(id => parseInt(id))
      
      await apiClient.linkContentToCase(caseId, contentIds)
      
      toast({
        title: "Content Linked Successfully",
        description: `${selectedContent.length} content items linked to case "${caseTitle}"`,
        variant: "default"
      })
      
      onContentLinked()
      onOpenChange(false)
      setSelectedContent([])
      setShowLinkConfirmation(false)
    } catch (error) {
      console.error('Error linking content:', error)
      toast({
        title: "Error",
        description: "Failed to link content to case",
        variant: "destructive"
      })
    } finally {
      setLinking(false)
    }
  }

  const getPlatformIcon = (platform: string) => {
    switch (platform.toLowerCase()) {
      case 'telegram':
        return <MessageSquare className="w-4 h-4" />
      case 'instagram':
        return <Image className="w-4 h-4" />
      case 'youtube':
        return <Video className="w-4 h-4" />
      default:
        return <FileText className="w-4 h-4" />
    }
  }

  const getSentimentColor = (sentiment?: number) => {
    if (!sentiment) return 'text-gray-600'
    if (sentiment > 0.1) return 'text-green-600'
    if (sentiment < -0.1) return 'text-red-600'
    return 'text-gray-600'
  }

  const getSentimentText = (sentiment?: number) => {
    if (!sentiment) return 'Unknown'
    if (sentiment > 0.1) return 'Positive'
    if (sentiment < -0.1) return 'Negative'
    return 'Neutral'
  }

  const getDisplayTimestamp = (item: ScrapedContent) => {
    return item.posted_at || item.timestamp || item.scrapedAt || ''
  }

  const getDisplayAuthor = (item: ScrapedContent) => {
    return item.source_handle || item.author || 'Unknown'
  }

  const getDisplayText = (item: ScrapedContent) => {
    return item.text || ''
  }

  const getDisplayKeywords = (item: ScrapedContent) => {
    return item.keywordMatches || item.keywords || []
  }

  const getDisplayEngagement = (item: ScrapedContent) => {
    return item.engagement || { likes: 0, comments: 0, shares: 0 }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto glassmorphism border-white/10">
        <DialogHeader>
          <DialogTitle className="text-foreground flex items-center gap-2">
            <Link className="h-5 w-5 text-primary" />
            Link Content to Case
          </DialogTitle>
          <DialogDescription className="text-muted-foreground">
            Select scraped content to link to case "{caseTitle}"
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Filters */}
          <Card className="glassmorphism">
            <CardHeader>
              <CardTitle className="text-lg font-semibold text-foreground flex items-center">
                <Filter className="h-5 w-5 mr-2 text-primary" />
                Search & Filter Content
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-4">
                <div className="flex-1 min-w-[200px]">
                  <Label htmlFor="search" className="text-muted-foreground">Search Content</Label>
                  <div className="relative">
                    <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="search"
                      placeholder="Search content..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10 bg-background/50 border-white/10 text-foreground placeholder-muted-foreground focus:border-primary"
                    />
                  </div>
                </div>

                <div className="min-w-[150px]">
                  <Label htmlFor="platform" className="text-muted-foreground">Platform</Label>
                  <Select value={platformFilter} onValueChange={setPlatformFilter}>
                    <SelectTrigger className="bg-background/50 border-white/10 text-foreground">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="glassmorphism border-white/10">
                      <SelectItem value="all" className="text-foreground hover:bg-white/5">All Platforms</SelectItem>
                      <SelectItem value="telegram" className="text-foreground hover:bg-white/5">Telegram</SelectItem>
                      <SelectItem value="instagram" className="text-foreground hover:bg-white/5">Instagram</SelectItem>
                      <SelectItem value="youtube" className="text-foreground hover:bg-white/5">YouTube</SelectItem>
                      <SelectItem value="twitter" className="text-foreground hover:bg-white/5">Twitter</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="min-w-[150px]">
                  <Label htmlFor="date" className="text-muted-foreground">Date Range</Label>
                  <Select value={dateFilter} onValueChange={setDateFilter}>
                    <SelectTrigger className="bg-background/50 border-white/10 text-foreground">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="glassmorphism border-white/10">
                      <SelectItem value="all" className="text-foreground hover:bg-white/5">All Time</SelectItem>
                      <SelectItem value="1" className="text-foreground hover:bg-white/5">Last 24 Hours</SelectItem>
                      <SelectItem value="7" className="text-foreground hover:bg-white/5">Last 7 Days</SelectItem>
                      <SelectItem value="30" className="text-foreground hover:bg-white/5">Last 30 Days</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="min-w-[150px]">
                  <Label htmlFor="keyword" className="text-muted-foreground">Keyword</Label>
                  <Input
                    id="keyword"
                    placeholder="Filter by keyword..."
                    value={keywordFilter}
                    onChange={(e) => setKeywordFilter(e.target.value)}
                    className="bg-background/50 border-white/10 text-foreground placeholder-muted-foreground focus:border-primary"
                  />
                </div>

                <div className="flex items-end">
                  <Button
                    variant="outline"
                    onClick={fetchContent}
                    disabled={loading}
                    className="h-10 glassmorphism border-white/10 text-foreground hover:bg-white/5"
                  >
                    <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                    Refresh
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Selection Summary */}
          {selectedContent.length > 0 && (
            <Card className="glassmorphism border-primary/20">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-primary" />
                    <span className="font-medium text-foreground">
                      {selectedContent.length} content item{selectedContent.length !== 1 ? 's' : ''} selected
                    </span>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setSelectedContent([])}
                    className="glassmorphism border-white/10 text-foreground hover:bg-white/5"
                  >
                    Clear Selection
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Content List */}
          <Card className="glassmorphism">
            <CardHeader>
              <CardTitle className="text-lg font-semibold text-foreground flex items-center">
                <FileText className="h-5 w-5 mr-2 text-primary" />
                Available Content ({filteredContent.length} items)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {loading ? (
                  <div className="flex items-center justify-center h-32">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                  </div>
                ) : filteredContent.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    No content found matching your criteria
                  </div>
                ) : (
                  <>
                    <div className="flex items-center justify-between p-3 glassmorphism rounded-lg">
                      <div className="flex items-center gap-2">
                        <Checkbox
                          checked={selectedContent.length === filteredContent.length && filteredContent.length > 0}
                          onCheckedChange={handleSelectAll}
                          className="border-white/20 data-[state=checked]:bg-primary data-[state=checked]:border-primary"
                        />
                        <span className="text-sm font-medium text-foreground">
                          Select All ({filteredContent.length} items)
                        </span>
                      </div>
                    </div>

                    {filteredContent.map((item) => (
                      <Card key={item.id} className={`cursor-pointer transition-colors glassmorphism ${
                        selectedContent.includes(item.id) ? 'ring-2 ring-primary bg-primary/10' : 'hover:bg-white/5'
                      }`}>
                        <CardContent className="p-4">
                          <div className="flex items-start gap-3">
                            <Checkbox
                              checked={selectedContent.includes(item.id)}
                              onCheckedChange={() => handleContentSelect(item.id)}
                              className="border-white/20 data-[state=checked]:bg-primary data-[state=checked]:border-primary"
                            />
                        
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex items-center gap-2">
                              {getPlatformIcon(item.platform)}
                              <Badge variant="outline" className="border-white/20 text-muted-foreground">{item.platform}</Badge>
                              <span className="text-sm text-foreground">@{getDisplayAuthor(item)}</span>
                              <span className="text-xs text-muted-foreground">
                                {getDisplayTimestamp(item) && format(new Date(getDisplayTimestamp(item)), 'MMM dd, yyyy HH:mm')}
                              </span>
                            </div>
                            
                            <div className="flex items-center gap-2">
                              <span className={`text-sm ${getSentimentColor(item.sentiment)}`}>
                                {getSentimentText(item.sentiment)}
                              </span>
                              {item.flagged && (
                                <Badge variant="destructive" className="text-xs bg-destructive/20 text-destructive border-destructive/30">Flagged</Badge>
                              )}
                              {item.risk_level && (
                                <Badge variant="outline" className="text-xs border-white/20 text-muted-foreground">
                                  Risk: {item.risk_level}
                                </Badge>
                              )}
                            </div>
                          </div>

                          <p className="text-sm mb-2 line-clamp-2 text-foreground">{getDisplayText(item)}</p>

                          {getDisplayKeywords(item).length > 0 && (
                            <div className="flex items-center gap-1 mb-2">
                              <Tag className="w-3 h-3 text-muted-foreground" />
                              <div className="flex flex-wrap gap-1">
                                {getDisplayKeywords(item).map((keyword, index) => (
                                  <Badge key={index} variant="secondary" className="text-xs bg-white/10 text-muted-foreground border-white/20">
                                    {keyword}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          )}

                          <div className="flex items-center gap-4 text-xs text-muted-foreground">
                            {getDisplayEngagement(item).likes > 0 && (
                              <div className="flex items-center gap-1">
                                <span>❤️ {getDisplayEngagement(item).likes}</span>
                              </div>
                            )}
                            {getDisplayEngagement(item).comments > 0 && (
                              <div className="flex items-center gap-1">
                                <span>💬 {getDisplayEngagement(item).comments}</span>
                              </div>
                            )}
                            {getDisplayEngagement(item).shares > 0 && (
                              <div className="flex items-center gap-1">
                                <span>🔄 {getDisplayEngagement(item).shares}</span>
                              </div>
                            )}
                            {item.url && (
                              <a 
                                href={item.url} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="flex items-center gap-1 text-primary hover:text-primary/80"
                              >
                                <ExternalLink className="w-3 h-3" />
                                View Original
                              </a>
                            )}
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
                  </>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Actions */}
          <div className="flex justify-end gap-2 pt-4 border-t border-white/10">
            <Button 
              variant="outline" 
              onClick={() => onOpenChange(false)}
              className="glassmorphism border-white/10 text-foreground hover:bg-white/5"
            >
              Cancel
            </Button>
            <Button 
              onClick={handleLinkContent} 
              disabled={selectedContent.length === 0 || linking}
              className="bg-primary hover:bg-primary/90 text-primary-foreground"
            >
              {linking ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-foreground mr-2"></div>
                  Linking...
                </>
              ) : (
                <>
                  <Link className="w-4 h-4 mr-2" />
                  Link {selectedContent.length} Content Item{selectedContent.length !== 1 ? 's' : ''}
                </>
              )}
            </Button>
          </div>
        </div>
      </DialogContent>

      {/* Link Content Confirmation Dialog */}
      <LinkContentConfirmationDialog
        open={showLinkConfirmation}
        onOpenChange={setShowLinkConfirmation}
        onConfirm={confirmLinkContent}
        itemCount={selectedContent.length}
        caseName={caseTitle}
        isLoading={linking}
      />
    </Dialog>
  )
}