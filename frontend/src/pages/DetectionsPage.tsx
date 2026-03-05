import React, { useEffect, useState } from 'react'
import { detectionsApi } from '../services/detectionsApi'
import { DetectionRunForm } from '../components/DetectionRunForm'
import { DetectionResultsTable } from '../components/DetectionResultsTable'

export function DetectionsPage() {
  const [results, setResults] = useState<any[]>([])
  const reload = () => detectionsApi.list().then(setResults).catch(() => setResults([]))
  useEffect(() => { reload() }, [])
  return (
    <main>
      <h2>Detections</h2>
      <DetectionRunForm onRun={(payload) => detectionsApi.run(payload).then(reload)} />
      <DetectionResultsTable results={results} />
    </main>
  )
}
