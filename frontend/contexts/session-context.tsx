"use client"

import React, { createContext, useContext, useEffect, useState } from 'react'
import { createSession } from '@/lib/api'

const SESSION_STORAGE_KEY = 'summarizer_session_id'

interface SessionContextType {
  sessionId: string | null
  loading: boolean
  error: string | null
  createNewSession: () => Promise<string>
  clearSession: () => void
}

const SessionContext = createContext<SessionContextType | undefined>(undefined)

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const createNewSession = async (): Promise<string> => {
    setLoading(true)
    setError(null)
    try {
      const id = await createSession()
      setSessionId(id)
      localStorage.setItem(SESSION_STORAGE_KEY, id)
      return id
    } catch (e: any) {
      const errorMsg = e?.message || 'Failed to create session'
      setError(errorMsg)
      throw new Error(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  const clearSession = () => {
    setSessionId(null)
    setError(null)
    localStorage.removeItem(SESSION_STORAGE_KEY)
  }

  // Load session from localStorage on mount, or create new one
  useEffect(() => {
    // Try to load existing session from localStorage
    const storedSessionId = localStorage.getItem(SESSION_STORAGE_KEY)
    if (storedSessionId) {
      setSessionId(storedSessionId)
      return
    }
    
    // If no stored session, create a new one
    createNewSession().catch(() => {
      // Error already handled in createNewSession
    })
  }, [])

  return (
    <SessionContext.Provider 
      value={{ 
        sessionId, 
        loading, 
        error, 
        createNewSession, 
        clearSession 
      }}
    >
      {children}
    </SessionContext.Provider>
  )
}

export function useSession() {
  const context = useContext(SessionContext)
  if (context === undefined) {
    throw new Error('useSession must be used within a SessionProvider')
  }
  return context
}

