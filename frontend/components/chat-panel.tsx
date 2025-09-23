"use client"

import { useEffect, useRef, useState } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "./ui/card"
import { Button } from "./ui/button"
import { Textarea } from "./ui/textarea"
import { streamSSE, HttpError } from "@/lib/api"
import { useSession } from "@/contexts/session-context"

type Msg = { id: string; role: "user" | "assistant"; content: string; isStreaming?: boolean }

export default function ChatPanel() {
  const [messages, setMessages] = useState<Msg[]>([
    {
      id: crypto.randomUUID(),
      role: "assistant",
      content: "Welcome! Upload documents on the left and ask questions here.",
    },
  ])
  const [input, setInput] = useState("")
  const listRef = useRef<HTMLDivElement | null>(null)
  const { sessionId, loading: sessionLoading, error: sessionError, createNewSession } = useSession()

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" })
  }, [messages])

  const send = async () => {
    const trimmed = input.trim()
    if (!trimmed) return
    const userMsg: Msg = { id: crypto.randomUUID(), role: "user", content: trimmed }
    setMessages((prev) => [...prev, userMsg])
    setInput("")

    const replyId = crypto.randomUUID()
    setMessages((prev) => [...prev, { id: replyId, role: "assistant", content: "", isStreaming: true }])
    if (!sessionId) {
      setMessages((prev) =>
        prev.map((m) => (m.id === replyId ? { ...m, content: "No session yet. Upload a file first." } : m)),
      )
      return
    }

    try {
      await streamSSE(
        "/chat/conversational",
        { session_id: sessionId, message: trimmed, k: 8, max_ctx: 6000 },
        ({ event, data }) => {
          if (event === "meta") return
          if (event === "done") {
            setMessages((prev) =>
              prev.map((m) => (m.id === replyId ? { ...m, isStreaming: false } : m)),
            )
            return
          }
          if (data) {
            setMessages((prev) =>
              prev.map((m) => (m.id === replyId ? { ...m, content: m.content + data } : m)),
            )
          }
        },
      )
    } catch (e: any) {
      if (e instanceof HttpError && e.status === 404) {
        try {
          const newId = await createNewSession()
          await streamSSE(
            "/chat/conversational",
            { session_id: newId, message: trimmed, k: 8, max_ctx: 6000 },
            ({ event, data }) => {
              if (event === "meta") return
              if (event === "done") {
                setMessages((prev) =>
                  prev.map((m) => (m.id === replyId ? { ...m, isStreaming: false } : m)),
                )
                return
              }
              if (data) {
                setMessages((prev) =>
                  prev.map((m) => (m.id === replyId ? { ...m, content: m.content + data } : m)),
                )
              }
            },
          )
          return
        } catch (ee: any) {
          setMessages((prev) => prev.map((m) => (m.id === replyId ? { ...m, content: ee?.message || "Error", isStreaming: false } : m)))
          return
        }
      }
      setMessages((prev) => prev.map((m) => (m.id === replyId ? { ...m, content: e?.message || "Error", isStreaming: false } : m)))
    }
  }

  return (
    <Card aria-label="Chat panel" className="h-full">
      <CardHeader>
        <CardTitle className="text-pretty">Chat</CardTitle>
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
      <CardContent className="flex h-full min-h-0 flex-col gap-3">
        <div ref={listRef} className="flex-1 overflow-y-auto rounded-md border p-4 space-y-4" aria-live="polite">
          {messages.map((m) => (
            <div key={m.id} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-[80%] rounded-lg px-4 py-3 ${
                m.role === "user" 
                  ? "bg-primary text-primary-foreground" 
                  : "bg-muted text-muted-foreground"
              }`}>
                <div className="text-xs font-medium mb-1 opacity-70">
                  {m.role === "user" ? "You" : "Assistant"}
                  {m.isStreaming && m.role === "assistant" && (
                    <span className="ml-2 text-xs opacity-50">● typing...</span>
                  )}
                </div>
                <div className="text-sm whitespace-pre-wrap leading-relaxed">
                  {m.content}
                  {m.isStreaming && m.role === "assistant" && (
                    <span className="inline-block w-2 h-4 bg-current opacity-50 animate-pulse ml-1" />
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="flex flex-col gap-2">
          <label htmlFor="chat-input" className="sr-only">
            Message
          </label>
          <Textarea
            id="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            rows={3}
            placeholder="Ask a question about your documents..."
          />
          <div className="flex items-center justify-end">
            <Button onClick={send} aria-label="Send message">
              Send
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
