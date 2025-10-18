import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Bell } from "lucide-react";

export default function AlertsPage() {
  return (
    <main className="flex-1 p-4 sm:p-6 md:p-8">
      <div className="max-w-screen-2xl mx-auto flex items-center justify-center h-full">
        <Card className="w-full max-w-md text-center">
            <CardHeader>
                <div className="mx-auto bg-muted rounded-full p-3 w-fit">
                    <Bell className="h-8 w-8 text-muted-foreground" />
                </div>
                <CardTitle className="mt-4">Alerts</CardTitle>
                <CardDescription>This feature is currently under development.</CardDescription>
            </CardHeader>
            <CardContent>
                <p className="text-sm text-muted-foreground">
                    Real-time alerting and notification configurations will be available here soon.
                </p>
            </CardContent>
        </Card>
      </div>
    </main>
  );
}
