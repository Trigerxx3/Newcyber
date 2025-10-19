"use client";

import * as React from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";
import { AtSign, Instagram, Link as LinkIcon, Loader2, MessageSquare, Send, Users } from "lucide-react";

import { identifySuspectedUser, IdentifySuspectedUserOutput } from "@/ai/flows/identify-suspected-user";
import { saveSuspectedUserData } from "@/app/actions";
import { useToast } from "@/hooks/use-toast";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "./ui/separator";
import { cn } from "@/lib/utils";

const userFormSchema = z.object({
  platform: z.enum(["Telegram", "WhatsApp", "Instagram"], {
    required_error: "Please select a platform.",
  }),
  username: z.string().min(3, { message: "Username must be at least 3 characters." }),
});

export function UserInvestigation() {
  const { toast } = useToast();
  
  const [isUserLoading, setIsUserLoading] = React.useState(false);
  const [userResult, setUserResult] = React.useState<IdentifySuspectedUserOutput | null>(null);

  const userForm = useForm<z.infer<typeof userFormSchema>>({
    resolver: zodResolver(userFormSchema),
    defaultValues: {
      username: "",
    },
  });

  async function onUserSubmit(values: z.infer<typeof userFormSchema>) {
    setIsUserLoading(true);
    setUserResult(null);

    try {
      const result = await identifySuspectedUser({
        platform: values.platform,
        username: values.username,
      });
      setUserResult(result);
      
      const saveResult = await saveSuspectedUserData({
        username: values.username,
        platform: values.platform,
        analysisResult: result,
      });

      if (saveResult.success) {
        toast({
          title: "User Profile Saved",
          description: `User profile for ${values.username} has been saved.`,
        });
      } else if (!saveResult.success) {
        toast({
          variant: "destructive",
          title: "Save Failed",
          description: saveResult.message,
        });
      }

    } catch (error) {
        console.error("User investigation failed:", error);
        toast({
          variant: "destructive",
          title: "Investigation Failed",
          description: "An unexpected error occurred. Please try again later.",
        });
    } finally {
        setIsUserLoading(false);
    }
  }

  const renderUserResults = () => {
    if (isUserLoading) {
      return (
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-1/2" />
          </CardHeader>
          <CardContent className="space-y-4">
            <Skeleton className="h-8 w-1/4" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
            <Separator />
            <Skeleton className="h-4 w-1/3" />
            <Skeleton className="h-4 w-1/2" />
            <Skeleton className="h-4 w-1/3" />
          </CardContent>
        </Card>
      );
    }
    
    if (!userResult) {
      return (
        <div className="flex flex-col items-center justify-center text-center p-12 border-2 border-dashed rounded-lg h-full">
          <div className="p-4 bg-secondary rounded-full mb-4">
              <Users className="h-10 w-10 text-muted-foreground" />
          </div>
          <h3 className="text-xl font-semibold">Awaiting User Investigation</h3>
          <p className="text-muted-foreground mt-1">Submit a username to begin the investigation.</p>
        </div>
      );
    }
    
    const getRiskColorClass = (level: string) => {
        if (level === 'Critical') return "bg-destructive text-destructive-foreground";
        if (level === 'High') return "bg-destructive/80 text-destructive-foreground";
        if (level === 'Medium') return "bg-accent/80 text-accent-foreground";
        return "bg-secondary text-secondary-foreground";
    };

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Users />
                        OSINT Report: {userForm.getValues("username")}
                    </div>
                    <Badge className={cn(getRiskColorClass(userResult.riskLevel))}>
                        {userResult.riskLevel} Risk
                    </Badge>
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                <div>
                    <h4 className="font-semibold">Summary</h4>
                    <p className="text-muted-foreground text-sm mt-2">{userResult.summary}</p>
                </div>
                <Separator />
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <h4 className="font-semibold flex items-center gap-2 mb-2"><LinkIcon className="h-4 w-4 text-accent" /> Linked Profiles</h4>
                        <div className="flex flex-col gap-1">
                            {userResult.linkedProfiles.length > 0 ? userResult.linkedProfiles.map((profile, i) => (
                                <Badge key={i} variant="outline">{profile}</Badge>
                            )) : <p className="text-sm text-muted-foreground">None found.</p>}
                        </div>
                    </div>
                    <div>
                        <h4 className="font-semibold flex items-center gap-2 mb-2"><AtSign className="h-4 w-4 text-accent" /> Potential Email</h4>
                        {userResult.email ? (
                            <Badge variant="outline">{userResult.email}</Badge>
                        ) : <p className="text-sm text-muted-foreground">None found.</p>}
                    </div>
                </div>
            </CardContent>
        </Card>
    );
  };


  return (
    <div className="grid grid-cols-1 xl:grid-cols-3 gap-8 items-start">
        <div className="xl:col-span-1 xl:sticky top-8">
            <Card>
                <CardHeader>
                <CardTitle>User Investigation</CardTitle>
                <CardDescription>Perform OSINT analysis on a username.</CardDescription>
                </CardHeader>
                <CardContent>
                <Form {...userForm}>
                    <form onSubmit={userForm.handleSubmit(onUserSubmit)} className="space-y-6">
                    <FormField
                        control={userForm.control}
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
                        control={userForm.control}
                        name="username"
                        render={({ field }) => (
                        <FormItem>
                            <FormLabel>Username</FormLabel>
                            <FormControl>
                            <Input placeholder="e.g. lsd_plug" {...field} />
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                        )}
                    />
                    <Button type="submit" className="w-full" disabled={isUserLoading}>
                        {isUserLoading ? (
                        <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Investigating...
                        </>
                        ) : (
                        "Investigate User"
                        )}
                    </Button>
                    </form>
                </Form>
                </CardContent>
            </Card>
        </div>
        <div className="xl:col-span-2 space-y-6">
            {renderUserResults()}
        </div>
    </div>
  );
}
