'use client';

import * as React from 'react';
import { getDashboardData, seedDatabase, isFirebaseConfigured } from '@/app/actions';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Download, FileWarning, KeyRound, Loader2, PieChartIcon, Sparkles, Users } from 'lucide-react';
import { ChartContainer, ChartTooltip, ChartTooltipContent, ChartConfig } from '@/components/ui/chart';
import { Bar, BarChart, Pie, PieChart, ResponsiveContainer, Cell, XAxis, YAxis, Tooltip as RechartsTooltip, CartesianGrid } from 'recharts';
import { format, parseISO } from 'date-fns';
import { cn } from '@/lib/utils';
import { useToast } from '@/hooks/use-toast';
import { getSampleDashboardData } from '@/lib/sample-data';

// Define types for the data we expect from the action
type FlaggedPost = {
  id: string;
  platform: string;
  channel: string;
  text: string;
  riskLevel: string;
  riskScore: number;
  detected_keywords: string[];
  timestamp: string;
};

type SuspectedUser = {
  id:string;
  username: string;
  platform: string;
  risk_level: string;
  linked_profiles: string[];
  last_seen: string;
};

type Stats = {
  riskLevelCounts: { [key: string]: number };
  platformCounts: { [key: string]: number };
  keywordCounts: { [key: string]: number };
};

const riskLevelChartConfig = {
  count: { label: 'Count' },
  Low: { label: 'Low', color: 'hsl(var(--chart-2))' },
  Medium: { label: 'Medium', color: 'hsl(var(--chart-4))' },
  High: { label: 'High', color: 'hsl(var(--chart-1))' },
  Critical: { label: 'Critical', color: 'hsl(var(--destructive))' },
} satisfies ChartConfig;

const platformChartConfig = {
    count: { label: 'Posts' },
    Telegram: { label: 'Telegram', color: 'hsl(var(--chart-1))' },
    WhatsApp: { label: 'WhatsApp', color: 'hsl(var(--chart-2))' },
    Instagram: { label: 'Instagram', color: 'hsl(var(--chart-3))' },
} satisfies ChartConfig;

const keywordChartConfig = {
  count: { label: 'Frequency' },
} satisfies ChartConfig;

