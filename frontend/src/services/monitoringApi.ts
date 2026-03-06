import { apiRequest } from './apiClient'
import { TrafficPoint } from '../types/generator'

export const monitoringApi = {
  ingest: (points: TrafficPoint[]) =>
    apiRequest<{ accepted: number }>('/traffic/ingest', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ points }),
    }),
  latestTraffic: () => apiRequest<{ points: any[] }>('/traffic/latest'),
  latestAnomalies: (detectorProfileId?: string) =>
    apiRequest<{ results: any[] }>(
      detectorProfileId
        ? `/anomalies/latest?detector_profile_id=${encodeURIComponent(detectorProfileId)}`
        : '/anomalies/latest',
    ),
}
