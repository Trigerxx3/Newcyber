"use client";

import * as React from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";
import { Bot, FileText, Instagram, Loader2, MessageSquare, Send, ShieldAlert } from "lucide-react";

import { analyzeSocialMediaContent, AnalyzeSocialMediaContentOutput } from "@/ai/flows/analyze-social-media-content";
import { assessDrugTraffickingRisk, AssessDrugTraffickingRiskOutput } from "@/ai/flows/assess-drug-trafficking-risk";
import { generateReportFromAnalysis, GenerateReportFromAnalysisOutput } from "@/ai/flows/generate-report-from-analysis";
// import { saveAnalysisToPostgres } from "@/app/actions"; // TODO: Replace with your PostgreSQL action

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

const contentFormSchema = z.object({
  platform: z.enum(["Telegram", "WhatsApp", "Instagram"], {
    required_error: "Please select a platform.",
  }),
  channel: z.string().min(3, { message: "Channel must be at least 3 characters." }),
  content: z.string().min(20, { message: "Content must be at least 20 characters." }),
});

export function ContentAnalysis() {
  const { toast } = useToast();
  
  const [isContentLoading, setIsContentLoading] = React.useState(false);
  const [analysisResult, setAnalysisResult] = React.useState<AnalyzeSocialMediaContentOutput | null>(null);
  const [riskResult, setRiskResult] = React.useState<AssessDrugTraffickingRiskOutput | null>(null);
  const [reportResult, setReportResult] = React.useState<GenerateReportFromAnalysisOutput | null>(null);

  const contentForm = useForm<z.infer<typeof contentFormSchema>>({
    resolver: zodResolver(contentFormSchema),
    defaultValues: {
      content: "",
      channel: "",
    },
  });

  async function onContentSubmit(values: z.infer<typeof contentFormSchema>) {
    setIsContentLoading(true);
    setAnalysisResult(null);
    setRiskResult(null);
    setReportResult(null);

    try {
      const analysis = await analyzeSocialMediaContent({
        platform: values.platform,
        content: values.content,
      });
      setAnalysisResult(analysis);

      const risk = await assessDrugTraffickingRisk({
        contentAnalysis: JSON.stringify(analysis, null, 2),
      });
      setRiskResult(risk);

      const report = await generateReportFromAnalysis({
        contentAnalysis: JSON.stringify(analysis, null, 2),
        riskAssessment: JSON.stringify(risk, null, 2),
      });
      setReportResult(report);

      // TODO: Replace Firebase save with your PostgreSQL implementation.
      // The AI analysis part above uses Genkit, which is a Firebase/Google product.
      // You may need to replace these flows if you are moving away from Google Cloud entirely.
      if (risk.riskLevel !== 'Low') {
        // const saveResult = await saveAnalysisToPostgres({
        //   platform: values.platform,
        //   channel: values.channel,
        //   content: values.content,
        //   analysisResult: analysis,
        //   riskResult: risk,
        // });
        // if (saveResult.success) {
        //   toast({
        //     title: "Analysis Saved",
        //     description: `Flagged content has been saved to your PostgreSQL database.`,
        //   });
        // } else {
        //   toast({
        //     variant: "destructive",
        //     title: "Save Failed",
        //     description: saveResult.message,
        //   });
        // }
      }

    } catch (error) {
      console.error("Analysis pipeline failed:", error);
      toast({
        variant: "destructive",
        title: "Analysis Failed",
        description: "An unexpected error occurred. Please try again later.",
      });
    } finally {
      setIsContentLoading(false);
    }
  }

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

    if (!analysisResult && !riskResult) {
      return (
        <div className="flex flex-col items-center justify-center text-center p-12 border-2 border-dashed rounded-lg h-full">
          <div className="p-4 bg-secondary rounded-full mb-4">
              <Bot className="h-10 w-10 text-muted-foreground" />
          </div>
          <h3 className="text-xl font-semibold">Awaiting Content Analysis</h3>
          <p className="text-muted-foreground mt-1">Submit content to begin the analysis process.</p>
        </div>
      );
    }

    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
        {riskResult && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ShieldAlert className="text-accent" />
                Risk Assessment
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <RiskMeter score={riskResult.riskScore} level={riskResult.riskLevel} />
              <Separator />
              <h4 className="font-semibold">Risk Indicators</h4>
              <div className="flex flex-wrap gap-2">
                {riskResult.indicators.map((indicator, i) => (
                  <Badge key={i} variant="secondary" className="bg-accent/10 text-accent border-accent/20">{indicator}</Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
        {analysisResult && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bot />
                AI Content Analysis
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h4 className="font-semibold mb-2">Potential Indicators</h4>
                <div className="flex flex-wrap gap-2">
                  {analysisResult.indicators.map((indicator, i) => (
                    <Badge key={i} variant="outline">{indicator}</Badge>
                  ))}
                </div>
              </div>
              <Separator />
              <div>
                <h4 className="font-semibold">AI Reasoning</h4>
                <p className="text-muted-foreground text-sm mt-2">{analysisResult.reasoning}</p>
              </div>
            </CardContent>
          </Card>
        )}
        {reportResult && (
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText />
                Generated Summary Report
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground whitespace-pre-wrap">{reportResult.report}</p>
            </CardContent>
          </Card>
        )}
      </div>
    );
  };

  return (
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
                      <FormLabel>Platform</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select a platform" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="Telegram">
                              <div className="flex items-center gap-2"><Send className="h-4 w-4"/> Telegram</div>
                          </SelectItem>
                          <SelectItem value="WhatsApp">
                              <div className="flex items-center gap-2"><MessageSquare className="h-4 w-4"/> WhatsApp</div>
                          </SelectItem>
                          <SelectItem value="Instagram">
                              <div className="flex items-center gap-2"><Instagram className="h-4 w-4"/> Instagram</div>
                          </SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={contentForm.control}
                  name="channel"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Channel / Group / Username</FormLabel>
                      <FormControl>
                        <Input placeholder="e.g. @example_channel" {...field} />
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
                <Button type="submit" className="w-full" disabled={isContentLoading}>
                  {isContentLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    "Run Analysis"
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
  );
}
