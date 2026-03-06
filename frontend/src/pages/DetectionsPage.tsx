import React, { useEffect, useState } from 'react'

import { DetectionResultsTable } from '../components/DetectionResultsTable'
import { DetectionRunForm } from '../components/DetectionRunForm'
import { ErrorBanner } from '../components/ErrorBanner'
import { toUserMessage } from '../services/apiClient'
import { detectionsApi } from '../services/detectionsApi'
import { detectorsApi } from '../services/detectorsApi'

export function DetectionsPage() {
  const [runs, setRuns] = useState<any[]>([])
  const [detectors, setDetectors] = useState<any[]>([])
  const [selectedDetectorId, setSelectedDetectorId] = useState<string>('')
  const [error, setError] = useState<string>()

  const reloadRuns = async () => {
    try {
      const items = await detectionsApi.list(selectedDetectorId || undefined)
      setRuns(items)
      setError(undefined)
    } catch (err) {
      setError(toUserMessage(err))
      setRuns([])
    }
  }

  const reloadDetectors = async () => {
    try {
      const listed = await detectorsApi.list()
      setDetectors(listed)
      if (!selectedDetectorId && listed.length > 0) {
        const preferred = listed.find((item) => item.status === 'active') ?? listed[0]
        setSelectedDetectorId(preferred.id)
      }
    } catch (err) {
      setError(toUserMessage(err))
      setDetectors([])
    }
  }

  const run = async (payload: any) => {
    try {
      await detectionsApi.run(payload)
      await reloadRuns()
    } catch (err) {
      setError(toUserMessage(err))
    }
  }

  useEffect(() => {
    void reloadDetectors()
  }, [])

  useEffect(() => {
    void reloadRuns()
  }, [selectedDetectorId])

  const selectedDetector = detectors.find((detector) => detector.id === selectedDetectorId)

  return (
    <main>
      <h2>Detections</h2>
      <ErrorBanner error={error} />
      <DetectionRunForm
        detectors={detectors}
        selectedDetectorId={selectedDetectorId}
        onChangeDetector={setSelectedDetectorId}
        onRun={run}
      />
      <section className="panel">
        <p className="small">
          Active detector: {selectedDetector?.name ?? 'not selected'} {selectedDetectorId ? `(${selectedDetectorId})` : ''}
        </p>
      </section>
      <DetectionResultsTable results={runs} />
    </main>
  )
}
