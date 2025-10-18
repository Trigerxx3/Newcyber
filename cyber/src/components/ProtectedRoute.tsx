'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'

interface ProtectedRouteProps {
  children: React.ReactNode
  requiredRole?: 'Admin' | 'Analyst'
}

export function ProtectedRoute({ children, requiredRole }: ProtectedRouteProps) {
  const { user, systemUser, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading) {
      if (!user) {
        router.push('/login')
        return
      }

      if (requiredRole && systemUser?.role !== requiredRole && systemUser?.role !== requiredRole.toUpperCase()) {
        router.push('/unauthorized')
        return
      }
    }
  }, [user, systemUser, loading, router, requiredRole])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900"></div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  if (requiredRole && systemUser?.role !== requiredRole && systemUser?.role !== requiredRole.toUpperCase()) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black text-white">
        <div className="text-center">
          <h1 className="text-2xl font-bold">Unauthorized</h1>
          <p className="text-gray-400">You don't have permission to access this page.</p>
          <p className="text-sm text-gray-500 mt-2">Required role: {requiredRole}</p>
        </div>
      </div>
    )
  }

  return <>{children}</>
}

export default ProtectedRoute