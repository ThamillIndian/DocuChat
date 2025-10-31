"use client"

import React, { createContext, useContext, useEffect, useState } from 'react'
import { createSession } from '@/lib/api'

const SESSION_STORAGE_KEY = 'summarizer_session_id'
const SESSION_TIMESTAMP_KEY = 'summarizer_session_timestamp'
const SESSION_MAX_AGE_MS = 2 * 60 * 60 * 1000 // 2 hours

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
      localStorage.setItem(SESSION_TIMESTAMP_KEY, Date.now().toString())
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
    localStorage.removeItem(SESSION_TIMESTAMP_KEY)
  }

  // Load session from localStorage on mount, or create new one
  useEffect(() => {
    // Try to load existing session from localStorage
    const storedSessionId = localStorage.getItem(SESSION_STORAGE_KEY)
    const storedTimestamp = localStorage.getItem(SESSION_TIMESTAMP_KEY)
    
    if (storedSessionId && storedTimestamp) {
      const sessionAge = Date.now() - parseInt(storedTimestamp, 10)
      
      // Check if session is still valid (not expired)
      if (sessionAge < SESSION_MAX_AGE_MS) {
        console.log('📦 Loaded existing session:', storedSessionId.slice(0, 8), `(${Math.round(sessionAge / 1000 / 60)}min old)`)
        setSessionId(storedSessionId)
        return
      } else {
        console.log('⏰ Session expired, creating new one')
        clearSession()
      }
    }
    
    // If no stored session or expired, create a new one
    console.log('🆕 Creating new session...')
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

