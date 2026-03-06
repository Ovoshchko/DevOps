import React, { FormEvent, useMemo, useState } from 'react'
import { TrafficGeneratorConfig } from '../types/generator'

type Props = {
  config: TrafficGeneratorConfig
  onChange: (next: TrafficGeneratorConfig) => void
  onStart: () => void
  disabled: boolean
}

export function TrafficGeneratorForm({ config, onChange, onStart, disabled }: Props) {
  const [validationError, setValidationError] = useState<string | undefined>()

  const isInvalid = useMemo(() => {
    if (config.batchSize <= 0) return 'Batch size must be greater than 0'
    if (config.intervalMs < 250) return 'Interval must be at least 250 ms'
    if (config.durationSeconds <= 0) return 'Duration must be greater than 0'
    if (config.bytesMin <= 0 || config.bytesMax <= 0) return 'Metric range must be positive'
    return undefined
  }, [config])

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (isInvalid) {
      setValidationError(isInvalid)
      return
    }
    setValidationError(undefined)
    onStart()
  }

  const update = <K extends keyof TrafficGeneratorConfig>(key: K, value: TrafficGeneratorConfig[K]) => {
    onChange({ ...config, [key]: value })
  }

  return (
    <form className="panel" onSubmit={submit}>
      <h3>Traffic Generator</h3>
      <p className="small">Generate synthetic traffic and send it to ingest.</p>

      {validationError ? <div className="error-banner">{validationError}</div> : null}

      <div className="form-grid">
        <label>
          Profile name
          <input
            value={config.profileName}
            onChange={(event) => update('profileName', event.target.value)}
            required
          />
        </label>
        <label>
          Source prefix
          <input
            value={config.sourcePrefix}
            onChange={(event) => update('sourcePrefix', event.target.value)}
            required
          />
        </label>
        <label>
          Batch size
          <input
            aria-label="Batch size"
            type="number"
            min={1}
            value={config.batchSize}
            onChange={(event) => update('batchSize', Number(event.target.value))}
            required
          />
        </label>
        <label>
          Interval (ms)
          <input
            aria-label="Interval"
            type="number"
            min={250}
            step={250}
            value={config.intervalMs}
            onChange={(event) => update('intervalMs', Number(event.target.value))}
            required
          />
        </label>
        <label>
          Duration (sec)
          <input
            aria-label="Duration"
            type="number"
            min={1}
            value={config.durationSeconds}
            onChange={(event) => update('durationSeconds', Number(event.target.value))}
            required
          />
        </label>
        <label>
          Bytes min
          <input
            aria-label="Bytes min"
            type="number"
            min={1}
            value={config.bytesMin}
            onChange={(event) => update('bytesMin', Number(event.target.value))}
            required
          />
        </label>
        <label>
          Bytes max
          <input
            aria-label="Bytes max"
            type="number"
            min={1}
            value={config.bytesMax}
            onChange={(event) => update('bytesMax', Number(event.target.value))}
            required
          />
        </label>
      </div>

      <div style={{ marginTop: '12px' }}>
        <button className="primary" type="submit" disabled={disabled}>
          Start
        </button>
      </div>
    </form>
  )
}
