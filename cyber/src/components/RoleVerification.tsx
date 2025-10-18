'use client'

import { useAuth } from '@/contexts/AuthContext'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

export default function RoleVerification() {
  const { user, systemUser, signOut } = useAuth()

  const adminFeatures = [
    'View all users',
    'Manage system settings',
    'Access admin dashboard',
    'Create/delete users'
  ]

  const analystFeatures = [
    'View intelligence data',
    'Create reports',
    'Access analyst tools',
    'View assigned sources'
  ]

  const testRoleAccess = () => {
    if (!systemUser) return

    console.log('🔐 Testing Role Access...')
    console.log('Current Role:', systemUser.role)
    
    if (systemUser.role === 'Admin') {
      console.log('✅ Admin features available:', adminFeatures)
    } else if (systemUser.role === 'Analyst') {
      console.log('✅ Analyst features available:', analystFeatures)
    }
  }

  if (!user || !systemUser) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-center text-gray-500">Please log in to verify roles</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Role & Permission Verification</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <span>Current User:</span>
          <Badge variant="outline">{systemUser.username}</Badge>
        </div>
        
        <div className="flex items-center justify-between">
          <span>Role:</span>
          <Badge variant={systemUser.role === 'Admin' ? 'default' : 'secondary'}>
            {systemUser.role}
          </Badge>
        </div>
        
        <div className="flex items-center justify-between">
          <span>Email:</span>
          <span className="text-sm">{user.email}</span>
        </div>
        
        <div className="pt-4 border-t">
          <h4 className="font-semibold mb-2">Available Features:</h4>
          <ul className="text-sm space-y-1">
            {(systemUser.role === 'Admin' ? adminFeatures : analystFeatures).map((feature, index) => (
              <li key={index} className="flex items-center">
                <span className="text-green-500 mr-2">✓</span>
                {feature}
              </li>
            ))}
          </ul>
        </div>
        
        <div className="flex gap-2 pt-4">
          <Button onClick={testRoleAccess} variant="outline" size="sm">
            Test Role Access
          </Button>
          <Button onClick={signOut} variant="destructive" size="sm">
            Sign Out
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}