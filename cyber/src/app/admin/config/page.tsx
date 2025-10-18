'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { Textarea } from '@/components/ui/textarea'
import { 
  Settings, 
  Server, 
  Key, 
  Database,
  AlertTriangle,
  Clock,
  Save,
  TestTube,
  CheckCircle,
  XCircle
} from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

interface APIConnection {
  id: string
  name: string
  status: 'connected' | 'disconnected' | 'error'
  endpoint: string
  lastChecked: string
}

interface ScrapingSettings {
  telegramEnabled: boolean
  instagramEnabled: boolean
  whatsappEnabled: boolean
  frequency: number // minutes
  maxPostsPerRun: number
}

interface KeywordSettings {
  keywords: string[]
  slangTerms: string[]
  emojiPatterns: string[]
}

export default function SystemConfiguration() {
  const { toast } = useToast()
  const [apiConnections, setApiConnections] = useState<APIConnection[]>([
    {
      id: 'telegram',
      name: 'Telegram API',
      status: 'connected',
      endpoint: 'api.telegram.org',
      lastChecked: '2024-01-15 10:30'
    },
    {
      id: 'instagram',
      name: 'Instagram Basic Display API',
      status: 'disconnected',
      endpoint: 'graph.instagram.com',
      lastChecked: '2024-01-14 16:20'
    },
    {
      id: 'sherlock',
      name: 'Sherlock OSINT',
      status: 'connected',
      endpoint: 'localhost:8001',
      lastChecked: '2024-01-15 09:45'
    },
    {
      id: 'spiderfoot',
      name: 'SpiderFoot',
      status: 'error',
      endpoint: 'localhost:5001',
      lastChecked: '2024-01-15 08:15'
    }
  ])

  const [scrapingSettings, setScrapingSettings] = useState<ScrapingSettings>({
    telegramEnabled: true,
    instagramEnabled: false,
    whatsappEnabled: true,
    frequency: 30,
    maxPostsPerRun: 1000
  })

  const [keywordSettings, setKeywordSettings] = useState<KeywordSettings>({
    keywords: ['drugs', 'narcotics', 'cocaine', 'heroin', 'cannabis', 'trafficking'],
    slangTerms: ['snow', 'ice', 'grass', 'blow', 'candy', 'rock'],
    emojiPatterns: ['💊', '🌿', '❄️', '💰', '🚫', '⚡']
  })

  const [apiKeys, setApiKeys] = useState({
    telegramBotToken: '****-****-****',
    instagramAppId: '****-****-****',
    instagramAppSecret: '****-****-****'
  })

  const testConnection = async (connectionId: string) => {
    try {
      setApiConnections(prev => prev.map(conn => 
        conn.id === connectionId 
          ? { ...conn, status: 'connected', lastChecked: new Date().toLocaleString() }
          : conn
      ))
      
      toast({
        title: 'Connection Test',
        description: `${connectionId} connection successful`
      })
    } catch (error) {
      setApiConnections(prev => prev.map(conn => 
        conn.id === connectionId 
          ? { ...conn, status: 'error', lastChecked: new Date().toLocaleString() }
          : conn
      ))
      
      toast({
        title: 'Connection Failed',
        description: `Failed to connect to ${connectionId}`,
        variant: 'destructive'
      })
    }
  }

  const saveConfiguration = async () => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      toast({
        title: 'Configuration Saved',
        description: 'System configuration has been updated successfully'
      })
    } catch (error) {
      toast({
        title: 'Save Failed',
        description: 'Failed to save configuration',
        variant: 'destructive'
      })
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'connected':
        return <CheckCircle className="h-4 w-4 text-green-400" />
      case 'disconnected':
        return <XCircle className="h-4 w-4 text-gray-400" />
      case 'error':
        return <AlertTriangle className="h-4 w-4 text-red-400" />
      default:
        return <XCircle className="h-4 w-4 text-gray-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected':
        return 'text-green-400 border-green-400/50'
      case 'disconnected':
        return 'text-gray-400 border-gray-400/50'
      case 'error':
        return 'text-red-400 border-red-400/50'
      default:
        return 'text-gray-400 border-gray-400/50'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">System Configuration</h1>
          <p className="text-gray-400">Manage API connections, keywords, and system settings</p>
        </div>
        
        <Button onClick={saveConfiguration} className="bg-blue-500 hover:bg-blue-600">
          <Save className="h-4 w-4 mr-2" />
          Save Configuration
        </Button>
      </div>

      {/* API Connections */}
      <Card className="bg-white/5 border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Server className="h-5 w-5" />
            API Connections
          </CardTitle>
          <CardDescription className="text-gray-400">
            Configure and test external API connections
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {apiConnections.map((connection) => (
            <div key={connection.id} className="flex items-center justify-between p-4 rounded-lg bg-white/5 border border-white/10">
              <div className="flex items-center gap-4">
                {getStatusIcon(connection.status)}
                <div>
                  <h3 className="font-medium text-white">{connection.name}</h3>
                  <p className="text-sm text-gray-400">{connection.endpoint}</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <Badge variant="outline" className={getStatusColor(connection.status)}>
                    {connection.status}
                  </Badge>
                  <p className="text-xs text-gray-500 mt-1">Last: {connection.lastChecked}</p>
                </div>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => testConnection(connection.id)}
                >
                  <TestTube className="h-4 w-4 mr-2" />
                  Test
                </Button>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* API Keys */}
      <Card className="bg-white/5 border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Key className="h-5 w-5" />
            API Keys & Credentials
          </CardTitle>
          <CardDescription className="text-gray-400">
            Manage API keys and authentication credentials
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="telegram-token" className="text-white">Telegram Bot Token</Label>
              <Input
                id="telegram-token"
                type="password"
                value={apiKeys.telegramBotToken}
                onChange={(e) => setApiKeys(prev => ({ ...prev, telegramBotToken: e.target.value }))}
                className="bg-white/10 border-white/20 text-white"
                placeholder="Enter Telegram bot token"
              />
            </div>
            <div>
              <Label htmlFor="instagram-app-id" className="text-white">Instagram App ID</Label>
              <Input
                id="instagram-app-id"
                type="password"
                value={apiKeys.instagramAppId}
                onChange={(e) => setApiKeys(prev => ({ ...prev, instagramAppId: e.target.value }))}
                className="bg-white/10 border-white/20 text-white"
                placeholder="Enter Instagram app ID"
              />
            </div>
            <div>
              <Label htmlFor="instagram-app-secret" className="text-white">Instagram App Secret</Label>
              <Input
                id="instagram-app-secret"
                type="password"
                value={apiKeys.instagramAppSecret}
                onChange={(e) => setApiKeys(prev => ({ ...prev, instagramAppSecret: e.target.value }))}
                className="bg-white/10 border-white/20 text-white"
                placeholder="Enter Instagram app secret"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Scraping Configuration */}
      <Card className="bg-white/5 border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Scraping Schedule & Settings
          </CardTitle>
          <CardDescription className="text-gray-400">
            Configure data collection frequency and limits
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center justify-between p-4 rounded-lg bg-white/5 border border-white/10">
              <div>
                <Label htmlFor="telegram-scraping" className="text-white">Telegram Scraping</Label>
                <p className="text-sm text-gray-400">Collect Telegram data</p>
              </div>
              <Switch
                id="telegram-scraping"
                checked={scrapingSettings.telegramEnabled}
                onCheckedChange={(checked) => setScrapingSettings(prev => ({ ...prev, telegramEnabled: checked }))}
              />
            </div>
            
            <div className="flex items-center justify-between p-4 rounded-lg bg-white/5 border border-white/10">
              <div>
                <Label htmlFor="instagram-scraping" className="text-white">Instagram Scraping</Label>
                <p className="text-sm text-gray-400">Collect Instagram data</p>
              </div>
              <Switch
                id="instagram-scraping"
                checked={scrapingSettings.instagramEnabled}
                onCheckedChange={(checked) => setScrapingSettings(prev => ({ ...prev, instagramEnabled: checked }))}
              />
            </div>

            <div className="flex items-center justify-between p-4 rounded-lg bg-white/5 border border-white/10">
              <div>
                <Label htmlFor="whatsapp-scraping" className="text-white">WhatsApp Monitoring</Label>
                <p className="text-sm text-gray-400">Monitor WhatsApp groups</p>
              </div>
              <Switch
                id="whatsapp-scraping"
                checked={scrapingSettings.whatsappEnabled}
                onCheckedChange={(checked) => setScrapingSettings(prev => ({ ...prev, whatsappEnabled: checked }))}
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="frequency" className="text-white">Scraping Frequency (minutes)</Label>
              <Input
                id="frequency"
                type="number"
                value={scrapingSettings.frequency || ''}
                onChange={(e) => setScrapingSettings(prev => ({ ...prev, frequency: parseInt(e.target.value) || 30 }))}
                className="bg-white/10 border-white/20 text-white"
                min="5"
                max="1440"
              />
            </div>
            <div>
              <Label htmlFor="max-posts" className="text-white">Max Posts Per Run</Label>
              <Input
                id="max-posts"
                type="number"
                value={scrapingSettings.maxPostsPerRun || ''}
                onChange={(e) => setScrapingSettings(prev => ({ ...prev, maxPostsPerRun: parseInt(e.target.value) || 1000 }))}
                className="bg-white/10 border-white/20 text-white"
                min="100"
                max="10000"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Keywords & Detection Rules */}
      <Card className="bg-white/5 border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <AlertTriangle className="h-5 w-5" />
            Keywords & Detection Rules
          </CardTitle>
          <CardDescription className="text-gray-400">
            Configure detection keywords, slang terms, and emoji patterns
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label htmlFor="keywords" className="text-white">Keywords</Label>
              <Textarea
                id="keywords"
                value={keywordSettings.keywords.join(', ')}
                onChange={(e) => setKeywordSettings(prev => ({ ...prev, keywords: e.target.value.split(', ').filter(k => k.trim()) }))}
                className="bg-white/10 border-white/20 text-white"
                placeholder="Enter keywords separated by commas"
                rows={4}
              />
              <p className="text-xs text-gray-500 mt-1">{keywordSettings.keywords.length} keywords</p>
            </div>

            <div>
              <Label htmlFor="slang" className="text-white">Slang Terms</Label>
              <Textarea
                id="slang"
                value={keywordSettings.slangTerms.join(', ')}
                onChange={(e) => setKeywordSettings(prev => ({ ...prev, slangTerms: e.target.value.split(', ').filter(k => k.trim()) }))}
                className="bg-white/10 border-white/20 text-white"
                placeholder="Enter slang terms separated by commas"
                rows={4}
              />
              <p className="text-xs text-gray-500 mt-1">{keywordSettings.slangTerms.length} terms</p>
            </div>

            <div>
              <Label htmlFor="emojis" className="text-white">Emoji Patterns</Label>
              <Textarea
                id="emojis"
                value={keywordSettings.emojiPatterns.join(', ')}
                onChange={(e) => setKeywordSettings(prev => ({ ...prev, emojiPatterns: e.target.value.split(', ').filter(k => k.trim()) }))}
                className="bg-white/10 border-white/20 text-white"
                placeholder="Enter emojis separated by commas"
                rows={4}
              />
              <p className="text-xs text-gray-500 mt-1">{keywordSettings.emojiPatterns.length} patterns</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}