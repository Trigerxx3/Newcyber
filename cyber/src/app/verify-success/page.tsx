'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { 
  CheckCircle, 
  AlertTriangle, 
  ArrowRight,
  Mail,
  Shield
} from 'lucide-react'

export default function VerifySuccessPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [loading, setLoading] = useState(true)
  const [verificationResult, setVerificationResult] = useState<{
    success: boolean
    message: string
    user?: {
      username: string
      email: string
      role: string
    }
  } | null>(null)

  useEffect(() => {
    // Get verification results from URL params
    const success = searchParams.get('success') === 'true'
    const message = searchParams.get('message') || ''
    const username = searchParams.get('username') || ''
    const email = searchParams.get('email') || ''
    const role = searchParams.get('role') || ''

    setVerificationResult({
      success,
      message,
      user: username ? { username, email, role } : undefined
    })
    setLoading(false)
  }, [searchParams])

  const handleGoToLogin = () => {
    router.push('/login')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="flex items-center gap-3 text-white">
          <div className="w-6 h-6 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
          <span>Loading...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-4">
      <Card className="w-full max-w-md bg-black border-white/20">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            {verificationResult?.success ? (
              <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center">
                <CheckCircle className="h-8 w-8 text-green-400" />
              </div>
            ) : (
              <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center">
                <AlertTriangle className="h-8 w-8 text-red-400" />
              </div>
            )}
          </div>
          
          <CardTitle className="text-white text-xl">
            {verificationResult?.success ? 'Email Verified!' : 'Verification Failed'}
          </CardTitle>
          
          <CardDescription className="text-gray-400 mt-2">
            {verificationResult?.message || 'Unknown result'}
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-6">
          {verificationResult?.success && verificationResult.user && (
            <div className="bg-green-400/10 border border-green-400/20 rounded-lg p-4">
              <div className="flex items-center gap-2 text-green-400 mb-3">
                <Shield className="h-4 w-4" />
                <span className="font-medium">Account Activated</span>
              </div>
              
              <div className="text-sm text-gray-300 space-y-1">
                <p><strong>Username:</strong> {verificationResult.user.username}</p>
                <p><strong>Email:</strong> {verificationResult.user.email}</p>
                <p><strong>Role:</strong> {verificationResult.user.role}</p>
              </div>
            </div>
          )}

          {verificationResult?.success ? (
            <div className="space-y-4">
              <div className="bg-blue-400/10 border border-blue-400/20 rounded-lg p-4">
                <div className="flex items-center gap-2 text-blue-400 mb-2">
                  <Mail className="h-4 w-4" />
                  <span className="font-medium">Next Steps</span>
                </div>
                <p className="text-sm text-gray-300">
                  Your account has been successfully verified and activated. You can now log in to the platform using your credentials.
                </p>
              </div>

              <Button 
                onClick={handleGoToLogin}
                className="w-full bg-blue-500 hover:bg-blue-600 text-white"
              >
                <ArrowRight className="h-4 w-4 mr-2" />
                Go to Login
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="bg-red-400/10 border border-red-400/20 rounded-lg p-4">
                <p className="text-sm text-gray-300">
                  The verification link may be expired, invalid, or already used. Please contact your administrator for assistance.
                </p>
              </div>

              <Button 
                onClick={handleGoToLogin}
                variant="outline"
                className="w-full border-white/20 text-white hover:bg-white/10"
              >
                Back to Login
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
