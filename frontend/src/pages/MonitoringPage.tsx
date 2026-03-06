import React, { useEffect, useMemo, useState } from 'react'

import { ErrorBanner } from '../components/ErrorBanner'
import { LatestAnomaliesWidget } from '../components/LatestAnomaliesWidget'
import { LatestTrafficWidget } from '../components/LatestTrafficWidget'
import { monitoringApi } from '../services/monitoringApi'
import { toUserMessage } from '../services/apiClient'

export function MonitoringPage() {
  const [points, setPoints] = useState<any[]>([])
  const [results, setResults] = useState<any[]>([])
  const [detectorId, setDetectorId] = useState<string>('')
  const [error, setError] = useState<string>()

  const refresh = async (profileId?: string) => {
    try {
      const [trafficData, anomalyData] = await Promise.all([
        monitoringApi.latestTraffic(),
        monitoringApi.latestAnomalies(profileId),
      ])
      setPoints(trafficData.points)
      setResults(anomalyData.results)
      setError(undefined)
    } catch (err) {
      setError(toUserMessage(err))
    }
  }

  useEffect(() => {
    void refresh(detectorId || undefined)
  }, [detectorId])

  const statusLabel = useMemo(
    () => `Traffic points: ${points.length}, anomalies: ${results.length}`,
    [points.length, results.length],
  )
  const latestTimestamp = useMemo(() => {
    if (points.length === 0) return 'No recent traffic'
    const stamp = points[0]?.timestamp
    if (!stamp) return 'No timestamp'
    return `Last point: ${new Date(stamp).toLocaleString()}`
  }, [points])

  return (
    <main>
      <h2>Monitoring</h2>
      <ErrorBanner error={error} />
      <section className="panel">
        <h3>Live filter</h3>
        <label>
          Active detector profile id
          <input
            placeholder="optional detector id"
            value={detectorId}
            onChange={(event) => setDetectorId(event.target.value)}
          />
        </label>
        <div style={{ marginTop: '12px', display: 'flex', gap: '8px' }}>
          <button type="button" onClick={() => void refresh(detectorId || undefined)}>
            Refresh now
          </button>
        </div>
        <p className="small" style={{ marginTop: '8px' }}>
          {latestTimestamp}
        </p>
      </section>
      <section className="page-grid-two">
        <LatestTrafficWidget points={points} />
        <LatestAnomaliesWidget results={results} />
      </section>
      <section className="panel">
        <p className="small">{statusLabel}</p>
      </section>
    </main>
  )
}
