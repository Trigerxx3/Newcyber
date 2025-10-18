'use client'

import { useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

export default function TestLoginPage() {
  const { signIn, user, systemUser, loading } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [testResults, setTestResults] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const testCredentials = [
    { email: 'admin@cyber.com', password: 'admin123456', role: 'Admin' },
    { email: 'analyst@cyber.com', password: 'analyst123456', role: 'Analyst' }
  ]

  const testLogin = async (testEmail: string, testPassword: string, expectedRole: string) => {
    setIsLoading(true)
    const startTime = Date.now()
    
    try {
      console.log(`🧪 Testing login for ${testEmail}`)
      
      const result = await signIn(testEmail, testPassword)
      const duration = Date.now() - startTime
      
      if (result.error) {
        setTestResults(prev => [...prev, {
          email: testEmail,
          success: false,
          error: result.error.message,
          duration,
          timestamp: new Date().toISOString()
        }])
      } else {
        setTestResults(prev => [...prev, {
          email: testEmail,
          success: true,
          user: result.data?.user,
          expectedRole,
          duration,
          timestamp: new Date().toISOString()
        }])
      }
    } catch (error) {
      const duration = Date.now() - startTime
      setTestResults(prev => [...prev, {
        email: testEmail,
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        duration,
        timestamp: new Date().toISOString()
      }])
    } finally {
      setIsLoading(false)
    }
  }

  const runAllTests = async () => {
    setTestResults([])
    for (const cred of testCredentials) {
      await testLogin(cred.email, cred.password, cred.role)
      await new Promise(resolve => setTimeout(resolve, 1000)) // Wait between tests
    }
  }

  const manualLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    await testLogin(email, password, 'Unknown')
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Authentication Test Suite
          </h1>
          <p className="text-gray-600">
            Test your login functionality end-to-end
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          {/* Current User Status */}
          <Card>
            <CardHeader>
              <CardTitle>Current User Status</CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <p>Loading...</p>
              ) : user ? (
                <div className="space-y-2">
                  <p><strong>Email:</strong> {user.email}</p>
                  <p><strong>Auth ID:</strong> {user.id}</p>
                  {systemUser && (
                    <>
                      <p><strong>Username:</strong> {systemUser.username}</p>
                      <p><strong>Role:</strong> 
                        <Badge className="ml-2">{systemUser.role}</Badge>
                      </p>
                      <p><strong>Last Login:</strong> {systemUser.last_login || 'Never'}</p>
                    </>
                  )}
                </div>
              ) : (
                <p className="text-gray-500">Not logged in</p>
              )}
            </CardContent>
          </Card>

          {/* Manual Login Test */}
          <Card>
            <CardHeader>
              <CardTitle>Manual Login Test</CardTitle>
              <CardDescription>Test login with custom credentials</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={manualLogin} className="space-y-4">
                <Input
                  type="email"
                  placeholder="Email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
                <Input
                  type="password"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                <Button type="submit" disabled={isLoading} className="w-full">
                  {isLoading ? 'Testing...' : 'Test Login'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Automated Tests */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Automated Login Tests</CardTitle>
            <CardDescription>Test all predefined credentials</CardDescription>
          </CardHeader>
          <CardContent>
            <Button 
              onClick={runAllTests} 
              disabled={isLoading}
              className="mb-4"
            >
              {isLoading ? 'Running Tests...' : 'Run All Tests'}
            </Button>

            {testResults.length > 0 && (
              <div className="space-y-4">
                <h4 className="font-semibold">Test Results:</h4>
                {testResults.map((result, index) => (
                  <div key={index} className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">{result.email}</span>
                      <Badge variant={result.success ? "default" : "destructive"}>
                        {result.success ? 'PASS' : 'FAIL'}
                      </Badge>
                    </div>
                    
                    {result.success ? (
                      <div className="text-sm text-green-600">
                        <p>✅ Login successful ({result.duration}ms)</p>
                        <p>User ID: {result.user?.id}</p>
                        <p>Expected Role: {result.expectedRole}</p>
                      </div>
                    ) : (
                      <div className="text-sm text-red-600">
                        <p>❌ Login failed: {result.error}</p>
                        <p>Duration: {result.duration}ms</p>
                      </div>
                    )}
                    
                    <p className="text-xs text-gray-500 mt-2">
                      {new Date(result.timestamp).toLocaleString()}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Test Credentials Reference */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Test Credentials</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              {testCredentials.map((cred, index) => (
                <div key={index} className="p-4 bg-gray-50 rounded-lg">
                  <h4 className="font-semibold mb-2">{cred.role} Account</h4>
                  <p className="text-sm">
                    <strong>Email:</strong> {cred.email}<br/>
                    <strong>Password:</strong> {cred.password}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}