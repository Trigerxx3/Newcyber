'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { apiClient } from '@/lib/api'
import { AlertTriangle, Loader2, CheckCircle2, Eye, EyeOff, Chrome as GoogleIcon } from 'lucide-react'
import { Logo } from '@/components/logo'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [username, setUsername] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [backendStatus, setBackendStatus] = useState<'checking' | 'connected' | 'error'>('checking')
  const [passwordVisible, setPasswordVisible] = useState(false)
  const [confirmPasswordVisible, setConfirmPasswordVisible] = useState(false)
  const [isSignUp, setIsSignUp] = useState(false)
  
  const { signIn, signUp, user, systemUser, loading: authLoading } = useAuth()
  const router = useRouter()

  // Redirect if already logged in
  useEffect(() => {
    console.log('🔐 LoginPage: Auth state check:', { 
      user: !!user, 
      systemUser: !!systemUser, 
      authLoading 
    })
    
    if (!authLoading && user) {
      console.log('🔐 LoginPage: User already logged in, redirecting...')
      // Redirect based on user role
      if (systemUser?.role === 'Admin') {
        console.log('🔐 Admin user already logged in, redirecting to admin dashboard')
        router.push('/admin')
      } else {
        console.log('🔐 Non-admin user already logged in, redirecting to dashboard')
        router.push('/dashboard')
      }
    }
  }, [user, systemUser, authLoading, router])

  const confirmAnd = async (action: () => Promise<void>) => {
    await action()
  }

  // Validation functions
  const isEmailValid = (value: string) => /.+@.+\..+/.test(value)
  const isPasswordValid = (value: string) => value.trim().length >= 6
  const isUsernameValid = (value: string) => value.trim().length >= 3
  const doPasswordsMatch = (pass: string, confirm: string) => pass === confirm

  const validateSignUpForm = () => {
    if (!isEmailValid(email)) {
      setError('Please enter a valid email address')
      return false
    }
    if (!isUsernameValid(username)) {
      setError('Username must be at least 3 characters long')
      return false
    }
    if (!isPasswordValid(password)) {
      setError('Password must be at least 6 characters long')
      return false
    }
    if (!doPasswordsMatch(password, confirmPassword)) {
      setError('Passwords do not match')
      return false
    }
    return true
  }

  const handleSignUp = async () => {
    if (!validateSignUpForm()) return

    setLoading(true)
    setError('')

    try {
      console.log('🔐 Starting sign up process...')
      const result = await signUp(email, password, username, 'Analyst')
      
      if (result.error) {
        console.error('❌ Sign up error:', result.error)
        setError(result.error.message || 'Sign up failed')
      } else {
        console.log('✅ Sign up successful')
        setMessage('Account created successfully! Please sign in with your credentials.')
        setIsSignUp(false)
        // Clear form
        setEmail('')
        setPassword('')
        setUsername('')
        setConfirmPassword('')
      }
    } catch (err: any) {
      console.error('❌ Sign up exception:', err)
      setError(err.message || 'Sign up failed')
    } finally {
      setLoading(false)
    }
  }

  const handleSignIn = async () => {
    setLoading(true)
    setError('')

    try {
      console.log('🔐 Starting sign in process...')
      const result = await signIn(email, password)
      
      if (result.error) {
        console.error('❌ Sign in error:', result.error)
        setError(result.error.message)
      } else {
        console.log('✅ Sign in successful, checking user role...')
        console.log('🔍 Full result data:', result.data)
        
        // Try to get role from multiple possible sources
        const userRole = result.data?.user?.role || result.data?.role
        console.log('🔍 Detected user role:', userRole)
        
        // Also try getting role directly from the API response if no role found
        if (!userRole) {
          try {
            const loginData: any = await apiClient.signIn(email, password)
            const directRole = loginData?.user?.role
            console.log('🔍 Direct API role:', directRole)
            if (directRole === 'Admin' || directRole === 'ADMIN') {
              console.log('🔐 Admin user detected via direct API, redirecting to admin dashboard')
              setTimeout(() => router.push('/admin'), 100)
              return
            } else {
              console.log('🔐 Non-admin user detected via direct API, redirecting to analyst dashboard')
              setTimeout(() => router.push('/dashboard'), 100)
              return
            }
          } catch (e) {
            console.error('Failed to get direct role:', e)
            // If all else fails, default to analyst dashboard
            console.log('🔐 Defaulting to analyst dashboard due to role detection failure')
            setTimeout(() => router.push('/dashboard'), 100)
            return
          }
        }
        
        if (userRole === 'Admin' || userRole === 'ADMIN') {
          console.log('🔐 Admin user detected, redirecting to admin dashboard')
          // Small delay to ensure state is updated
          setTimeout(() => router.push('/admin'), 100)
        } else {
          console.log('🔐 Analyst user detected, redirecting to dashboard')
          setTimeout(() => router.push('/dashboard'), 100)
        }
      }
    } catch (err: any) {
      console.error('❌ Sign in exception:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }


  // Form validation
  const canSubmitSignin = backendStatus === 'connected' && isEmailValid(email) && isPasswordValid(password) && !loading
  const canSubmitSignup = backendStatus === 'connected' && isEmailValid(email) && isUsernameValid(username) && isPasswordValid(password) && doPasswordsMatch(password, confirmPassword) && !loading

  const toggleMode = () => {
    setIsSignUp(!isSignUp)
    setError('')
    setMessage('')
    // Clear form when switching modes
    setEmail('')
    setPassword('')
    setUsername('')
    setConfirmPassword('')
  }

  // Instead of blocking the page, we let the form render while auth initializes

  // API health check
  useEffect(() => {
    console.log('🔧 Login page environment check:', {
      NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
      window_location: typeof window !== 'undefined' ? window.location.href : 'server-side'
    })
    
    const checkHealth = async () => {
      try {
        setBackendStatus('checking')
        console.log('🔍 Starting health check from login page...')
        
        const data: any = await apiClient.healthCheck()
        console.log('✅ Health check successful:', data)
        setBackendStatus(data && data.database_connected === false ? 'error' : 'connected')
      } catch (error) {
        console.error('❌ Health check failed:', error)
        setBackendStatus('error')
      }
    }
    
    checkHealth()
  }, [])

  const retryHealth = async () => {
    try {
      setBackendStatus('checking')
      console.log('🔄 Retrying health check...')
      const data: any = await apiClient.healthCheck()
      console.log('✅ Retry health check response:', data)
      setBackendStatus(data && data.database_connected === false ? 'error' : 'connected')
    } catch (error) {
      console.error('❌ Retry health check failed:', error)
      setBackendStatus('error')
    }
  }
  
  const handleGoogleLogin = () => {
    // Open popup for OAuth
    const url = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'}/api/auth/google/login`
    const popup = window.open(url, 'google_oauth', 'width=500,height=600')
    if (!popup) return
    
    const onMessage = (event: MessageEvent) => {
      const data = event.data as any
      if (data && data.type === 'oauth' && data.provider === 'google') {
        // Store tokens and fetch profile
        try {
          // access_token from backend JWT
          const token = data.access_token as string | null
          if (token) {
            // reuse existing helpers
            // dynamically import to avoid circulars
            import('@/lib/api').then(({ setTokens }) => {
              setTokens(token, null)
            })
          }
          // Best-effort redirect
          router.push('/')
        } catch {}
        window.removeEventListener('message', onMessage)
      }
    }
    window.addEventListener('message', onMessage)
  }

  const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'

  return (
    <div className="min-h-screen flex flex-col bg-[radial-gradient(1200px_600px_at_50%_-10%,rgba(14,165,233,0.18),transparent),radial-gradient(800px_400px_at_80%_10%,rgba(16,185,129,0.12),transparent)]">
      <section className="relative flex-1">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0nNDAnIGhlaWdodD0nNDAnIHhtbG5zPSdodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2Zyc+PHBhdGggZD0nTTAgMjBoNDBNIDIwIDB2NDBNIDAgMGg0MCcgc3Ryb2tlPSdyZ2JhKDI1NSwyNTUsMjU1LDAuMDUpJyBmaWxsPSdub25lJyBzdHJva2Utd2lkdGg9JzAuNScvPjwvc3ZnPg==')] opacity-40 pointer-events-none" />
        <div className="container mx-auto px-6 py-12 md:py-16 flex items-center justify-center">
          <Card className="glassmorphism w-full max-w-md border border-white/10 bg-black/30">
            <CardHeader className="text-center space-y-3">
              <div className="flex justify-center"><Logo /></div>
              <CardTitle className="text-2xl font-bold">
                {isSignUp ? 'Create Account' : 'Sign in to Narcotics Intelligence'}
              </CardTitle>
              <CardDescription>
                {isSignUp ? 'Join the intelligence platform' : 'Access your analyst dashboard'}
              </CardDescription>
            </CardHeader>
            <CardContent>
          {authLoading && (
            <div className="mb-4 rounded border border-white/10 bg-white/5 p-3 text-sm text-muted-foreground">
              Initializing session...
            </div>
          )}

          {/* Backend status banner */}
          {backendStatus === 'checking' && (
            <Alert className="mb-4">
              <Loader2 className="h-4 w-4 animate-spin" />
              <AlertDescription>
                Checking backend at {apiBase}...
              </AlertDescription>
            </Alert>
          )}
          {/* Connected banner removed per request */}
          {backendStatus === 'error' && (
            <Alert className="mb-4" variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription className="flex items-center justify-between">
                <span>Cannot reach backend at {apiBase}. Start it with: python run.py</span>
                <Button size="sm" variant="outline" className="ml-2" onClick={retryHealth}>
                  Retry
                </Button>
              </AlertDescription>
            </Alert>
          )}
          <div className="w-full">
              <form onSubmit={(e) => e.preventDefault()} className="space-y-4">
                {isSignUp && (
                  <div className="space-y-1">
                    <label className="text-sm text-muted-foreground">Username</label>
                    <div className="relative">
                      <Input
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        placeholder="Choose a username"
                        required
                        className={username && !isUsernameValid(username) ? 'border-red-500' : ''}
                      />
                      {username && isUsernameValid(username) && (
                        <CheckCircle2 className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-green-500" />
                      )}
                    </div>
                    {username && !isUsernameValid(username) && (
                      <p className="text-xs text-red-500">Username must be at least 3 characters</p>
                    )}
                  </div>
                )}
                <div className="space-y-1">
                  <label className="text-sm text-muted-foreground">Email</label>
                  <div className="relative">
                    <Input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="Enter your email"
                      required
                      className={email && !isEmailValid(email) ? 'border-red-500' : ''}
                    />
                    {email && isEmailValid(email) && (
                      <CheckCircle2 className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-green-500" />
                    )}
                  </div>
                  {email && !isEmailValid(email) && (
                    <p className="text-xs text-red-500">Please enter a valid email address</p>
                  )}
                </div>
                <div className="space-y-1">
                  <label className="text-sm text-muted-foreground">Password</label>
                  <div className="relative">
                    <Input
                      type={passwordVisible ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder={isSignUp ? "Create a password (min 6 characters)" : "Enter your password"}
                      required
                      className={`pr-10 ${password && !isPasswordValid(password) ? 'border-red-500' : ''}`}
                    />
                    <button
                      type="button"
                      aria-label={passwordVisible ? 'Hide password' : 'Show password'}
                      className="absolute right-8 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                      onClick={() => setPasswordVisible(v => !v)}
                    >
                      {passwordVisible ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                    {password && isPasswordValid(password) && (
                      <CheckCircle2 className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-green-500" />
                    )}
                  </div>
                  {password && !isPasswordValid(password) && (
                    <p className="text-xs text-red-500">Password must be at least 6 characters</p>
                  )}
                </div>
                {isSignUp && (
                  <div className="space-y-1">
                    <label className="text-sm text-muted-foreground">Confirm Password</label>
                    <div className="relative">
                      <Input
                        type={confirmPasswordVisible ? 'text' : 'password'}
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        placeholder="Confirm your password"
                        required
                        className={`pr-10 ${confirmPassword && !doPasswordsMatch(password, confirmPassword) ? 'border-red-500' : ''}`}
                      />
                      <button
                        type="button"
                        aria-label={confirmPasswordVisible ? 'Hide password' : 'Show password'}
                        className="absolute right-8 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                        onClick={() => setConfirmPasswordVisible(v => !v)}
                      >
                        {confirmPasswordVisible ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </button>
                      {confirmPassword && doPasswordsMatch(password, confirmPassword) && (
                        <CheckCircle2 className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-green-500" />
                      )}
                    </div>
                    {confirmPassword && !doPasswordsMatch(password, confirmPassword) && (
                      <p className="text-xs text-red-500">Passwords do not match</p>
                    )}
                  </div>
                )}
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button 
                      type="button" 
                      className="w-full" 
                      disabled={!canSubmitSignin && !canSubmitSignup}
                    >
                      {loading ? (
                        <>
                          <Loader2 className="h-4 w-4 animate-spin mr-2" />
                          {isSignUp ? 'Creating Account...' : 'Signing In...'}
                        </>
                      ) : (
                        isSignUp ? 'Create Account' : 'Sign In'
                      )}
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>
                        {isSignUp ? 'Create Account?' : 'Sign in?'}
                      </AlertDialogTitle>
                      <AlertDialogDescription>
                        {isSignUp 
                          ? 'Create your account with the provided information.' 
                          : 'Continue with the provided credentials.'
                        }
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                      <AlertDialogAction onClick={async () => { 
                        if (isSignUp) {
                          await handleSignUp()
                        } else {
                          await handleSignIn()
                        }
                      }}>
                        {isSignUp ? 'Create Account' : 'Sign In'}
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
                <div className="relative my-3">
                  <div className="absolute inset-0 flex items-center"><span className="w-full border-t border-white/10" /></div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-transparent px-2 text-muted-foreground">Or continue with</span>
                  </div>
                </div>
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button type="button" variant="outline" className="w-full">
                      <GoogleIcon className="h-4 w-4 mr-2" /> 
                      {isSignUp ? 'Sign up with Google' : 'Sign in with Google'}
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>
                        {isSignUp ? 'Sign up with Google?' : 'Continue with Google?'}
                      </AlertDialogTitle>
                      <AlertDialogDescription>
                        {isSignUp 
                          ? 'We will open Google to create your account.' 
                          : 'We will open Google to authenticate your account.'
                        }
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                      <AlertDialogAction onClick={handleGoogleLogin}>
                        {isSignUp ? 'Sign up with Google' : 'Continue with Google'}
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
                
                {/* Toggle between sign-in and sign-up */}
                <div className="text-center mt-4">
                  <p className="text-sm text-muted-foreground">
                    {isSignUp ? 'Already have an account?' : "Don't have an account?"}
                    <button
                      type="button"
                      onClick={toggleMode}
                      className="ml-1 text-blue-400 hover:text-blue-300 underline"
                    >
                      {isSignUp ? 'Sign in' : 'Sign up'}
                    </button>
                  </p>
                </div>
              </form>
          </div>

          {error && (
            <Alert className="mt-4" variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {message && (
            <Alert className="mt-4">
              <AlertDescription>{message}</AlertDescription>
            </Alert>
          )}
            </CardContent>
          </Card>
        </div>
      </section>
    </div>
  )
}





