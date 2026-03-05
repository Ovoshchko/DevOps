import { apiRequest } from './apiClient'

const BASE = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000'

export const detectionsApi = {
  run: (payload: any) => apiRequest<any>(`${BASE}/detections/run`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }),
  list: () => apiRequest<any[]>(`${BASE}/detections`),
  get: (id: string) => apiRequest<any>(`${BASE}/detections/${id}`)
}
