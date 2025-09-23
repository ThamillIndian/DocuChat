"use client"

import { useState } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "./ui/card"
import { Button } from "./ui/button"
import { Progress } from "./ui/progress"
import UploadPanel from "./upload-panel"
import { postJson, HttpError } from "@/lib/api"
import { useSession } from "@/contexts/session-context"

export default function SummaryPanel() {
  const [loading, setLoading] = useState(false)
  const [summary, setSummary] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [progress, setProgress] = useState(0)
  const { sessionId, loading: sessionLoading, error: sessionError, createNewSession, clearSession } = useSession()

  async function handleSummarize() {
    try {
      setError(null)
      setLoading(true)
      setProgress(10)
      if (!sessionId) throw new Error("No session yet")
      
      // Simulate progress steps
      const progressSteps = [25, 50, 75, 90]
      for (const step of progressSteps) {
        await new Promise(resolve => setTimeout(resolve, 200))
        setProgress(step)
      }
      
      let data = await postJson<{ summary: string; sources: string[] }>(
        "/summarize",
        { session_id: sessionId, mode: "executive" },
      )
      setProgress(100)
      setSummary(data.summary)
    } catch (e: any) {
      if (e instanceof HttpError && e.status === 404) {
        try {
          const newId = await createNewSession()
          const data = await postJson<{ summary: string; sources: string[] }>(
            "/summarize",
            { session_id: newId, mode: "executive" },
          )
          setProgress(100)
          setSummary(data.summary)
          return
        } catch (ee: any) {
          setError(ee?.message || "Something went wrong")
          return
        }
      }
      setError(e?.message || "Something went wrong")
    } finally {
      setLoading(false)
      setTimeout(() => setProgress(0), 1000) // Reset progress after 1 second
    }
  }

  async function handleNewSession() {
    try {
      await createNewSession()
      setSummary(null)
      setError(null)
    } catch (e) {
      console.error('Failed to create new session:', e)
    }
  }

  return (
    <Card aria-label="Summary panel" className="h-full">
      <CardHeader>
        <CardTitle className="text-pretty">Summary</CardTitle>
        {/* Session Status */}
        <div className="text-xs text-muted-foreground">
          {sessionLoading ? (
            "Creating session..."
          ) : sessionError ? (
            <span className="text-red-500">Session error: {sessionError}</span>
          ) : sessionId ? (
            `Session: ${sessionId.slice(0, 8)}...`
          ) : (
            "No session"
          )}
        </div>
      </CardHeader>

      {/* Make the inside scrollable while the page remains static */}
      <CardContent className="flex h-full min-h-0 flex-col gap-4 overflow-hidden">
        <div className="flex-1 min-h-0 overflow-y-auto space-y-4">
          <UploadPanel embedded />
          
          {/* Summary Content */}
          {summary && (
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-green-500"></div>
                <h3 className="text-sm font-medium text-muted-foreground">Executive Summary</h3>
              </div>
              <div className="rounded-lg border bg-card p-4">
                <div className="text-sm whitespace-pre-wrap leading-relaxed text-foreground">
                  {summary}
                </div>
              </div>
            </div>
          )}

          {/* Loading State */}
          {loading && (
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-blue-500 animate-pulse"></div>
                <h3 className="text-sm font-medium text-muted-foreground">Generating Summary</h3>
              </div>
              <div className="rounded-lg border bg-card p-4">
                <div className="space-y-3">
                  <Progress value={progress} className="h-2" />
                  <div className="text-xs text-muted-foreground text-center">
                    {progress < 25 && "Analyzing documents..."}
                    {progress >= 25 && progress < 50 && "Extracting key points..."}
                    {progress >= 50 && progress < 75 && "Structuring content..."}
                    {progress >= 75 && progress < 100 && "Finalizing summary..."}
                    {progress === 100 && "Complete!"}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-3 dark:border-red-800 dark:bg-red-950">
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-red-500"></div>
              <span className="text-sm font-medium text-red-700 dark:text-red-300">Error</span>
            </div>
            <p className="mt-1 text-sm text-red-600 dark:text-red-400">{error}</p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-2 pt-2">
          <Button 
            onClick={handleSummarize} 
            disabled={loading || !sessionId} 
            aria-busy={loading} 
            className="flex-1"
          >
            {loading ? (
              <div className="flex items-center gap-2">
                <div className="h-3 w-3 animate-spin rounded-full border-2 border-current border-t-transparent"></div>
                Generating...
              </div>
            ) : (
              "Generate Summary"
            )}
          </Button>
          <Button 
            onClick={handleNewSession} 
            variant="outline" 
            disabled={sessionLoading || loading}
            className="text-xs"
          >
            {sessionLoading ? "..." : "New Session"}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
