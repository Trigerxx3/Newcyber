'use client'

import { useState } from 'react'

export default function ApiTestPage() {
  const [result, setResult] = useState('')
  const [loading, setLoading] = useState(false)

  const testDirect = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://127.0.0.1:5000/health', {
        method: 'GET',
        mode: 'cors'
      })
      const data = await response.json()
      setResult(`✅ Direct test success: ${JSON.stringify(data, null, 2)}`)
    } catch (error) {
      setResult(`❌ Direct test failed: ${error}`)
    }
    setLoading(false)
  }

  const testViaApiClient = async () => {
    setLoading(true)
    try {
      const { apiClient } = await import('@/lib/api')
      const data = await apiClient.healthCheck()
      setResult(`✅ API client success: ${JSON.stringify(data, null, 2)}`)
    } catch (error) {
      setResult(`❌ API client failed: ${error}`)
    }
    setLoading(false)
  }

  return (
    <div className="p-8">
      <h1 className="text-2xl mb-4">API Connection Test</h1>
      
      <div className="space-y-4">
        <button 
          onClick={testDirect}
          disabled={loading}
          className="px-4 py-2 bg-blue-500 text-white rounded mr-4"
        >
          Test Direct Fetch
        </button>
        
        <button 
          onClick={testViaApiClient}
          disabled={loading}
          className="px-4 py-2 bg-green-500 text-white rounded"
        >
          Test Via API Client
        </button>
      </div>

      {result && (
        <pre className="mt-4 p-4 bg-gray-100 rounded text-sm overflow-auto">
          {result}
        </pre>
      )}

      <div className="mt-4 text-sm text-gray-600">
        <p>Environment: {process.env.NEXT_PUBLIC_API_URL || 'Not set'}</p>
        <p>Node ENV: {process.env.NODE_ENV}</p>
      </div>
    </div>
  )
} 
