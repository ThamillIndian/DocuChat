export function getBackendBaseUrl(): string {
  if (typeof window !== 'undefined') {
    const fromEnv = (window as any).ENV_BACKEND_URL as string | undefined
    if (fromEnv) return stripTrailingSlash(fromEnv)
  }
  const env = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
  return stripTrailingSlash(env)
}

function stripTrailingSlash(url: string): string {
  return url.endsWith('/') ? url.slice(0, -1) : url
}

export class HttpError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function throwForNonOk(res: Response) {
  if (!res.ok) {
    const msg = await safeText(res)
    throw new HttpError(res.status, msg)
  }
}

export async function createSession(): Promise<string> {
  const base = getBackendBaseUrl()
  const res = await fetch(`${base}/session/new`, { method: 'POST' })
  await throwForNonOk(res)
  const data = await res.json()
  return data.session_id as string
}

export async function postJson<T>(path: string, payload: unknown, init?: RequestInit): Promise<T> {
  const base = getBackendBaseUrl()
  const res = await fetch(`${base}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...(init?.headers || {}) },
    body: JSON.stringify(payload),
    ...init,
  })
  await throwForNonOk(res)
  return (await res.json()) as T
}

async function safeText(res: Response): Promise<string> {
  try { return await res.text() } catch { return `${res.status}` }
}

export async function uploadFiles(sessionId: string, files: File[]): Promise<any> {
  const base = getBackendBaseUrl()
  const form = new FormData()
  for (const f of files) form.append('files', f)
  const res = await fetch(`${base}/session/${sessionId}/upload`, { method: 'POST', body: form })
  await throwForNonOk(res)
  return await res.json()
}

export type SseHandler = (event: { event?: string; data?: string }) => void

export async function streamSSE(path: string, payload: unknown, onMessage: SseHandler) {
  const base = getBackendBaseUrl()
  const res = await fetch(`${base}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) {
    const msg = await safeText(res)
    throw new HttpError(res.status, msg)
  }
  if (!res.body) throw new Error('Failed to start stream')
  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    let idx
    while ((idx = buffer.indexOf('\n\n')) !== -1) {
      const chunk = buffer.slice(0, idx)
      buffer = buffer.slice(idx + 2)
      const lines = chunk.split('\n')
      const ev: { event?: string; data?: string } = {}
      for (const line of lines) {
        if (line.startsWith('event:')) ev.event = line.slice(6).trim()
        else if (line.startsWith('data:')) ev.data = (ev.data || '') + line.slice(5)
      }
      onMessage(ev)
    }
  }
}


