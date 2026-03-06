const API_BASE = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000'

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
  }
}

export function toUserMessage(error: unknown): string {
  if (error instanceof ApiError) return error.message
  if (error instanceof Error) return error.message
  return 'Unexpected error. Please try again.'
}

export async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  const res = await fetch(`${API_BASE}${normalizedPath}`, init)

  if (!res.ok) {
    let msg = `Request failed: ${res.status}`
    try {
      const body = (await res.json()) as { error?: string; detail?: string; message?: string }
      msg = body.error || body.detail || body.message || msg
    } catch {
      // keep fallback
    }
    throw new ApiError(res.status, msg)
  }

  if (res.status === 204) {
    return undefined as T
  }

  return res.json() as Promise<T>
}
