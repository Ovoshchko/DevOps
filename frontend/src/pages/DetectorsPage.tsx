import React, { useEffect, useState } from 'react'

import { DetectorForm } from '../components/DetectorForm'
import { ErrorBanner } from '../components/ErrorBanner'
import { toUserMessage } from '../services/apiClient'
import { DetectorPayload, detectorsApi } from '../services/detectorsApi'

export function DetectorsPage() {
  const [items, setItems] = useState<any[]>([])
  const [error, setError] = useState<string>()

  const reload = async () => {
    try {
      const listed = await detectorsApi.list()
      setItems(listed)
      setError(undefined)
    } catch (err) {
      setError(toUserMessage(err))
      setItems([])
    }
  }

  const create = async (payload: DetectorPayload) => {
    try {
      await detectorsApi.create(payload)
      await reload()
    } catch (err) {
      setError(toUserMessage(err))
    }
  }

  const archive = async (id: string) => {
    try {
      await detectorsApi.remove(id)
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
      <h2>Detectors</h2>
      <ErrorBanner error={error} />
      <DetectorForm onSubmit={create} />
      <section className="panel">
        <h3>Configured detectors</h3>
        {items.length === 0 ? <p className="small">No detectors created yet.</p> : null}
        <ul>
          {items.map((detector) => (
            <li key={detector.id}>
              <strong>{detector.name}</strong> ({detector.status}){' '}
              <span className="small">
                sensitivity: {detector.sensitivity ?? '-'}, window: {detector.window_size_seconds ?? '-'}s /{' '}
                {detector.window_step_seconds ?? '-'}s, features: {(detector.features ?? []).join(', ') || '-'}
              </span>{' '}
              <button type="button" onClick={() => archive(detector.id)}>
                Archive
              </button>
            </li>
          ))}
        </ul>
      </section>
    </main>
  )
}
