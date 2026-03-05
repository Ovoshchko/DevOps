import React, { useEffect, useState } from 'react'
import { monitoringApi } from '../services/monitoringApi'
import { LatestTrafficWidget } from '../components/LatestTrafficWidget'
import { LatestAnomaliesWidget } from '../components/LatestAnomaliesWidget'

export function MonitoringPage() {
  const [points, setPoints] = useState<any[]>([])
  const [results, setResults] = useState<any[]>([])
  useEffect(() => {
    monitoringApi.latestTraffic().then((r) => setPoints(r.points)).catch(() => setPoints([]))
    monitoringApi.latestAnomalies().then((r) => setResults(r.results)).catch(() => setResults([]))
  }, [])
  return (
    <main>
      <h2>Monitoring</h2>
      <LatestTrafficWidget points={points} />
      <LatestAnomaliesWidget results={results} />
    </main>
  )
}
