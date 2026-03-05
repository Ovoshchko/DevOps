import { apiRequest } from './apiClient'

const BASE = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000'

export const detectorsApi = {
  list: () => apiRequest<any[]>(`${BASE}/detectors`),
  create: (payload: any) => apiRequest<any>(`${BASE}/detectors`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }),
  update: (id: string, payload: any) => apiRequest<any>(`${BASE}/detectors/${id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }),
  remove: (id: string) => apiRequest<void>(`${BASE}/detectors/${id}`, { method: 'DELETE' })
}
