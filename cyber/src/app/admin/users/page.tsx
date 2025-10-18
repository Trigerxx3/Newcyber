'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
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
import { Label } from '@/components/ui/label'
import { 
  Plus, 
  Search, 
  Edit, 
  Trash2, 
  UserCheck, 
  UserX,
  Key,
  Shield,
  Activity,
  Lock,
  Chrome
} from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api'
import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'

interface User {
  id: string
  username: string
  email: string
  role: 'Admin' | 'Analyst'
  isActive: boolean
  lastLogin: string
  createdAt: string
  casesAssigned: number
  signInMethod: 'password' | 'google' | 'unknown'
  googleId?: string
  emailVerified?: boolean
}

export default function UserManagement() {
  const { toast } = useToast()
  const { systemUser } = useAuth()
  const router = useRouter()
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedRole, setSelectedRole] = useState<string>('all')
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [newUser, setNewUser] = useState({
    username: '',
    email: '',
    role: 'Analyst' as 'Admin' | 'Analyst'
  })

  // Real-time validation states
  const [validationErrors, setValidationErrors] = useState({
    username: '',
    email: ''
  })

  // Delete user state
  const [userToDelete, setUserToDelete] = useState<User | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)

  // Check if user is admin
  useEffect(() => {
    if (systemUser && systemUser.role !== 'Admin') {
      toast({
        title: 'Access Denied',
        description: 'You must be an admin to access this page.',
        variant: 'destructive'
      })
      router.push('/dashboard')
      return
    }
  }, [systemUser, router, toast])

  useEffect(() => {
    loadUsers()
  }, [])

  // Real-time validation function
  const validateField = (field: 'username' | 'email', value: string) => {
    let error = ''
    
    if (field === 'email') {
      if (value) {
        // Check email format
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        if (!emailRegex.test(value)) {
          error = 'Invalid email format'
        } else {
          // Check for duplicate email
          const existingUser = users.find(user => 
            user.email.toLowerCase() === value.toLowerCase()
          )
          if (existingUser) {
            error = `Email already used by ${existingUser.username}`
          }
        }
      }
    } else if (field === 'username') {
      if (value) {
        // Check for duplicate username
        const existingUser = users.find(user => 
          user.username.toLowerCase() === value.toLowerCase()
        )
        if (existingUser) {
          error = 'Username already taken'
        }
      }
    }
    
    setValidationErrors(prev => ({
      ...prev,
      [field]: error
    }))
    
    return error === ''
  }

  const loadUsers = async () => {
    try {
      setLoading(true)
      
      // Check if we have a valid token first
      const token = localStorage.getItem('access_token')
      console.log('🔐 Admin: Checking token...', token ? 'Token found' : 'No token')
      
      if (!token) {
        console.log('🔐 Admin: No token found, user needs to login')
        throw new Error('No authentication token found. Please log in again.')
      }
      
      console.log('🔐 Admin: Making API call to getSystemUsers...')
      // Fetch real users from the API
      const response: any = await apiClient.getSystemUsers()
      console.log('🔍 Raw users API response:', response)
      
      // Handle the response structure - API returns { value: [...], Count: 5 }
      const usersData = response?.value || response || []
      console.log('🔍 Extracted users data:', usersData)
      
      // Transform API response to match User interface
      const transformedUsers: User[] = usersData.map((user: any) => ({
        id: user.id.toString(),
        username: user.username,
        email: user.email,
        role: user.role,
        isActive: user.is_active,
        // Backend now returns pre-formatted timestamps, use as-is
        lastLogin: user.last_login || 'Never',
        createdAt: user.created_at || 'Unknown',
        casesAssigned: user.cases_assigned || 0,
        signInMethod: user.sign_in_method || 'unknown',
        googleId: user.google_id || undefined,
        emailVerified: user.email_verified
      }))
      
      console.log('🔍 Transformed users:', transformedUsers)
      setUsers(transformedUsers)
      
      toast({
        title: 'Success',
        description: `Loaded ${transformedUsers.length} users successfully`,
        variant: 'default'
      })
    } catch (error: any) {
      console.error('❌ Failed to load users:', error)
      
      let errorMessage = 'Failed to load users from server. Check console for details.'
      
      // Handle specific error types
      if (error.message?.includes('No authentication token')) {
        errorMessage = 'Please log in as an admin to access this page.'
      } else if (error.message?.includes('401') || error.message?.includes('Unauthorized')) {
        errorMessage = 'You are not authorized to access this page. Please log in as an admin.'
      } else if (error.message?.includes('Failed to fetch')) {
        errorMessage = 'Cannot connect to the backend server. Please check if it is running.'
      }
      
      toast({
        title: 'Error',
        description: errorMessage,
        variant: 'destructive'
      })
      // Set empty state on error
      setUsers([])
    } finally {
      setLoading(false)
    }
  }

  const handleCreateUser = async () => {
    try {
      if (!newUser.username || !newUser.email) {
        toast({
          title: 'Validation Error',
          description: 'Please fill in username and email',
          variant: 'destructive'
        })
        return
      }

      // Client-side validation for duplicates
      const existingUserByEmail = users.find(user => 
        user.email.toLowerCase() === newUser.email.toLowerCase()
      )
      if (existingUserByEmail) {
        toast({
          title: 'Email Already Registered',
          description: `The email "${newUser.email}" is already associated with user "${existingUserByEmail.username}". Please use a different email address.`,
          variant: 'destructive',
          duration: 6000
        })
        return
      }

      const existingUserByUsername = users.find(user => 
        user.username.toLowerCase() === newUser.username.toLowerCase()
      )
      if (existingUserByUsername) {
        toast({
          title: 'Username Not Available',
          description: `The username "${newUser.username}" is already taken. Please choose a different username.`,
          variant: 'destructive',
          duration: 6000
        })
        return
      }

      // Basic email format validation
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailRegex.test(newUser.email)) {
        toast({
          title: 'Invalid Email Format',
          description: 'Please enter a valid email address (e.g., user@example.com)',
          variant: 'destructive'
        })
        return
      }

      console.log('🔐 Creating user (admin action):', newUser)

      // Generate a temporary strong password (8-12 chars)
      const tempPassword = Math.random().toString(36).slice(-8) + 'A1!'

      // Use general signup endpoint to create a system user
      const response: any = await apiClient.signUp(
        newUser.email,
        tempPassword,
        newUser.username,
        newUser.role
      )

      console.log('🔐 User creation response:', response)

      // Map minimal response to local User shape with sensible defaults
      const created = response?.user || response?.data?.user || {}
      const user: User = {
        id: String(
          created.id ?? (
            typeof crypto !== 'undefined' && 'randomUUID' in crypto
              ? (crypto as any).randomUUID()
              : Math.random().toString(36).slice(2)
          )
        ),
        username: created.username ?? newUser.username,
        email: created.email ?? newUser.email,
        role: created.role ?? newUser.role,
        isActive: true,
        lastLogin: 'Never',
        createdAt: new Date().toLocaleDateString(),
        casesAssigned: 0,
        emailVerified: true,
        signInMethod: 'password'
      }

      setUsers(prev => [...prev, user])
      setShowCreateDialog(false)
      setNewUser({ username: '', email: '', role: 'Analyst' })
      setValidationErrors({ username: '', email: '' })

      toast({
        title: 'User Created',
        description: `User ${user.username} created successfully. A temporary password was set.`,
        duration: 6000
      })
      
      // Refresh users list to get updated data
      loadUsers()
      
    } catch (error: any) {
      console.error('Failed to create user:', error)
      
      // Handle specific validation errors with better messaging
      let title = 'Error'
      let description = error.message || 'Failed to create user'
      
      if (error.message?.includes('email already exists')) {
        title = 'Email Already Registered'
        description = `The email "${newUser.email}" is already associated with another user account. Please use a different email address.`
      } else if (error.message?.includes('Username already taken')) {
        title = 'Username Not Available'
        description = `The username "${newUser.username}" is already taken. Please choose a different username.`
      } else if (error.message?.includes('Invalid email format')) {
        title = 'Invalid Email'
        description = `Please enter a valid email address. Example: user@example.com`
      } else if (error.message?.includes('Username and email are required')) {
        title = 'Missing Information'
        description = 'Both username and email are required to create a user account.'
      } else if (error.message?.includes('Missing Authorization Header') || error.message?.includes('Invalid credentials')) {
        title = 'Authentication Required'
        description = 'Please log in as an admin to create user accounts.'
      }
      
      toast({
        title,
        description,
        variant: 'destructive',
        duration: 6000 // Show longer for important validation messages
      })
    }
  }

  const handleToggleUserStatus = async (userId: string) => {
    try {
      const target = users.find(u => u.id === userId)
      const resp: any = await apiClient.toggleSystemUserActive(userId)
      const isActive = resp?.isActive ?? !target?.isActive
      setUsers(prev => prev.map(user => user.id === userId ? { ...user, isActive } : user))
      toast({
        title: 'Success',
        description: `User ${target?.username} ${isActive ? 'activated' : 'deactivated'}`
      })
    } catch (error) {
      console.error('Failed to toggle user status:', error)
      toast({
        title: 'Error',
        description: 'Failed to update user status. Please try again.',
        variant: 'destructive'
      })
    }
  }

  const handleDeleteUser = async () => {
    if (!userToDelete) return
    
    try {
      setIsDeleting(true)
      
      console.log(`🗑️ Deleting user: ${userToDelete.username} (ID: ${userToDelete.id})`)
      
      // Deletion endpoint is not implemented in API client/backend yet.
      // For now, show a clear message and avoid runtime errors.
      toast({
        title: 'Not Implemented',
        description: 'User deletion is not available in this build.',
        variant: 'destructive',
        duration: 5000
      })
      // Optional: If you want to remove locally (UI only), uncomment below
      // setUsers(prev => prev.filter(user => user.id !== userToDelete.id))
      // setUserToDelete(null)
      
    } catch (error: any) {
      console.error('Failed to delete user:', error)
      
      let title = 'Delete Failed'
      let description = error.message || 'Failed to delete user'
      
      if (error.message?.includes('Cannot delete your own account')) {
        title = 'Cannot Delete Own Account'
        description = 'You cannot delete your own account. Please ask another admin to perform this action.'
      } else if (error.message?.includes('User not found')) {
        title = 'User Not Found'
        description = 'This user may have already been deleted or does not exist.'
      }
      
      toast({
        title,
        description,
        variant: 'destructive',
        duration: 6000
      })
    } finally {
      setIsDeleting(false)
    }
  }

  const filteredUsers = users.filter(user => {
    const matchesSearch = (user.username && user.username.toLowerCase().includes(searchTerm.toLowerCase())) ||
                         (user.email && user.email.toLowerCase().includes(searchTerm.toLowerCase()))
    const matchesRole = selectedRole === 'all' || user.role === selectedRole
    return matchesSearch && matchesRole
  })

  const stats = {
    total: users.length,
    active: users.filter(u => u.isActive).length,
    admins: users.filter(u => u.role === 'Admin').length,
    analysts: users.filter(u => u.role === 'Analyst').length
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">User & Access Management</h1>
          <p className="text-gray-400">Manage analyst accounts and permissions</p>
        </div>
        
        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogTrigger asChild>
            <Button className="bg-blue-500 hover:bg-blue-600">
              <Plus className="h-4 w-4 mr-2" />
              Create User
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-black border-white/20">
            <DialogHeader>
              <DialogTitle className="text-white">Create New User</DialogTitle>
              <DialogDescription className="text-gray-400">
                Add a new analyst or admin account. A verification email will be sent for password setup.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="username" className="text-white">Username</Label>
                <Input
                  id="username"
                  value={newUser.username}
                  onChange={(e) => {
                    const value = e.target.value
                    setNewUser(prev => ({ ...prev, username: value }))
                    validateField('username', value)
                  }}
                  className={`bg-white/10 border-white/20 text-white ${
                    validationErrors.username ? 'border-red-400 focus:border-red-400' : ''
                  }`}
                  placeholder="Enter username"
                />
                {validationErrors.username && (
                  <p className="text-red-400 text-sm mt-1">{validationErrors.username}</p>
                )}
              </div>
              <div>
                <Label htmlFor="email" className="text-white">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={newUser.email}
                  onChange={(e) => {
                    const value = e.target.value
                    setNewUser(prev => ({ ...prev, email: value }))
                    validateField('email', value)
                  }}
                  className={`bg-white/10 border-white/20 text-white ${
                    validationErrors.email ? 'border-red-400 focus:border-red-400' : ''
                  }`}
                  placeholder="Enter email address"
                />
                {validationErrors.email && (
                  <p className="text-red-400 text-sm mt-1">{validationErrors.email}</p>
                )}
              </div>
              <div>
                <Label htmlFor="role" className="text-white">Role</Label>
                <Select 
                  value={newUser.role} 
                  onValueChange={(value: 'Admin' | 'Analyst') => setNewUser(prev => ({ ...prev, role: value }))}
                >
                  <SelectTrigger className="bg-white/10 border-white/20 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-black border-white/20">
                    <SelectItem value="Analyst">Analyst</SelectItem>
                    <SelectItem value="Admin">Admin</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => {
                setShowCreateDialog(false)
                setNewUser({ username: '', email: '', role: 'Analyst' })
                setValidationErrors({ username: '', email: '' })
              }}>
                Cancel
              </Button>
              <Button 
                onClick={handleCreateUser} 
                disabled={
                  !newUser.username || 
                  !newUser.email || 
                  validationErrors.username !== '' || 
                  validationErrors.email !== ''
                }
                className="bg-blue-500 hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Create User
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-white/5 border-white/10">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-400">Total Users</CardTitle>
            <Shield className="h-4 w-4 text-blue-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{stats.total}</div>
          </CardContent>
        </Card>

        <Card className="bg-white/5 border-white/10">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-400">Active Users</CardTitle>
            <UserCheck className="h-4 w-4 text-green-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{stats.active}</div>
          </CardContent>
        </Card>

        <Card className="bg-white/5 border-white/10">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-400">Admins</CardTitle>
            <Key className="h-4 w-4 text-red-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{stats.admins}</div>
          </CardContent>
        </Card>

        <Card className="bg-white/5 border-white/10">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-400">Analysts</CardTitle>
            <Activity className="h-4 w-4 text-purple-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{stats.analysts}</div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card className="bg-white/5 border-white/10">
        <CardHeader>
          <CardTitle className="text-white">User Management</CardTitle>
          <CardDescription className="text-gray-400">
            Search and filter user accounts
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 mb-6">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search users..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 bg-white/10 border-white/20 text-white"
                />
              </div>
            </div>
            <Select value={selectedRole} onValueChange={setSelectedRole}>
              <SelectTrigger className="w-40 bg-white/10 border-white/20 text-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-black border-white/20">
                <SelectItem value="all">All Roles</SelectItem>
                <SelectItem value="Admin">Admin</SelectItem>
                <SelectItem value="Analyst">Analyst</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Users Table */}
          <div className="rounded-lg border border-white/10 overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow className="border-white/10">
                  <TableHead className="text-gray-400">User</TableHead>
                  <TableHead className="text-gray-400">Role</TableHead>
                  <TableHead className="text-gray-400">Status</TableHead>
                  <TableHead className="text-gray-400">Email Verified</TableHead>
                  <TableHead className="text-gray-400">Sign-in Method</TableHead>
                  <TableHead className="text-gray-400">Last Login</TableHead>
                  <TableHead className="text-gray-400">Cases</TableHead>
                  <TableHead className="text-gray-400">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading ? (
                  [...Array(4)].map((_, i) => (
                    <TableRow key={i} className="border-white/10">
                      <TableCell colSpan={7}>
                        <div className="animate-pulse flex space-x-4">
                          <div className="rounded-full bg-white/10 h-8 w-8"></div>
                          <div className="flex-1 space-y-2">
                            <div className="h-4 bg-white/10 rounded w-3/4"></div>
                            <div className="h-3 bg-white/10 rounded w-1/2"></div>
                          </div>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  filteredUsers.map((user) => {
                    const getSignInMethodIcon = (method: string) => {
                      switch (method) {
                        case 'google':
                          return <Chrome className="h-4 w-4 text-blue-400" />
                        case 'password':
                          return <Lock className="h-4 w-4 text-gray-400" />
                        default:
                          return <Key className="h-4 w-4 text-gray-500" />
                      }
                    }
                    
                    const getSignInMethodLabel = (method: string) => {
                      switch (method) {
                        case 'google':
                          return 'Google OAuth'
                        case 'password':
                          return 'Password'
                        default:
                          return 'Unknown'
                      }
                    }
                    
                    return (
                      <TableRow key={user.id} className="border-white/10">
                        <TableCell>
                          <div>
                            <div className="font-medium text-white">{user.username}</div>
                            <div className="text-sm text-gray-400">{user.email}</div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge 
                            variant="outline" 
                            className={user.role === 'Admin' ? 
                              "text-red-400 border-red-400/50" : 
                              "text-blue-400 border-blue-400/50"
                            }
                          >
                            {user.role}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge 
                            variant="outline" 
                            className={user.isActive ? 
                              "text-green-400 border-green-400/50" : 
                              "text-red-400 border-red-400/50"
                            }
                          >
                            {user.isActive ? 'Active' : 'Inactive'}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge 
                            variant="outline" 
                            className={user.emailVerified !== false ? 
                              "text-green-400 border-green-400/50" : 
                              "text-yellow-400 border-yellow-400/50"
                            }
                          >
                            {user.emailVerified !== false ? 'Verified' : 'Pending'}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            {getSignInMethodIcon(user.signInMethod)}
                            <span className="text-sm text-gray-400">
                              {getSignInMethodLabel(user.signInMethod)}
                            </span>
                          </div>
                        </TableCell>
                        <TableCell className="text-gray-400">{user.lastLogin}</TableCell>
                        <TableCell className="text-gray-400">{user.casesAssigned}</TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button variant="ghost" size="sm">
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button 
                              variant="ghost" 
                              size="sm"
                              onClick={() => handleToggleUserStatus(user.id)}
                            >
                              {user.isActive ? (
                                <UserX className="h-4 w-4 text-red-400" />
                              ) : (
                                <UserCheck className="h-4 w-4 text-green-400" />
                              )}
                            </Button>
                            <Button 
                              variant="ghost" 
                              size="sm"
                              onClick={() => setUserToDelete(user)}
                              className="text-red-400 hover:text-red-300"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    )
                  })
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* Delete User Confirmation Dialog */}
      <AlertDialog open={!!userToDelete} onOpenChange={() => setUserToDelete(null)}>
        <AlertDialogContent className="bg-black border-white/20">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-white flex items-center gap-2">
              <Trash2 className="h-5 w-5 text-red-400" />
              Delete User Account
            </AlertDialogTitle>
            <AlertDialogDescription className="text-gray-400">
              This action cannot be undone. This will permanently delete the user account and remove all associated data from the system.
            </AlertDialogDescription>
          </AlertDialogHeader>
          
          {userToDelete && (
            <div className="bg-red-400/10 border border-red-400/20 rounded-lg p-4 my-4">
              <h4 className="text-red-400 font-medium mb-2">User to be deleted:</h4>
              <div className="text-sm text-gray-300 space-y-1">
                <p><strong>Username:</strong> {userToDelete.username}</p>
                <p><strong>Email:</strong> {userToDelete.email}</p>
                <p><strong>Role:</strong> {userToDelete.role}</p>
                <p><strong>Status:</strong> {userToDelete.isActive ? 'Active' : 'Inactive'}</p>
                <p><strong>Email Verified:</strong> {userToDelete.emailVerified !== false ? 'Yes' : 'No'}</p>
              </div>
            </div>
          )}
          
          <AlertDialogFooter>
            <AlertDialogCancel 
              className="bg-white/10 border-white/20 text-white hover:bg-white/20"
              disabled={isDeleting}
            >
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction 
              className="bg-red-500 hover:bg-red-600 text-white"
              onClick={handleDeleteUser}
              disabled={isDeleting}
            >
              {isDeleting ? (
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  Deleting...
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <Trash2 className="h-4 w-4" />
                  Delete User
                </div>
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}