import React, { FormEvent, useState } from 'react'

import { DetectorPayload } from '../services/detectorsApi'

type Props = {
  onSubmit: (v: DetectorPayload) => Promise<void> | void
}

export function DetectorForm({ onSubmit }: Props) {
  const [name, setName] = useState('Default detector')
  const [description, setDescription] = useState('Detects traffic spikes in rolling windows')
  const [sensitivity, setSensitivity] = useState(0.7)
  const [windowSize, setWindowSize] = useState(60)
  const [windowStep, setWindowStep] = useState(30)
  const [featuresRaw, setFeaturesRaw] = useState('bytes_per_sec, packets_per_sec')
  const [status, setStatus] = useState<'draft' | 'active' | 'archived'>('active')

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const features = featuresRaw
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean)

    await onSubmit({
      name,
      description,
      sensitivity,
      window_size_seconds: windowSize,
      window_step_seconds: windowStep,
      features: features.length > 0 ? features : ['bytes_per_sec'],
      status,
    })
  }

  return (
    <form className="panel" onSubmit={handleSubmit}>
      <h3>Create detector</h3>
      <div className="form-grid">
        <label>
          Detector name
          <input value={name} onChange={(event) => setName(event.target.value)} required minLength={3} />
        </label>
        <label>
          Status
          <select value={status} onChange={(event) => setStatus(event.target.value as typeof status)}>
            <option value="draft">Draft</option>
            <option value="active">Active</option>
            <option value="archived">Archived</option>
          </select>
        </label>
        <label>
          Description
          <input
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            maxLength={180}
            required
          />
        </label>
        <label>
          Sensitivity (0.1 - 1.0)
          <input
            type="number"
            min={0.1}
            max={1}
            step={0.05}
            value={sensitivity}
            onChange={(event) => setSensitivity(Number(event.target.value))}
            required
          />
        </label>
        <label>
          Window size (seconds)
          <input
            type="number"
            min={10}
            max={3600}
            step={10}
            value={windowSize}
            onChange={(event) => setWindowSize(Number(event.target.value))}
            required
          />
        </label>
        <label>
          Window step (seconds)
          <input
            type="number"
            min={5}
            max={900}
            step={5}
            value={windowStep}
            onChange={(event) => setWindowStep(Number(event.target.value))}
            required
          />
        </label>
        <label>
          Features (comma-separated)
          <input
            value={featuresRaw}
            onChange={(event) => setFeaturesRaw(event.target.value)}
            placeholder="bytes_per_sec, packets_per_sec, latency_ms"
            required
          />
        </label>
      </div>
      <div style={{ marginTop: '12px' }}>
        <button className="primary" type="submit">
          Save detector
        </button>
      </div>
    </form>
  )
}
