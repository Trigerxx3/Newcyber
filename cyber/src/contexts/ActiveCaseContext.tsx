'use client'

import React, { createContext, useContext, useEffect, useState } from 'react'
import apiClient from '@/lib/api'

type ActiveCase = any | null

interface ActiveCaseContextType {
  activeCase: ActiveCase
  setActiveCase: (caseId: number) => Promise<void>
  clearActiveCase: () => Promise<void>
  refreshActiveCase: () => Promise<void>
  loading: boolean
}

const ActiveCaseContext = createContext<ActiveCaseContextType | undefined>(undefined)

export function ActiveCaseProvider({ children }: { children: React.ReactNode }) {
  const [activeCase, setActiveCaseState] = useState<ActiveCase>(null)
  const [loading, setLoading] = useState(true)

  const refreshActiveCase = async () => {
    try {
      const res = await apiClient.getActiveCase()
      const data = (res as any)?.data
      setActiveCaseState(data || null)
      if (typeof window !== 'undefined') {
        localStorage.setItem('active_case', data ? JSON.stringify(data) : '')
      }
    } catch (e) {
      // ignore
    }
  }

  useEffect(() => {
    (async () => {
      // bootstrap from localStorage quickly
      if (typeof window !== 'undefined') {
        const raw = localStorage.getItem('active_case')
        if (raw) {
          try { setActiveCaseState(JSON.parse(raw)) } catch {}
        }
      }
      await refreshActiveCase()
      setLoading(false)
    })()
  }, [])

  const setActiveCase = async (caseId: number) => {
    await apiClient.setActiveCase(caseId)
    await refreshActiveCase()
  }

  const clearActiveCase = async () => {
    await apiClient.clearActiveCase()
    setActiveCaseState(null)
    if (typeof window !== 'undefined') localStorage.removeItem('active_case')
  }

  return (
    <ActiveCaseContext.Provider value={{ activeCase, setActiveCase, clearActiveCase, refreshActiveCase, loading }}>
      {children}
    </ActiveCaseContext.Provider>
  )
}

export function useActiveCase() {
  const ctx = useContext(ActiveCaseContext)
  if (!ctx) throw new Error('useActiveCase must be used within ActiveCaseProvider')
  return ctx
}


