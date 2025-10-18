'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useToast } from '@/hooks/use-toast'
import { 
  CheckCircle, 
  AlertTriangle, 
  Clock, 
  Mail, 
  Lock,
  Eye,
  EyeOff,
  Shield,
  ArrowRight
} from 'lucide-react'

interface TokenStatus {
  valid: boolean
  reason?: string
  user?: {
    email: string
    username: string
    role: string
  }
  expires_at?: string
}

export default function VerifyEmailPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { toast } = useToast()
  
  const [token, setToken] = useState<string>('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(true)
  const [verifying, setVerifying] = useState(false)
  const [tokenStatus, setTokenStatus] = useState<TokenStatus | null>(null)
  const [step, setStep] = useState<'checking' | 'set-password' | 'success' | 'error'>('checking')

  useEffect(() => {
    const tokenParam = searchParams.get('token')
    if (tokenParam) {
      setToken(tokenParam)
      checkToken(tokenParam)
    } else {
      setStep('error')
      setTokenStatus({ valid: false, reason: 'No verification token provided' })
      setLoading(false)
    }
  }, [searchParams])

  const checkToken = async (tokenToCheck: string) => {
    try {
      setLoading(true)
      
      const response = await fetch('http://127.0.0.1:5000/api/verification/check-token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token: tokenToCheck })
      })

      const data = await response.json()
      
      if (data.valid) {
        setTokenStatus(data)
        setStep('set-password')
      } else {
        setTokenStatus(data)
        setStep('error')
      }
    } catch (error: any) {
      console.error('Token check failed:', error)
      setTokenStatus({ valid: false, reason: 'Failed to verify token' })
      setStep('error')
    } finally {
      setLoading(false)
    }
  }

  const handleVerifyEmail = async () => {
    if (!password || !confirmPassword) {
      toast({
        title: 'Validation Error',
        description: 'Please fill in all fields',
        variant: 'destructive'
      })
      return
    }

    if (password !== confirmPassword) {
      toast({
        title: 'Password Mismatch',
        description: 'Passwords do not match',
        variant: 'destructive'
      })
      return
    }

    if (password.length < 8) {
      toast({
        title: 'Password Too Weak',
        description: 'Password must be at least 8 characters long',
        variant: 'destructive'
      })
      return
    }

    try {
      setVerifying(true)

      const response = await fetch('http://127.0.0.1:5000/api/verification/verify-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token: token,
          password: password
        })
      })

      const data = await response.json()

      if (response.ok) {
        setStep('success')
        toast({
          title: 'Email Verified!',
          description: 'Your account has been activated. You can now log in.',
          duration: 6000
        })
        
        // Redirect to login after 3 seconds
        setTimeout(() => {
          router.push('/login')
        }, 3000)
      } else {
        toast({
          title: 'Verification Failed',
          description: data.error || 'Failed to verify email',
          variant: 'destructive'
        })
      }
    } catch (error: any) {
      console.error('Verification failed:', error)
      toast({
        title: 'Error',
        description: 'Network error. Please try again.',
        variant: 'destructive'
      })
    } finally {
      setVerifying(false)
    }
  }

  const handleResendEmail = async () => {
    if (!tokenStatus?.user?.email) return
    
    try {
      const response = await fetch('http://127.0.0.1:5000/api/verification/resend-verification', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: tokenStatus.user.email
        })
      })

      const data = await response.json()

      if (response.ok) {
        toast({
          title: 'Email Sent',
          description: 'A new verification email has been sent to your inbox.',
        })
      } else {
        toast({
          title: 'Failed to Resend',
          description: data.error || 'Failed to resend verification email',
          variant: 'destructive'
        })
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Network error. Please try again.',
        variant: 'destructive'
      })
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <Card className="w-full max-w-md bg-white/5 border-white/10">
          <CardContent className="p-8">
            <div className="text-center space-y-4">
              <Clock className="h-12 w-12 text-blue-400 mx-auto animate-spin" />
              <h1 className="text-xl font-semibold text-white">Checking Verification Link</h1>
              <p className="text-gray-400">Please wait while we verify your email link...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (step === 'error') {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <Card className="w-full max-w-md bg-white/5 border-white/10">
          <CardHeader className="text-center">
            <AlertTriangle className="h-12 w-12 text-red-400 mx-auto mb-4" />
            <CardTitle className="text-white">Verification Failed</CardTitle>
            <CardDescription className="text-gray-400">
              {tokenStatus?.reason || 'Unknown error occurred'}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-center space-y-2">
              <p className="text-sm text-gray-500">
                Your verification link may have expired or is invalid.
              </p>
              {tokenStatus?.user?.email && (
                <Button 
                  variant="outline" 
                  onClick={handleResendEmail}
                  className="w-full"
                >
                  <Mail className="h-4 w-4 mr-2" />
                  Request New Verification Email
                </Button>
              )}
              <Button 
                variant="ghost" 
                onClick={() => router.push('/login')}
                className="w-full text-gray-400"
              >
                Back to Login
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (step === 'success') {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <Card className="w-full max-w-md bg-white/5 border-white/10">
          <CardHeader className="text-center">
            <CheckCircle className="h-12 w-12 text-green-400 mx-auto mb-4" />
            <CardTitle className="text-white">Email Verified Successfully!</CardTitle>
            <CardDescription className="text-gray-400">
              Your account has been activated and is ready to use.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="bg-green-400/10 border border-green-400/20 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <Shield className="h-5 w-5 text-green-400" />
                <span className="text-green-400 font-medium">Account Activated</span>
              </div>
              <p className="text-sm text-green-300 mt-2">
                Welcome to the Cyber Intelligence Platform! You now have access to all analyst features.
              </p>
            </div>
            
            <div className="text-center space-y-3">
              <p className="text-sm text-gray-400">
                Redirecting you to the login page...
              </p>
              <Button 
                onClick={() => router.push('/login')}
                className="w-full bg-blue-500 hover:bg-blue-600"
              >
                <ArrowRight className="h-4 w-4 mr-2" />
                Go to Login
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      <Card className="w-full max-w-md bg-white/5 border-white/10">
        <CardHeader className="text-center">
          <Mail className="h-12 w-12 text-blue-400 mx-auto mb-4" />
          <CardTitle className="text-white">Set Your Password</CardTitle>
          <CardDescription className="text-gray-400">
            Complete your account setup for the Cyber Intelligence Platform
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {tokenStatus?.user && (
            <div className="bg-blue-400/10 border border-blue-400/20 rounded-lg p-4">
              <h3 className="text-blue-400 font-medium mb-2">Account Details</h3>
              <div className="text-sm text-gray-300 space-y-1">
                <p><strong>Email:</strong> {tokenStatus.user.email}</p>
                <p><strong>Username:</strong> {tokenStatus.user.username}</p>
                <p><strong>Role:</strong> {tokenStatus.user.role}</p>
              </div>
            </div>
          )}

          <div className="space-y-4">
            <div>
              <Label htmlFor="password" className="text-white">Password</Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="bg-white/10 border-white/20 text-white pr-10"
                  placeholder="Enter your password"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 text-gray-400 hover:text-white"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>

            <div>
              <Label htmlFor="confirmPassword" className="text-white">Confirm Password</Label>
              <Input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="bg-white/10 border-white/20 text-white"
                placeholder="Confirm your password"
              />
            </div>

            <div className="text-xs text-gray-500 space-y-1">
              <p>Password requirements:</p>
              <ul className="list-disc list-inside ml-2 space-y-1">
                <li>At least 8 characters long</li>
                <li>Mix of letters, numbers recommended</li>
                <li>Keep it secure and unique</li>
              </ul>
            </div>
          </div>

          <Button 
            onClick={handleVerifyEmail}
            disabled={verifying || !password || !confirmPassword}
            className="w-full bg-blue-500 hover:bg-blue-600 disabled:opacity-50"
          >
            {verifying ? (
              <>
                <Clock className="h-4 w-4 mr-2 animate-spin" />
                Verifying...
              </>
            ) : (
              <>
                <Lock className="h-4 w-4 mr-2" />
                Verify Email & Set Password
              </>
            )}
          </Button>

          <div className="text-center">
            <Button 
              variant="ghost" 
              onClick={() => router.push('/login')}
              className="text-gray-400 hover:text-white"
            >
              Back to Login
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
