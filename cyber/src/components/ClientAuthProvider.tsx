'use client'

import { AuthProvider } from '@/contexts/AuthContext'
import { ActiveCaseProvider } from '@/contexts/ActiveCaseContext'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { useEffect, useState } from 'react'

export function ClientAuthProvider({ children }: { children: React.ReactNode }) {
  const [isClient, setIsClient] = useState(false)

  useEffect(() => {
    setIsClient(true)
  }, [])

  if (!isClient) {
    // During SSR, render a simple loading state
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  // On client side, render with auth context wrapped in error boundary
  return (
    <ErrorBoundary>
      <AuthProvider>
        <ActiveCaseProvider>
          {children}
        </ActiveCaseProvider>
      </AuthProvider>
    </ErrorBoundary>
  )
}
