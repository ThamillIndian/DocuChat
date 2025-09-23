"use client"

import { useRef, useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "./ui/card"
import { Button } from "./ui/button"
import { Input } from "./ui/input"
import { Progress } from "./ui/progress"
import { useSession } from "@/contexts/session-context"
import { uploadFiles, HttpError } from "@/lib/api"

type DocItem = {
  id: string
  name: string
  size: number
  status: "pending" | "uploaded"
}

function formatBytes(bytes: number) {
  if (bytes === 0) return "0 B"
  const k = 1024
  const sizes = ["B", "KB", "MB", "GB"]
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`
}

export default function UploadPanel({ embedded = false }: { embedded?: boolean }) {
  const inputRef = useRef<HTMLInputElement | null>(null)
  const [docs, setDocs] = useState<DocItem[]>([])
  const [isUploading, setIsUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const { sessionId, createNewSession } = useSession()

  const onPickFiles = () => {
    console.log('Upload button clicked!')
    console.log('inputRef.current:', inputRef.current)
    inputRef.current?.click()
  }

  useEffect(() => {
    console.log('Component mounted, inputRef:', inputRef.current)
  }, [])

  const onFiles = async (files: FileList | null) => {
    console.log('onFiles called with:', files)
    if (!files || files.length === 0) return
    if (!sessionId) {
      console.warn('No session yet')
      return
    }
    const items: DocItem[] = Array.from(files).map((f) => ({
      id: crypto.randomUUID(),
      name: f.name,
      size: f.size,
      status: "pending",
    }))
    setDocs((prev) => [...items, ...prev])
    setIsUploading(true)
    setProgress(5)
    try {
      await uploadFiles(sessionId, Array.from(files))
      setProgress(100)
      setDocs((prev) => prev.map((d) => ({ ...d, status: "uploaded" })))
    } catch (e) {
      console.error(e)
      // Auto-recover when session is missing
      if (e instanceof HttpError && e.status === 404) {
        try {
          const newId = await createNewSession()
          // Retry once
          await uploadFiles(newId, Array.from(files))
          setProgress(100)
          setDocs((prev) => prev.map((d) => ({ ...d, status: "uploaded" })))
        } catch (ee) {
          console.error(ee)
        }
      }
    } finally {
      setIsUploading(false)
    }
  }

  const onRemove = (id: string) => {
    setDocs((prev) => prev.filter((d) => d.id !== id))
  }

  // Factor the inner content so we can reuse for embedded mode
  const Content = () => (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-3">
        <Input
          ref={inputRef}
          type="file"
          accept=".pdf,.doc,.docx,.md,.txt,.csv,.json,.xml,.html,.htm,.py,.js,.css,.sql,.log,.pptx,.ppt,.png,.jpg,.jpeg,.mp3,.mp4,.m4a,.wav,.mov,.mkv,.aac,.aiff,.ogg,.opus,.flac,.amr,.wma,.webm"
          multiple
          onChange={(e) => onFiles(e.target.files)}
          className="hidden"
          aria-hidden="true"
          tabIndex={-1}
        />
        <Button 
          onClick={onPickFiles} 
          aria-label="Choose documents"
          className="cursor-pointer"
          style={{ pointerEvents: 'auto' }}
          onMouseDown={() => console.log('Button mouse down')}
          onMouseUp={() => console.log('Button mouse up')}
        >
          Choose files
        </Button>
        <p className="text-sm text-muted-foreground">
          Supported: Documents (PDF, DOCX, MD, TXT, CSV, JSON, XML, HTML), 
          Code (PY, JS, CSS, SQL), Audio/Video (MP3, MP4, WAV, MOV), 
          Images (PNG, JPG), Presentations (PPT, PPTX)
        </p>
      </div>

      {isUploading && (
        <div className="flex flex-col gap-2" aria-live="polite">
          <Progress value={progress} aria-label="Upload progress" />
          <span className="text-xs text-muted-foreground">Uploading... {progress}%</span>
        </div>
      )}

      <ul className="flex flex-col gap-2">
        {docs.length === 0 ? (
          <li className="text-sm text-muted-foreground">No documents uploaded yet.</li>
        ) : (
          docs.map((d) => (
            <li key={d.id} className="flex items-center justify-between rounded-md border p-2">
              <div className="min-w-0">
                <p className="truncate text-sm font-medium">{d.name}</p>
                <p className="text-xs text-muted-foreground">
                  {formatBytes(d.size)} · {d.status === "uploaded" ? "Ready" : "Pending"}
                </p>
              </div>
              <Button variant="ghost" size="sm" onClick={() => onRemove(d.id)} aria-label={`Remove ${d.name}`}>
                Remove
              </Button>
            </li>
          ))
        )}
      </ul>
    </div>
  )

  if (embedded) {
    return (
      <section aria-label="Upload" className="rounded-md border p-3">
        <h3 className="mb-2 text-sm font-semibold">Upload</h3>
        <Content />
      </section>
    )
  }

  return (
    <Card aria-label="Upload panel">
      <CardHeader>
        <CardTitle className="text-pretty">Upload</CardTitle>
      </CardHeader>
      <CardContent>
        <Content />
      </CardContent>
    </Card>
  )
}