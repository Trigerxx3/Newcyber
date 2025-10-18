'use server'

// SQLAlchemy-only data interfaces
// All data operations now go through Flask backend APIs

export interface AnalysisData {
  riskResult: {
    riskLevel: 'Low' | 'Medium' | 'High'
    score: number
    reasons: string[]
  }
  content: string
  platform: string
  timestamp: string
  userId?: string
  metadata?: any
}

export interface SuspectedUserData {
  username: string
  platform: string
  analysisResult: {
    username: string
    platform: string
    linkedProfiles: string[]
    email: string | null
    riskLevel: 'Low' | 'Medium' | 'High' | 'Critical'
    summary: string
    toolsUsed: string[]
    totalProfilesFound: number
    confidenceLevel: 'low' | 'medium' | 'high'
  }
}

// All data operations now handled by Flask backend
export async function saveAnalysisData(_data: AnalysisData) {
  console.warn('Data operations now handled by Flask backend API endpoints.')
  return { success: true, message: 'Use Flask backend /api/content endpoints' }
}

export async function saveSuspectedUserData(_data: SuspectedUserData) {
  console.warn('Data operations now handled by Flask backend API endpoints.')
  return { success: true, message: 'Use Flask backend /api/users endpoints' }
}

export async function getDashboardData() {
  try {
    // Dashboard now uses Flask endpoints directly in pages
    return { flaggedPosts: [], suspectedUsers: [], stats: { riskLevelCounts: {}, platformCounts: {}, keywordCounts: {} } }
  } catch (error) {
    console.error('Error fetching dashboard data:', error)
    return {
      flaggedPosts: [],
      suspectedUsers: [],
      stats: {
        riskLevelCounts: {},
        platformCounts: {},
        keywordCounts: {},
      }
    }
  }
}

export async function seedDatabase() {
  return { success: true, message: 'Database seeding handled by Flask backend' }
}

export async function isDatabaseConfigured(): Promise<boolean> { 
  // Check if Flask backend is configured and accessible
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/health`)
    const data = await response.json()
    return data.database_connected === true
  } catch {
    return false
  }
}
