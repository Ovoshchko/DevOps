import React, { useEffect, useState } from 'react'

import { DetectionResultsTable } from '../components/DetectionResultsTable'
import { DetectionRunForm } from '../components/DetectionRunForm'
import { ErrorBanner } from '../components/ErrorBanner'
import { toUserMessage } from '../services/apiClient'
import { detectionsApi } from '../services/detectionsApi'

export function DetectionsPage() {
  const [runs, setRuns] = useState<any[]>([])
  const [error, setError] = useState<string>()

  const reload = async () => {
    try {
      const items = await detectionsApi.list()
      setRuns(items)
      setError(undefined)
    } catch (err) {
      setError(toUserMessage(err))
      setRuns([])
    }
  }

  const run = async (payload: any) => {
    try {
      await detectionsApi.run(payload)
      await reload()
    } catch (err) {
      setError(toUserMessage(err))
    }
  }

  useEffect(() => {
    void reload()
  }, [])

  return (
    <main>
      <h2>Detections</h2>
      <ErrorBanner error={error} />
      <DetectionRunForm onRun={run} />
      <DetectionResultsTable results={runs} />
    </main>
  )
}
