'use client'

import React, { createContext, useContext, useEffect, useState } from 'react'
import apiClient, { setTokens, getAccessToken, getRefreshToken } from '@/lib/api'
import { toast } from '@/hooks/use-toast'

interface SystemUser {
  system_user_id: string
  auth_user_id: string
  username: string
  email: string
  role: 'Admin' | 'Analyst'
  last_login: string | null
  created_at: string
  updated_at: string
}

interface AuthContextType {
  user: { id: string; email?: string | null } | null
  systemUser: SystemUser | null
  session: { access_token: string | null } | null
  loading: boolean
  signUp: (email: string, password: string, username: string, role?: string) => Promise<any>
  signIn: (email: string, password: string) => Promise<any>
  signOut: () => Promise<void>
  refreshSystemUser: () => Promise<void>
  clearAuthState: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<{ id: string; email?: string | null } | null>(null)
  const [systemUser, setSystemUser] = useState<SystemUser | null>(null)
  const [session, setSession] = useState<{ access_token: string | null } | null>(null)
  const [loading, setLoading] = useState(true)

  const debugSystemUsersTable = async () => {
    // This function is no longer needed for Flask backend
    console.log('Debug function disabled for Flask backend')
  }

  const fetchSystemUser = async (authUserId: string) => {
    try {
      // Only fetch profile if we have a token
      const token = getAccessToken()
      if (!token || token.trim() === '') {
        console.log('🔐 AuthContext: No valid token available, skipping profile fetch')
        return null
      }
      
      console.log('🔐 AuthContext: Token found, attempting profile fetch...')
      console.log('🔐 AuthContext: Token preview:', token.substring(0, 50) + '...')
      
      const profile = await apiClient.getProfile()
      console.log('🔐 AuthContext: Profile data received:', profile)
      
      // Handle the direct API response format
      const userData = (profile as any)?.user || profile
      console.log('🔐 AuthContext: Extracted system user:', userData)
      
      return userData as SystemUser
    } catch (error) {
      console.error('🔐 AuthContext: Error fetching system user:', error)
      
      // Check if it's an authentication error
      const isAuthError = error && typeof error === 'object' && 'status' in error && 
                         ((error as any).status === 401 || (error as any).status === 422)
      
      if (isAuthError) {
        console.log('🔐 AuthContext: Authentication error detected, clearing tokens')
        setTokens(null, null)
        setSession(null)
        setUser(null)
        setSystemUser(null)
        
        // Show user-friendly message
        toast({
          title: "Session Expired",
          description: "Please sign in again to continue.",
          variant: "destructive"
        })
      }
      return null
    }
  }

  const refreshSystemUser = async () => {
    const token = getAccessToken()
    if (user && token) {
      const systemUserData = await fetchSystemUser(user.id)
      setSystemUser(systemUserData)
    } else {
      console.log('🔐 AuthContext: Cannot refresh - no user or token')
    }
  }

  useEffect(() => {
    debugSystemUsersTable()

    // Bootstrap from stored tokens (JWT from Flask backend)
    ;(async () => {
      try {
        console.log('🔐 AuthContext: Starting auth bootstrap...')
        const access = getAccessToken()
        const refresh = getRefreshToken()
        
        if (access && access.trim() !== '') {
          console.log('🔐 AuthContext: Found stored token, validating...')
          setSession({ access_token: access })
          
          try {
            // Set provisional user immediately so UI can react
            setUser({ id: 'self', email: null })
            const systemUserData = await fetchSystemUser('self')
            console.log('🔐 AuthContext: Initial system user fetch result:', systemUserData)
            
            if (systemUserData) {
              setSystemUser(systemUserData)
              setUser({ id: systemUserData?.auth_user_id || 'self', email: systemUserData?.email })
              console.log('🔐 AuthContext: Successfully authenticated from stored token')
            } else {
              // Token is invalid, clear everything
              console.log('🔐 AuthContext: Stored token is invalid, clearing session')
              setUser(null)
              setSession(null)
              setSystemUser(null)
              setTokens(null, null)
            }
          } catch (error) {
            console.error('🔐 AuthContext: Error validating stored token:', error)
            setSystemUser(null)
            setUser(null)
            setSession(null)
            setTokens(null, null)
          }
        } else {
          console.log('🔐 AuthContext: No stored token found, starting fresh')
          setSession(null)
          setUser(null)
          setSystemUser(null)
        }
      } catch (err) {
        console.error('🔐 AuthContext: Auth bootstrap failed:', err)
        setSession(null)
        setUser(null)
        setSystemUser(null)
        setTokens(null, null)
      } finally {
        setLoading(false)
      }
    })()

    // Listen for auth changes
    // Handle OAuth popup postMessage from backend callback
    const onMessage = async (event: MessageEvent) => {
      const data = event.data as any
      if (data && data.type === 'oauth' && data.access_token) {
        try {
          setTokens(data.access_token, data.refresh_token || null)
          setSession({ access_token: data.access_token })
          setUser({ id: 'self', email: null })
          const sys = await fetchSystemUser('self')
          setSystemUser(sys)
          setUser({ id: sys?.auth_user_id || 'self', email: sys?.email })
        } catch (e) {
          console.error('OAuth message handling failed:', e)
        }
      }
    }
    if (typeof window !== 'undefined') {
      window.addEventListener('message', onMessage)
    }
    return () => {
      if (typeof window !== 'undefined') {
        window.removeEventListener('message', onMessage)
      }
    }
  }, [])