export function LiveDashboard() {
  const { toast } = useToast();
  const [loading, setLoading] = React.useState(true);
  const [isSeeding, setIsSeeding] = React.useState(false);
  const [firebaseConfigured, setFirebaseConfigured] = React.useState<boolean | null>(null);
  const [data, setData] = React.useState<{
    flaggedPosts: FlaggedPost[];
    suspectedUsers: SuspectedUser[];
    stats: Stats;
  } | null>(null);

  React.useEffect(() => {
    const init = async () => {
        setLoading(true);
        try {
            const isConfigured = await isFirebaseConfigured();
            setFirebaseConfigured(isConfigured);
            
            if (isConfigured) {
              const result = await getDashboardData();
              if (result) {
                  setData(result as any);
              }
            } else {
              setData(getSampleDashboardData() as any);
            }
        } catch (error) {
            console.error("Failed to fetch dashboard data:", error);
            toast({
                variant: "destructive",
                title: "Error",
                description: "Could not fetch dashboard data.",
            })
        } finally {
            setLoading(false);
        }
    };
    init();
  }, [toast]);

  const handleSeedDatabase = async () => {
    setIsSeeding(true);
    try {
        if (firebaseConfigured) {
          const result = await seedDatabase();
          if (result.success) {
              toast({
                  title: 'Success',
                  description: result.message,
              });
              // Re-fetch data after seeding
              const newData = await getDashboardData();
              if (newData) {
                  setData(newData as any);
              }
          } else {
              toast({
                  variant: 'destructive',
                  title: 'Seeding Failed',
                  description: result.message,
              });
          }
        } else {
            // "Demo mode" seeding
            setData(getSampleDashboardData() as any);
            toast({
                title: 'Success',
                description: 'Dashboard populated with sample data.',
            });
        }
    } catch (error) {
        toast({
            variant: 'destructive',
            title: 'Error',
            description: 'An unexpected error occurred while seeding the database.',
        });
    } finally {
        setIsSeeding(false);
    }
  };

  const handleExport = () => {
    toast({
        title: "Feature not available",
        description: "Report generation is not yet implemented.",
    });
  };

  const getRiskColorClass = (level: string) => {
    if (level === 'Critical' || level === 'High') return "bg-destructive/80 text-destructive-foreground";
    if (level === 'Medium') return "bg-accent text-accent-foreground";
    return "bg-secondary text-secondary-foreground";
  };
  
  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(3)].map((_, i) => (
            <Card key={i}>
              <CardHeader><Skeleton className="h-6 w-1/2" /></CardHeader>
              <CardContent><Skeleton className="h-48 w-full" /></CardContent>
            </Card>
          ))}
        </div>
        <Card>
          <CardHeader><Skeleton className="h-6 w-1/3" /></CardHeader>
          <CardContent className="space-y-2">
            {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-10 w-full" />)}
          </CardContent>
        </Card>
      </div>
    );
  }

  const noData = !data || (!data.flaggedPosts.length && !data.suspectedUsers.length);

  if (firebaseConfigured === false && noData) {
    return (
      <div className="flex flex-col items-center justify-center text-center p-12 border-2 border-dashed rounded-lg h-full min-h-[60vh]">
        <PieChartIcon className="h-12 w-12 text-muted-foreground mb-4" />
        <h3 className="text-xl font-semibold">Firebase Not Configured</h3>
        <p className="text-muted-foreground mt-2 max-w-md">
            Please set your Firebase environment variables to connect to the database and view the dashboard. You can use sample data to preview the dashboard in the meantime.
        </p>
        <Button className="mt-6" onClick={handleSeedDatabase} disabled={isSeeding}>
            {isSeeding ? (
                <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Populating...
                </>
            ) : (
                <>
                    <Sparkles className="mr-2 h-4 w-4" />
                    Populate with Sample Data
                </>
            )}
        </Button>
      </div>
    );
  }

  if (noData) {
    return (
        <div className="flex flex-col items-center justify-center text-center p-12 border-2 border-dashed rounded-lg h-full min-h-[60vh]">
            <PieChartIcon className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-xl font-semibold">
                {firebaseConfigured ? "Dashboard is Empty" : "Firebase Not Configured"}
            </h3>
            <p className="text-muted-foreground mt-2 max-w-md">
                {firebaseConfigured
                    ? "Submit some analyses to see data, or populate the dashboard with sample data to get started."
                    : "To use a live database, please set your Firebase environment variables. Otherwise, you can use sample data to preview the dashboard."
                }
            </p>
            <Button className="mt-6" onClick={handleSeedDatabase} disabled={isSeeding}>
                {isSeeding ? (
                    <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Populating...
                    </>
                ) : (
                    <>
                        <Sparkles className="mr-2 h-4 w-4" />
                        Populate with Sample Data
                    </>
                )}
            </Button>
        </div>
    )
  }
  
  if (!data) return null; // Should not happen if logic above is correct, but good for type safety

  const riskLevelData = Object.entries(data.stats.riskLevelCounts).map(([name, count]) => ({ name, count, fill: `var(--color-${name})` }));
  const platformData = Object.entries(data.stats.platformCounts).map(([name, count]) => ({ name, count, fill: `var(--color-${name})` }));
  const keywordData = Object.entries(data.stats.keywordCounts).map(([name, count]) => ({ name, count }));

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold tracking-tight">Intelligence Dashboard</h2>
        <Button variant="outline" onClick={handleExport}>
            <Download className="mr-2 h-4 w-4" />
            Export Report
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base"><FileWarning className="h-5 w-5" /> Risk Level Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ChartContainer config={riskLevelChartConfig} className="h-48 w-full">
              <ResponsiveContainer>
                <PieChart>
                  <ChartTooltip content={<ChartTooltipContent nameKey="count" hideLabel />} />
                  <Pie data={riskLevelData} dataKey="count" nameKey="name" cx="50%" cy="50%" outerRadius={60}>
                    {riskLevelData.map((entry) => (
                        <Cell key={`cell-${entry.name}`} fill={cn(
                            entry.name === "Critical" && "hsl(var(--destructive))",
                            entry.name === "High" && "hsl(var(--chart-1))",
                            entry.name === "Medium" && "hsl(var(--chart-4))",
                            entry.name === "Low" && "hsl(var(--chart-2))"
                        )} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            </ChartContainer>
          </CardContent>
        </Card>
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base"><PieChartIcon className="h-5 w-5" /> Platform Distribution</CardTitle>
            </CardHeader>
            <CardContent>
                <ChartContainer config={platformChartConfig} className="h-48 w-full">
                    <ResponsiveContainer>
                        <PieChart>
                            <ChartTooltip content={<ChartTooltipContent nameKey="count" hideLabel />} />
                            <Pie data={platformData} dataKey="count" nameKey="name" cx="50%" cy="50%" outerRadius={60}>
                                {platformData.map((entry) => (
                                    <Cell key={`cell-${entry.name}`} fill={cn(
                                        entry.name === "Telegram" && "hsl(var(--chart-1))",
                                        entry.name === "WhatsApp" && "hsl(var(--chart-2))",
                                        entry.name === "Instagram" && "hsl(var(--chart-3))"
                                    )} />
                                ))}
                            </Pie>
                        </PieChart>
                    </ResponsiveContainer>
                </ChartContainer>
            </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base"><KeyRound className="h-5 w-5" /> Top Keywords</CardTitle>

          </CardHeader>
          <CardContent>
            <ChartContainer config={keywordChartConfig} className="h-48 w-full">
                <ResponsiveContainer>
                    <BarChart data={keywordData} layout="vertical" margin={{ left: 10, right: 10 }}>
                        <CartesianGrid horizontal={false} />
                        <XAxis type="number" hide />
                        <YAxis dataKey="name" type="category" tickLine={false} axisLine={false} tickMargin={10} width={80} interval={0} />
                        <RechartsTooltip cursor={{ fill: 'hsl(var(--muted))' }} content={<ChartTooltipContent indicator="line" />} />
                        <Bar dataKey="count" fill="hsl(var(--primary))" radius={4} barSize={16} />
                    </BarChart>
                </ResponsiveContainer>
            </ChartContainer>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><FileWarning className="h-5 w-5" /> Recently Flagged Posts</CardTitle>
            <CardDescription>Displaying the latest flagged posts.</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Platform</TableHead>
                  <TableHead className="hidden sm:table-cell">Content</TableHead>
                  <TableHead>Risk</TableHead>
                  <TableHead className="hidden md:table-cell">Timestamp</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.flaggedPosts.map((post) => (
                  <TableRow key={post.id}>
                    <TableCell>{post.platform}</TableCell>
                    <TableCell className="max-w-xs truncate hidden sm:table-cell">{post.text}</TableCell>
                    <TableCell>
                      <Badge className={cn(getRiskColorClass(post.riskLevel))} variant="secondary">
                          {post.riskLevel} ({post.riskScore})
                      </Badge>
                    </TableCell>
                    <TableCell className="hidden md:table-cell">{format(parseISO(post.timestamp), "PP")}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><Users className="h-5 w-5" /> Recently Flagged Users</CardTitle>
            <CardDescription>Displaying the latest flagged users.</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Username</TableHead>
                  <TableHead>Risk</TableHead>
                  <TableHead className="hidden sm:table-cell">Linked</TableHead>
                  <TableHead className="hidden md:table-cell">Last Seen</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.suspectedUsers.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>
                        <div className="font-medium">{user.username}</div>
                        <div className="text-xs text-muted-foreground">{user.platform}</div>
                    </TableCell>
                    <TableCell>
                      <Badge className={cn(getRiskColorClass(user.risk_level))} variant="secondary">
                        {user.risk_level}
                      </Badge>
                    </TableCell>
                    <TableCell className="hidden sm:table-cell max-w-xs truncate">{user.linked_profiles.join(', ')}</TableCell>
                    <TableCell className="hidden md:table-cell">{format(parseISO(user.last_seen), "PP")}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
