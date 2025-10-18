"use client";

import * as React from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";
import { Bot, FileText, Instagram, Loader2, MessageSquare, Send, ShieldAlert, Database, Search, RefreshCw, CheckCircle, Clock, Filter } from "lucide-react";

import { apiClient } from "@/lib/api";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { RiskMeter } from "@/components/risk-meter";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "./ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Checkbox } from "@/components/ui/checkbox";

const contentFormSchema = z.object({
  platform: z.enum(["Instagram", "Telegram", "WhatsApp", "Facebook", "Twitter", "TikTok"]).optional(),
  username: z.string().optional(),
  content: z.string().min(10, { message: "Content must be at least 10 characters." }),
});

interface AnalysisResult {
  platform: string;
  username: string;
  text: string;
  matched_keywords: string[];
  intent: string;
  suspicion_score: number;
  is_flagged: boolean;
  confidence: number;
  analysis_data: {
    drug_matches: string[];
    selling_indicators: string[];
    buying_indicators: string[];
    payment_indicators: string[];
    location_indicators: string[];
    entities: [string, string][];
    intent_verbs: string[];
    sentiment: string;
    word_count: number;
    sentence_count: number;
  };
  content_id: number | null;
  processing_time: number;
  saved_to_database: boolean;
}

interface ScrapedContent {
  id: string;
  source_handle: string;
  platform: string;
  text: string;
  author: string;
  posted_at: string;
  risk_level: string;
  status: string;
  keywords?: string[];
  analysis_summary?: string;
  is_analyzed?: boolean;
}

interface ScrapedContentFilters {
  platform?: string;
  risk_level?: string;
  status?: string;
  search_term?: string;
  analyzed_only?: boolean;
}

