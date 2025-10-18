'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Loader2, Search, ExternalLink, Shield, AlertTriangle, Users, Clock } from 'lucide-react';

interface OSINTResult {
  username: string;
  platform: string;
  linkedProfiles: Array<string | {
    platform: string;
    url: string;
    status?: string;
    verified?: boolean;
    source?: string;
  }>;
  email?: string;
  riskLevel: 'Low' | 'Medium' | 'High' | 'Critical';
  summary: string;
  toolsUsed: string[];
  totalProfilesFound: number;
  confidenceLevel: 'low' | 'medium' | 'high';
  timestamp: string;
  rawResults?: any;
}

interface ToolStatus {
  sherlock: { installed: boolean; path: string };
  spiderfoot: { installed: boolean; path: string };
}

export function UserInvestigationDashboard() {
  const [username, setUsername] = useState('');
  const [platform, setPlatform] = useState('Telegram');
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<OSINTResult | null>(null);
  const [toolStatus, setToolStatus] = useState<ToolStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [backendStatus, setBackendStatus] = useState<'checking' | 'connected' | 'error'>('checking');

  // Check backend connectivity on page load
  useEffect(() => {
    const checkBackendConnection = async () => {
      try {
        const data = await apiClient.healthCheck();
        setBackendStatus(data?.database_connected ? 'connected' : 'error');
        if (data?.database_connected) {
          checkToolStatus();
        }
      } catch (err) {
        console.error('Backend connection failed:', err);
        setBackendStatus('error');
      }
    };
    
    checkBackendConnection();
  }, []);

  const checkBackendConnection = async () => {
    try {
      setBackendStatus('checking');
      const data = await apiClient.healthCheck();
      setBackendStatus(data?.database_connected ? 'connected' : 'error');
      if (data?.database_connected) {
        checkToolStatus();
      }
    } catch (err) {
      console.error('Backend connection failed:', err);
      setBackendStatus('error');
    }
  };

  const checkToolStatus = async () => {
    try {
      const data = await apiClient.getOsintToolsStatus();
      if (data?.status === 'success') {
        setToolStatus(data.tools);
      }
    } catch (err) {
      console.error('Failed to check tool status:', err);
    }
  };

  const runInvestigation = async () => {
    if (!username.trim()) {
      setError('Please enter a username');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      console.log(`🔍 Starting investigation for user: ${username.trim()} on ${platform}`);
      const data = await apiClient.investigateUser(username.trim(), platform);
      
      if (data?.status === 'success') {
        setResults(data.data);
        console.log('✅ Investigation completed successfully');
      } else {
        const errorMsg = data?.message || 'Investigation failed';
        setError(errorMsg);
        console.error('❌ Investigation failed:', errorMsg);
      }
    } catch (err: any) {
      console.error('Investigation error:', err);
      
      // Provide more specific error messages
      let errorMessage = 'Investigation failed';
      
      if (err.message?.includes('timeout') || err.message?.includes('aborted')) {
        errorMessage = 'Investigation is taking longer than expected. This may indicate:\n' +
                     '• OSINT tools are running but taking time to complete\n' +
                     '• Backend server is processing the request\n' +
                     '• Network connectivity issues\n\n' +
                     'Please check if the Flask backend is running and try again.';
      } else if (err.message?.includes('Failed to fetch') || err.message?.includes('CORS')) {
        errorMessage = 'Cannot connect to the backend server. Please ensure:\n' +
                     '• Flask server is running on http://localhost:5000\n' +
                     '• OSINT tools (Sherlock, Spiderfoot) are properly installed\n' +
                     '• No firewall is blocking the connection';
      } else if (err.message?.includes('500')) {
        errorMessage = 'Server error occurred during investigation. This may be due to:\n' +
                     '• Missing OSINT tools installation\n' +
                     '• Server configuration issues\n' +
                     '• Database connectivity problems';
      }
      
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">User Investigation Dashboard</h1>
          <p className="text-muted-foreground">
            Investigate usernames using real OSINT tools (Sherlock & Spiderfoot)
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button onClick={checkToolStatus} variant="outline" disabled={backendStatus !== 'connected'}>
            Check Tool Status
          </Button>
        </div>
      </div>

      {/* Backend Connection Warning */}
      {backendStatus === 'error' && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            Cannot connect to Flask backend server (http://localhost:5000). 
            Please make sure the Flask server is running by executing: <code>python run.py</code> in the flask_backend directory.
          </AlertDescription>
        </Alert>
      )}

      {/* Tool Status */}
      {toolStatus && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              OSINT Tools Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center justify-between">
                <span>Sherlock</span>
                <Badge variant={toolStatus.sherlock?.installed ? "default" : "destructive"}>
                  {toolStatus.sherlock?.installed ? "Installed" : "Not Found"}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span>Spiderfoot</span>
                <Badge variant={toolStatus.spiderfoot?.installed ? "default" : "destructive"}>
                  {toolStatus.spiderfoot?.installed ? "Installed" : "Not Found"}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Investigation Form */}
      <Card>
        <CardHeader>
          <CardTitle>Start Investigation</CardTitle>
          <CardDescription>
            Enter a username to investigate across multiple platforms
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                placeholder="Enter username to investigate"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && runInvestigation()}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="platform">Original Platform</Label>
              <Select value={platform} onValueChange={setPlatform}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select platform" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Telegram">Telegram</SelectItem>
                  <SelectItem value="WhatsApp">WhatsApp</SelectItem>
                  <SelectItem value="Instagram">Instagram</SelectItem>
                  <SelectItem value="Unknown">Unknown</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          
          <Button 
            onClick={runInvestigation} 
            disabled={isLoading || !username.trim()}
            className="w-full"
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Investigating... (This may take up to 1 minute)
              </>
            ) : (
              <>
                <Search className="mr-2 h-4 w-4" />
                Start Investigation
              </>
            )}
          </Button>

          {error && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                <div className="whitespace-pre-line">{error}</div>
              </AlertDescription>
            </Alert>
          )}
          
          {isLoading && (
            <Alert>
              <Clock className="h-4 w-4" />
              <AlertDescription>
                <div className="space-y-2">
                  <p><strong>Investigation in progress...</strong></p>
                  <p>The system is running OSINT tools to search for user profiles across multiple platforms. This process may take up to 1 minute depending on:</p>
                  <ul className="list-disc list-inside space-y-1 text-sm">
                    <li>Number of platforms being searched</li>
                    <li>Network response times</li>
                    <li>OSINT tool availability and performance</li>
                  </ul>
                  <p className="text-sm text-muted-foreground">Please be patient and do not refresh the page.</p>
                </div>
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Results */}
      {results && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                Investigation Results for "{results.username}"
                <div className="flex gap-2">
                  <Badge variant="outline">{results.riskLevel} Risk</Badge>
                  <Badge variant="outline">{results.confidenceLevel} Confidence</Badge>
                </div>
              </CardTitle>
              <CardDescription>
                Found {results.totalProfilesFound} potential profiles for username '{results.username}'
              </CardDescription>
            </CardHeader>
          </Card>

          <Tabs defaultValue="profiles" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="profiles">Linked Profiles</TabsTrigger>
              <TabsTrigger value="details">Investigation Details</TabsTrigger>
              <TabsTrigger value="raw">Raw Results</TabsTrigger>
            </TabsList>

            <TabsContent value="profiles" className="space-y-4">
              {/* Group profiles by source */}
              {(() => {
                const profilesBySource: Record<string, any[]> = {};
                results.linkedProfiles?.forEach((profile: any) => {
                  const source = profile.source || 'unknown';
                  if (!profilesBySource[source]) {
                    profilesBySource[source] = [];
                  }
                  profilesBySource[source].push(profile);
                });

                const sourceLabels: Record<string, { name: string; icon: string; color: string }> = {
                  spiderfoot: { name: 'Spiderfoot (Comprehensive OSINT)', icon: '🕷️', color: 'text-purple-600' },
                  sherlock: { name: 'Sherlock (Social Media)', icon: '🔍', color: 'text-blue-600' },
                  url_check: { name: 'URL Checker (Fast Check)', icon: '🌐', color: 'text-green-600' },
                };

                return Object.keys(profilesBySource).length > 0 ? (
                  <div className="space-y-4">
                    {Object.entries(profilesBySource).map(([source, profiles]) => {
                      const sourceInfo = sourceLabels[source] || { name: source, icon: '📋', color: 'text-gray-600' };
                      return (
                        <Card key={source}>
                          <CardHeader>
                            <CardTitle className={`flex items-center gap-2 ${sourceInfo.color}`}>
                              <span>{sourceInfo.icon}</span>
                              <span>{sourceInfo.name}</span>
                              <Badge variant="secondary">{profiles.length} profiles</Badge>
                            </CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-2">
                              {profiles.map((profile, index) => {
                                let platform = 'Unknown';
                                let url = '';
                                let confidence = profile.confidence || 'medium';
                                
                                try {
                                  if (typeof profile === 'string') {
                                    const parts = profile.split(':', 2);
                                    platform = parts[0] || 'Unknown';
                                    url = parts[1] || '';
                                  } else if (profile && typeof profile === 'object') {
                                    platform = profile.platform || 'Unknown';
                                    url = profile.url || '';
                                  }
                                } catch (e) {
                                  console.error('Error parsing profile:', profile, e);
                                  platform = 'Unknown';
                                  url = '';
                                }
                                
                                return (
                                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50 transition-colors">
                                    <div className="flex-1">
                                      <div className="flex items-center gap-2">
                                        <span className="font-medium">{platform}</span>
                                        {source === 'spiderfoot' && (
                                          <Badge variant="outline" className="text-xs">
                                            {confidence} confidence
                                          </Badge>
                                        )}
                                      </div>
                                      {url && (
                                        <p className="text-sm text-muted-foreground truncate max-w-md mt-1">
                                          {url}
                                        </p>
                                      )}
                                    </div>
                                    {url && (
                                      <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={() => window.open(url, '_blank')}
                                      >
                                        <ExternalLink className="h-4 w-4" />
                                      </Button>
                                    )}
                                  </div>
                                );
                              })}
                            </div>
                          </CardContent>
                        </Card>
                      );
                    })}
                  </div>
                ) : (
                  <Card>
                    <CardContent className="py-8">
                      <p className="text-muted-foreground text-center">No linked profiles found</p>
                    </CardContent>
                  </Card>
                );
              })()}
            </TabsContent>

            <TabsContent value="details" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Investigation Summary</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>Total Profiles Found:</span>
                      <span className="font-semibold">{results.totalProfilesFound}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Tools Used:</span>
                      <span className="font-semibold">{results.toolsUsed?.join(', ') || 'None'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Risk Level:</span>
                      <span className="font-semibold">{results.riskLevel}</span>
                    </div>
                    {results.email && (
                      <div className="flex justify-between">
                        <span>Email Found:</span>
                        <span className="font-semibold">{results.email}</span>
                      </div>
                    )}
                  </div>
                  
                  {results.summary && (
                    <div className="mt-4">
                      <h4 className="font-semibold mb-2">Summary</h4>
                      <p className="text-sm text-muted-foreground">{results.summary}</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Tool-specific results breakdown */}
              <Card>
                <CardHeader>
                  <CardTitle>Results by Tool</CardTitle>
                  <CardDescription>Detailed breakdown of findings from each OSINT tool</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Spiderfoot Results */}
                  {results.rawResults?.spiderfoot_results && (
                    <div className="border-l-4 border-purple-500 pl-4 py-2">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-2xl">🕷️</span>
                        <h4 className="font-semibold text-purple-600">Spiderfoot</h4>
                      </div>
                      <div className="space-y-1 text-sm">
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Status:</span>
                          <Badge variant={results.rawResults.spiderfoot_results.status === 'completed' ? 'default' : 'destructive'}>
                            {results.rawResults.spiderfoot_results.status || 'unknown'}
                          </Badge>
                        </div>
                        {results.rawResults.spiderfoot_results.findings && (
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Findings:</span>
                            <span className="font-medium">{results.rawResults.spiderfoot_results.findings.length}</span>
                          </div>
                        )}
                        {results.rawResults.spiderfoot_results.error && (
                          <div className="text-xs text-red-600 mt-1">
                            Error: {results.rawResults.spiderfoot_results.error}
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Sherlock Results */}
                  {results.rawResults?.sherlock_results && (
                    <div className="border-l-4 border-blue-500 pl-4 py-2">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-2xl">🔍</span>
                        <h4 className="font-semibold text-blue-600">Sherlock</h4>
                      </div>
                      <div className="space-y-1 text-sm">
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Status:</span>
                          <Badge variant={results.rawResults.sherlock_results.status === 'success' ? 'default' : 'destructive'}>
                            {results.rawResults.sherlock_results.status || 'unknown'}
                          </Badge>
                        </div>
                        {results.rawResults.sherlock_results.found_profiles && (
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Profiles Found:</span>
                            <span className="font-medium">{results.rawResults.sherlock_results.found_profiles.length}</span>
                          </div>
                        )}
                        {results.rawResults.sherlock_results.message && results.rawResults.sherlock_results.status === 'error' && (
                          <div className="text-xs text-red-600 mt-1">
                            Error: {results.rawResults.sherlock_results.message}
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Fallback API Results */}
                  {results.rawResults?.fallback_results && (
                    <div className="border-l-4 border-green-500 pl-4 py-2">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-2xl">🌐</span>
                        <h4 className="font-semibold text-green-600">URL Checker</h4>
                      </div>
                      <div className="space-y-1 text-sm">
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Status:</span>
                          <Badge variant={results.rawResults.fallback_results.status === 'success' ? 'default' : 'destructive'}>
                            {results.rawResults.fallback_results.status || 'unknown'}
                          </Badge>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Profiles Found:</span>
                          <span className="font-medium">{results.rawResults.fallback_results.total_found || 0}</span>
                        </div>
                        <div className="text-xs text-muted-foreground mt-1">
                          Method: {results.rawResults.fallback_results.method || 'URL pattern checking'}
                        </div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="raw" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Raw Investigation Data</CardTitle>
                  <CardDescription>
                    Complete output from OSINT tools for debugging
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <pre className="bg-muted p-4 rounded-lg overflow-auto text-xs max-h-96">
                    {JSON.stringify(results.rawResults || results, null, 2)}
                  </pre>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      )}
    </div>
  );
}