  const signUp = async (email: string, password: string, username: string, role: string = 'Analyst') => {
    try {
      const data = await apiClient.signUp(email, password, username, role)
      return { data, error: null }
    } catch (error: any) {
      console.error('Signup error:', error)
      console.error('Error data:', error?.data)
      console.error('Error message:', error?.message)
      // Extract the actual error message from the backend response
      const errorMessage = error?.data?.error || error?.message || 'Sign up failed'
      console.error('Extracted error message:', errorMessage)
      return { data: null, error: { message: errorMessage } }
    }
  }

  const signIn = async (email: string, password: string) => {
    try {
      console.log('🔐 AuthContext: Starting sign in for:', email)
      const data = await apiClient.signIn(email, password)
      console.log('🔐 AuthContext: Raw login data received:', data)
      // Store tokens
      setTokens((data as any)?.access_token || null, (data as any)?.refresh_token || null)
      setSession({ access_token: (data as any)?.access_token || null })
      // Provisional user immediately
      setUser({ id: 'self', email })
      toast({ title: 'Signed in', description: 'You are now logged in.' })
      try {
          const sys = await fetchSystemUser('self')
        setSystemUser(sys)
        setUser({ id: sys?.auth_user_id || 'self', email: sys?.email })
        
        // Return user data for role-based redirect - use original login data if sys fails
        return { data: { user: sys || (data as any)?.user, access_token: (data as any)?.access_token }, error: null }
      } catch (fetchError) {
        console.error('Failed to fetch system user:', fetchError)
        // Return the original login data instead of null
        return { data: { user: (data as any)?.user, access_token: (data as any)?.access_token }, error: null }
      }
    } catch (error) {
      console.error('❌ AuthContext: Sign in exception:', error)
      // Provide more specific error message for 401
      const errorMessage = error && typeof error === 'object' && 'message' in error 
        ? (error as any).message 
        : String(error)
      
      if (errorMessage.includes('HTTP 401')) {
        const friendlyError = new Error('Invalid email or password. Please check your credentials.')
        return { data: null, error: friendlyError }
      }
      
      return { data: null, error }
    }
  }

  const signOut = async () => {
    console.log('🔐 AuthContext: Signing out user')
    setTokens(null, null)
    setSession(null)
    setUser(null)
    setSystemUser(null)
    
    // Show success message
    toast({
      title: "Signed Out",
      description: "You have been successfully signed out.",
    })
  }

  const clearAuthState = () => {
    console.log('🔐 AuthContext: Clearing authentication state')
    setTokens(null, null)
    setSession(null)
    setUser(null)
    setSystemUser(null)
    
    // Show message
    toast({
      title: "Authentication Cleared",
      description: "Please sign in again to continue.",
      variant: "destructive"
    })
  }

  const value = {
    user,
    systemUser,
    session,
    loading,
    signUp,
    signIn,
    signOut,
    refreshSystemUser,
    clearAuthState
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}