export function ContentAnalysis() {
  const { toast } = useToast();
  
  const [isContentLoading, setIsContentLoading] = React.useState(false);
  const [analysisResult, setAnalysisResult] = React.useState<AnalysisResult | null>(null);
  const [saveContent, setSaveContent] = React.useState(false);
  
  // Scraped content state
  const [scrapedContent, setScrapedContent] = React.useState<ScrapedContent[]>([]);
  const [selectedContent, setSelectedContent] = React.useState<string[]>([]);
  const [isLoadingScrapedContent, setIsLoadingScrapedContent] = React.useState(false);
  const [isAnalyzingSelected, setIsAnalyzingSelected] = React.useState(false);
  const [filters, setFilters] = React.useState<ScrapedContentFilters>({});
  const [showFilters, setShowFilters] = React.useState(false);

  const contentForm = useForm<z.infer<typeof contentFormSchema>>({
    resolver: zodResolver(contentFormSchema),
    defaultValues: {
      content: "",
      username: "",
    },
  });

  async function onContentSubmit(values: z.infer<typeof contentFormSchema>) {
    setIsContentLoading(true);
    setAnalysisResult(null);

    try {
      const response = await apiClient.post('/api/content-analysis/analyze', {
        platform: values.platform || "Unknown",
        username: values.username || "Anonymous",
        content: values.content,
        save_to_database: saveContent,  // Use the save content checkbox state
      });

      // Check if response exists (apiClient returns data directly, not wrapped in .data)
      if (!response) {
        throw new Error('No response received from server');
      }

      if (response.status === 'success') {
        setAnalysisResult(response);
        
        toast({
          title: "Analysis Complete",
          description: `Content analyzed with ${response.suspicion_score}% suspicion score. ${response.saved_to_database ? 'Results saved to database.' : 'Results not saved to database.'}`,
        });
      } else {
        throw new Error(response.message || 'Analysis failed');
      }

    } catch (error: any) {
      console.error("Analysis failed:", error);
      
      let errorMessage = "An unexpected error occurred. Please try again later.";
      
      if (error.message) {
        errorMessage = error.message;
      } else if (error.data?.message) {
        errorMessage = error.data.message;
      } else if (error.status) {
        errorMessage = `Server error (${error.status}). Please check if the backend is running.`;
      } else if (error.message?.includes('Cannot connect to backend')) {
        errorMessage = error.message;
      } else if (error.message?.includes('Failed to fetch') || error.message?.includes('Network Error')) {
        errorMessage = "Network error. Please check your connection and ensure the backend server is running.";
      }
      
      toast({
        variant: "destructive",
        title: "Analysis Failed",
        description: errorMessage,
      });
    } finally {
      setIsContentLoading(false);
    }
  }

  // Load scraped content from the database
  const loadScrapedContent = async () => {
    setIsLoadingScrapedContent(true);
    try {
      const response = await apiClient.get('/api/content-analysis/scraped-content?limit=100');
      
      if (response && Array.isArray(response)) {
        setScrapedContent(response);
      } else {
        setScrapedContent([]);
      }
    } catch (error: any) {
      console.error("Failed to load scraped content:", error);
      toast({
        variant: "destructive",
        title: "Failed to Load Content",
        description: "Could not load scraped content. Please try again.",
      });
      setScrapedContent([]);
    } finally {
      setIsLoadingScrapedContent(false);
    }
  };

  // Save content after analysis
  const saveContentAfterAnalysis = async () => {
    if (!analysisResult) return;
    
    setIsContentLoading(true);
    try {
      const response = await apiClient.post('/api/content-analysis/analyze', {
        platform: analysisResult.platform,
        username: analysisResult.username,
        content: analysisResult.text,
        save_to_database: true,  // Save to database
      });

      if (response && response.status === 'success') {
        // Update the analysis result to show it's now saved
        setAnalysisResult({
          ...analysisResult,
          content_id: response.content_id,
          saved_to_database: true
        });
        
        toast({
          title: "Content Saved",
          description: "Content has been successfully saved to the database.",
        });
      } else {
        throw new Error(response?.message || 'Failed to save content');
      }
    } catch (error: any) {
      console.error("Failed to save content:", error);
      toast({
        variant: "destructive",
        title: "Save Failed",
        description: error.message || "Failed to save content. Please try again.",
      });
    } finally {
      setIsContentLoading(false);
    }
  };

  // Analyze selected scraped content
  const analyzeSelectedContent = async () => {
    if (selectedContent.length === 0) {
      toast({
        variant: "destructive",
        title: "No Content Selected",
        description: "Please select content to analyze.",
      });
      return;
    }

    setIsAnalyzingSelected(true);
    const results: AnalysisResult[] = [];
    const errors: string[] = [];

    try {
      for (const contentId of selectedContent) {
        try {
          const content = scrapedContent.find(c => c.id === contentId);
          if (!content) continue;

          const response = await apiClient.post('/api/content-analysis/analyze', {
            platform: content.platform || "Unknown",
            username: content.author || "Unknown",
            content: content.text,
            save_to_database: true,  // Save scraped content analysis
          });

          if (response && response.status === 'success') {
            results.push(response);
          } else {
            errors.push(`Failed to analyze content from ${content.author}`);
          }
        } catch (error: any) {
          errors.push(`Error analyzing content: ${error.message}`);
        }
      }

      if (results.length > 0) {
        toast({
          title: "Batch Analysis Complete",
          description: `Successfully analyzed ${results.length} content items.`,
        });
        
        // Show the last result in the results panel
        if (results.length > 0) {
          setAnalysisResult(results[results.length - 1]);
        }
      }

      if (errors.length > 0) {
        toast({
          variant: "destructive",
          title: "Some Analyses Failed",
          description: `${errors.length} content items failed to analyze.`,
        });
      }

    } catch (error: any) {
      console.error("Batch analysis failed:", error);
      toast({
        variant: "destructive",
        title: "Analysis Failed",
        description: "Failed to analyze selected content. Please try again.",
      });
    } finally {
      setIsAnalyzingSelected(false);
    }
  };

  // Filter scraped content based on current filters
  const filteredScrapedContent = React.useMemo(() => {
    return scrapedContent.filter(content => {
      if (filters.platform && content.platform !== filters.platform) return false;
      if (filters.risk_level && content.risk_level !== filters.risk_level) return false;
      if (filters.status && content.status !== filters.status) return false;
      if (filters.analyzed_only && !content.is_analyzed) return false;
      if (filters.search_term) {
        const searchLower = filters.search_term.toLowerCase();
        return (
          content.text.toLowerCase().includes(searchLower) ||
          content.author.toLowerCase().includes(searchLower) ||
          content.source_handle.toLowerCase().includes(searchLower)
        );
      }
      return true;
    });
  }, [scrapedContent, filters]);

  // Load scraped content on component mount
  React.useEffect(() => {
    loadScrapedContent();
  }, []);

  // Render scraped content list
  const renderScrapedContentList = () => {
    if (isLoadingScrapedContent) {
      return (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex items-center space-x-4 p-4 border rounded-lg">
              <Skeleton className="h-4 w-4" />
              <div className="space-y-2 flex-1">
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-3 w-1/2" />
              </div>
              <Skeleton className="h-6 w-16" />
            </div>
          ))}
        </div>
      );
    }

    if (filteredScrapedContent.length === 0) {
      return (
        <div className="text-center py-8">
          <Database className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2">No Scraped Content Found</h3>
          <p className="text-muted-foreground mb-4">
            {scrapedContent.length === 0 
              ? "No content has been scraped yet. Start scraping to analyze content."
              : "No content matches your current filters."
            }
          </p>
          <Button onClick={loadScrapedContent} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      );
    }

    return (
      <div className="space-y-4">
        {/* Filters */}
        {showFilters && (
          <Card className="p-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="text-sm font-medium">Platform</label>
                <Select value={filters.platform || ""} onValueChange={(value) => setFilters(prev => ({ ...prev, platform: value || undefined }))}>
                  <SelectTrigger>
                    <SelectValue placeholder="All platforms" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">All platforms</SelectItem>
                    <SelectItem value="Instagram">Instagram</SelectItem>
                    <SelectItem value="Telegram">Telegram</SelectItem>
                    <SelectItem value="WhatsApp">WhatsApp</SelectItem>
                    <SelectItem value="Facebook">Facebook</SelectItem>
                    <SelectItem value="Twitter">Twitter</SelectItem>
                    <SelectItem value="TikTok">TikTok</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-sm font-medium">Risk Level</label>
                <Select value={filters.risk_level || ""} onValueChange={(value) => setFilters(prev => ({ ...prev, risk_level: value || undefined }))}>
                  <SelectTrigger>
                    <SelectValue placeholder="All risk levels" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">All risk levels</SelectItem>
                    <SelectItem value="Low">Low</SelectItem>
                    <SelectItem value="Medium">Medium</SelectItem>
                    <SelectItem value="High">High</SelectItem>
                    <SelectItem value="Critical">Critical</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-sm font-medium">Status</label>
                <Select value={filters.status || ""} onValueChange={(value) => setFilters(prev => ({ ...prev, status: value || undefined }))}>
                  <SelectTrigger>
                    <SelectValue placeholder="All statuses" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">All statuses</SelectItem>
                    <SelectItem value="New">New</SelectItem>
                    <SelectItem value="Analyzed">Analyzed</SelectItem>
                    <SelectItem value="Flagged">Flagged</SelectItem>
                    <SelectItem value="Archived">Archived</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-sm font-medium">Search</label>
                <Input
                  placeholder="Search content..."
                  value={filters.search_term || ""}
                  onChange={(e) => setFilters(prev => ({ ...prev, search_term: e.target.value || undefined }))}
                />
              </div>
            </div>
            <div className="flex items-center gap-4 mt-4">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="analyzed-only"
                  checked={filters.analyzed_only || false}
                  onCheckedChange={(checked) => setFilters(prev => ({ ...prev, analyzed_only: checked as boolean }))}
                />
                <label htmlFor="analyzed-only" className="text-sm font-medium">
                  Analyzed content only
                </label>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setFilters({})}
              >
                Clear Filters
              </Button>
            </div>
          </Card>
        )}

        {/* Content List */}
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {filteredScrapedContent.map((content) => (
            <div
              key={content.id}
              className={`flex items-start space-x-4 p-4 border rounded-lg hover:bg-muted/50 cursor-pointer transition-colors ${
                selectedContent.includes(content.id) ? 'bg-primary/10 border-primary' : ''
              }`}
              onClick={() => {
                setSelectedContent(prev => 
                  prev.includes(content.id)
                    ? prev.filter(id => id !== content.id)
                    : [...prev, content.id]
                );
              }}
            >
              <Checkbox
                checked={selectedContent.includes(content.id)}
                onChange={() => {}}
                className="mt-1"
              />
              <div className="flex-1 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{content.author}</span>
                    <Badge variant="outline">{content.platform}</Badge>
                    {content.is_analyzed && (
                      <Badge variant="secondary" className="text-xs">
                        <CheckCircle className="h-3 w-3 mr-1" />
                        Analyzed
                      </Badge>
                    )}
                  </div>
                  <Badge variant={
                    content.risk_level === 'Critical' ? 'destructive' :
                    content.risk_level === 'High' ? 'destructive' :
                    content.risk_level === 'Medium' ? 'default' : 'secondary'
                  }>
                    {content.risk_level}
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground line-clamp-2">
                  {content.text}
                </p>
                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {new Date(content.posted_at).toLocaleDateString()}
                  </span>
                  <span>@{content.source_handle}</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredScrapedContent.length > 0 && (
          <div className="text-sm text-muted-foreground text-center pt-4">
            Showing {filteredScrapedContent.length} of {scrapedContent.length} content items
          </div>
        )}
      </div>
    );
  };

  // Render analysis summary for scraped content
  const renderAnalysisSummary = () => {
    if (!analysisResult) return null;

    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-2xl font-bold" style={{ color: analysisResult.suspicion_score >= 70 ? '#ef4444' : analysisResult.suspicion_score >= 40 ? '#f59e0b' : '#10b981' }}>
              {analysisResult.suspicion_score}%
            </div>
            <div className="text-sm text-muted-foreground">Suspicion Score</div>
          </div>
          <Badge variant={analysisResult.is_flagged ? "destructive" : "secondary"}>
            {analysisResult.is_flagged ? "FLAGGED" : "CLEAN"}
          </Badge>
        </div>
        
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Intent:</span>
            <Badge variant="outline">{analysisResult.intent}</Badge>
          </div>
          <div className="flex justify-between text-sm">
            <span>Confidence:</span>
            <span>{Math.round(analysisResult.confidence * 100)}%</span>
          </div>
          <div className="flex justify-between text-sm">
            <span>Processing Time:</span>
            <span>{analysisResult.processing_time.toFixed(3)}s</span>
          </div>
        </div>

        {analysisResult.matched_keywords.length > 0 && (
          <div>
            <div className="text-sm font-medium mb-2">Matched Keywords:</div>
            <div className="flex flex-wrap gap-1">
              {analysisResult.matched_keywords.map((keyword, index) => (
                <Badge key={index} variant="outline" className="text-xs">
                  {keyword}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderContentResults = () => {
    if (isContentLoading) {
      return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <Skeleton className="h-6 w-1/2" />
            </CardHeader>
            <CardContent className="space-y-4">
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-5/6" />
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <Skeleton className="h-6 w-1/2" />
            </CardHeader>
            <CardContent className="space-y-4">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-5/6" />
            </CardContent>
          </Card>
          <Card className="lg:col-span-2">
            <CardHeader>
              <Skeleton className="h-6 w-1/3" />
            </CardHeader>
            <CardContent className="space-y-4">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </CardContent>
          </Card>
        </div>
      );
    }

    if (!analysisResult) {
      return (
        <div className="flex flex-col items-center justify-center text-center p-12 border-2 border-dashed rounded-lg h-full">
          <div className="p-4 bg-secondary rounded-full mb-4">
              <Bot className="h-10 w-10 text-muted-foreground" />
          </div>
          <h3 className="text-xl font-semibold">Awaiting Content Analysis</h3>
          <p className="text-muted-foreground mt-1">Submit content to begin the NLP-based analysis process.</p>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        {/* Risk Assessment Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
              <ShieldAlert className={analysisResult.is_flagged ? "text-red-500" : "text-green-500"} />
                Risk Assessment
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-3xl font-bold" style={{ color: analysisResult.suspicion_score >= 70 ? '#ef4444' : analysisResult.suspicion_score >= 40 ? '#f59e0b' : '#10b981' }}>
                  {analysisResult.suspicion_score}%
                </div>
                <div className="text-sm text-muted-foreground">Suspicion Score</div>
              </div>
              <Badge variant={analysisResult.is_flagged ? "destructive" : "secondary"}>
                {analysisResult.is_flagged ? "FLAGGED" : "CLEAN"}
              </Badge>
            </div>
              <Separator />
            <div>
              <h4 className="font-semibold mb-2">Detected Intent</h4>
              <Badge variant="outline" className="text-lg px-3 py-1">
                {analysisResult.intent}
              </Badge>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Confidence Level</h4>
              <div className="text-lg font-semibold" style={{ color: analysisResult.confidence >= 0.8 ? '#10b981' : analysisResult.confidence >= 0.6 ? '#f59e0b' : '#6b7280' }}>
                {(analysisResult.confidence * 100).toFixed(0)}%
              </div>
              </div>
            </CardContent>
          </Card>

        {/* Analysis Details */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bot />
                NLP Analysis Results
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h4 className="font-semibold mb-2">Matched Keywords</h4>
                <div className="flex flex-wrap gap-2">
                  {analysisResult.matched_keywords.map((keyword, i) => (
                    <Badge key={i} variant="secondary" className="bg-red-100 text-red-800 border-red-200">
                      {keyword}
                    </Badge>
                  ))}
                </div>
              </div>
              <Separator />
              <div>
                <h4 className="font-semibold mb-2">Drug References</h4>
                <div className="flex flex-wrap gap-2">
                  {analysisResult.analysis_data.drug_matches.map((drug, i) => (
                    <Badge key={i} variant="outline" className="bg-orange-100 text-orange-800 border-orange-200">
                      {drug}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText />
                Analysis Details
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h4 className="font-semibold mb-2">Selling Indicators</h4>
                <div className="flex flex-wrap gap-2">
                  {analysisResult.analysis_data.selling_indicators.map((indicator, i) => (
                    <Badge key={i} variant="destructive" className="text-xs">
                      {indicator}
                    </Badge>
                  ))}
                </div>
              </div>
              <div>
                <h4 className="font-semibold mb-2">Buying Indicators</h4>
                <div className="flex flex-wrap gap-2">
                  {analysisResult.analysis_data.buying_indicators.map((indicator, i) => (
                    <Badge key={i} variant="secondary" className="text-xs">
                      {indicator}
                    </Badge>
                  ))}
                </div>
              </div>
              <div>
                <h4 className="font-semibold mb-2">Payment References</h4>
                <div className="flex flex-wrap gap-2">
                  {analysisResult.analysis_data.payment_indicators.map((payment, i) => (
                    <Badge key={i} variant="outline" className="text-xs">
                      {payment}
                    </Badge>
                  ))}
                </div>
              </div>
              <div>
                <h4 className="font-semibold mb-2">Location References</h4>
                <div className="flex flex-wrap gap-2">
                  {analysisResult.analysis_data.location_indicators.map((location, i) => (
                    <Badge key={i} variant="outline" className="text-xs">
                      {location}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Case Linking Button */}
        {analysisResult.is_flagged && (
          <Card className="border-red-200 bg-red-50">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-semibold text-red-800">Flagged Content Detected</h4>
                  <p className="text-sm text-red-600 mt-1">
                    This content has been flagged for review due to high suspicion score.
                  </p>
                </div>
                <div className="flex gap-2">
                  <Button 
                    variant="destructive"
                    onClick={() => {
                      // TODO: Implement case linking functionality
                      toast({
                        title: "Case Linking",
                        description: "Case linking functionality will be implemented next.",
                      });
                    }}
                  >
                    Link to Case
                  </Button>
                  
                  {/* Save Content Button - only show if not already saved */}
                  {!analysisResult.saved_to_database && (
                    <Button 
                      variant="outline"
                      onClick={saveContentAfterAnalysis}
                      disabled={isContentLoading}
                    >
                      {isContentLoading ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Saving...
                        </>
                      ) : (
                        <>
                          <Database className="mr-2 h-4 w-4" />
                          Save Content
                        </>
                      )}
                    </Button>
                  )}
                  
                  {/* Show saved status if already saved */}
                  {analysisResult.saved_to_database && (
                    <div className="flex items-center gap-2 px-3 py-2 bg-green-50 border border-green-200 rounded-md">
                      <CheckCircle className="h-4 w-4 text-green-600" />
                      <span className="text-sm font-medium text-green-800">Saved to Database</span>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Content Analysis</h2>
          <p className="text-muted-foreground">
            Analyze social media content for drug-related keywords and suspicious activity.
          </p>
        </div>
      </div>

      <Tabs defaultValue="manual" className="space-y-6">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="manual" className="flex items-center gap-2">
            <FileText className="h-4 w-4" />
            Manual Analysis
          </TabsTrigger>
          <TabsTrigger value="scraped" className="flex items-center gap-2">
            <Database className="h-4 w-4" />
            Scraped Content Pipeline
          </TabsTrigger>
        </TabsList>

        {/* Manual Content Analysis Tab */}
        <TabsContent value="manual" className="space-y-6">
    <div className="grid grid-cols-1 xl:grid-cols-3 gap-8 items-start">
      <div className="xl:col-span-1 xl:sticky top-8">
        <Card>
          <CardHeader>
            <CardTitle>Content Submission</CardTitle>
            <CardDescription>Enter social media content for analysis.</CardDescription>
          </CardHeader>
          <CardContent>
            <Form {...contentForm}>
              <form onSubmit={contentForm.handleSubmit(onContentSubmit)} className="space-y-6">
                <FormField
                  control={contentForm.control}
                  name="platform"
                  render={({ field }) => (
                    <FormItem>
                            <FormLabel>Platform (Optional)</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                                  <SelectValue placeholder="Select a platform (optional)" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                                <SelectItem value="Instagram">
                                    <div className="flex items-center gap-2"><Instagram className="h-4 w-4"/> Instagram</div>
                                </SelectItem>
                          <SelectItem value="Telegram">
                              <div className="flex items-center gap-2"><Send className="h-4 w-4"/> Telegram</div>
                          </SelectItem>
                          <SelectItem value="WhatsApp">
                              <div className="flex items-center gap-2"><MessageSquare className="h-4 w-4"/> WhatsApp</div>
                          </SelectItem>
                                <SelectItem value="Facebook">Facebook</SelectItem>
                                <SelectItem value="Twitter">Twitter</SelectItem>
                                <SelectItem value="TikTok">TikTok</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={contentForm.control}
                        name="username"
                  render={({ field }) => (
                    <FormItem>
                            <FormLabel>Username (Optional)</FormLabel>
                      <FormControl>
                              <Input placeholder="e.g. @username or username (optional)" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={contentForm.control}
                  name="content"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Content</FormLabel>
                      <FormControl>
                        <Textarea
                          placeholder="Paste text content here..."
                          className="resize-y min-h-[150px]"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                      
                      {/* Save Content Checkbox */}
                      <div className="flex items-center space-x-2 p-4 border rounded-lg bg-muted/50">
                        <Checkbox
                          id="save-content"
                          checked={saveContent}
                          onCheckedChange={(checked) => setSaveContent(checked as boolean)}
                        />
                        <label
                          htmlFor="save-content"
                          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                        >
                          Save content to database
                        </label>
                      </div>
                      
                <Button type="submit" className="w-full" disabled={isContentLoading}>
                  {isContentLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                          <>
                            <Send className="mr-2 h-4 w-4" />
                            Analyze Content
                          </>
                  )}
                </Button>
              </form>
            </Form>
          </CardContent>
        </Card>
      </div>

      <div className="xl:col-span-2 space-y-6">
          {renderContentResults()}
      </div>
          </div>
        </TabsContent>

        {/* Scraped Content Pipeline Tab */}
        <TabsContent value="scraped" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Scraped Content List */}
            <div className="lg:col-span-2 space-y-4">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        <Database className="h-5 w-5" />
                        Scraped Content
                      </CardTitle>
                      <CardDescription>
                        Select content from your scraped data for analysis pipeline
                      </CardDescription>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setShowFilters(!showFilters)}
                      >
                        <Filter className="h-4 w-4 mr-2" />
                        Filters
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={loadScrapedContent}
                        disabled={isLoadingScrapedContent}
                      >
                        <RefreshCw className={`h-4 w-4 mr-2 ${isLoadingScrapedContent ? 'animate-spin' : ''}`} />
                        Refresh
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  {renderScrapedContentList()}
                </CardContent>
              </Card>
            </div>

            {/* Batch Analysis Controls & Results */}
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Bot className="h-5 w-5" />
                    Batch Analysis
                  </CardTitle>
                  <CardDescription>
                    Analyze selected content items
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">
                      Selected: {selectedContent.length} items
                    </span>
                    <Button
                      onClick={analyzeSelectedContent}
                      disabled={selectedContent.length === 0 || isAnalyzingSelected}
                      className="w-full"
                    >
                      {isAnalyzingSelected ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Analyzing...
                        </>
                      ) : (
                        <>
                          <Search className="mr-2 h-4 w-4" />
                          Analyze Selected
                        </>
                      )}
                    </Button>
                  </div>
                  
                  {selectedContent.length > 0 && (
                    <Button
                      variant="outline"
                      onClick={() => setSelectedContent([])}
                      className="w-full"
                    >
                      Clear Selection
                    </Button>
                  )}
                </CardContent>
              </Card>

              {/* Analysis Results Panel */}
              {analysisResult && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <ShieldAlert className="h-5 w-5" />
                      Latest Analysis Result
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {renderAnalysisSummary()}
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
