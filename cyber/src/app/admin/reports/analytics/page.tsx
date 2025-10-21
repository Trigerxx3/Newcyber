'use client'

import ProtectedRoute from '@/components/ProtectedRoute'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function ReportAnalyticsPage() {
  return (
    <ProtectedRoute>
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <Card className="glassmorphism">
          <CardHeader>
            <CardTitle>Report Analytics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-muted-foreground">Analytics and charts will go here.</div>
          </CardContent>
        </Card>
      </div>
    </ProtectedRoute>
  )
}


