import { apiRequest } from './apiClient'

const BASE = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000'

export const monitoringApi = {
  ingest: (points: any[]) => apiRequest<{ accepted: number }>(`${BASE}/traffic/ingest`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ points }) }),
  latestTraffic: () => apiRequest<{ points: any[] }>(`${BASE}/traffic/latest`),
  latestAnomalies: () => apiRequest<{ results: any[] }>(`${BASE}/anomalies/latest`)
}
