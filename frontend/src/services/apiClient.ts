export async function apiRequest<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, init)
  if (!res.ok) {
    let msg = `Request failed: ${res.status}`
    try {
      const body = await res.json() as { error?: string }
      if (body.error) msg = body.error
    } catch {
      // ignore non-json errors
    }
    throw new Error(msg)
  }
  if (res.status === 204) return undefined as T
  return res.json() as Promise<T>
}
