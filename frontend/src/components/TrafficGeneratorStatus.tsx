import React from 'react'
import { GeneratorRunState } from '../types/generator'

type Props = {
  runState: GeneratorRunState
  onStop: () => void
  onRetry: () => void
}

export function TrafficGeneratorStatus({ runState, onStop, onRetry }: Props) {
  const progress =
    runState.totalBatches > 0
      ? `${runState.sentBatches}/${runState.totalBatches} batches`
      : 'No batches sent yet'

  return (
    <section className="panel">
      <h3>Generator Status</h3>
      <p className="small">State: {runState.state}</p>
      <p className="small">Progress: {progress}</p>
      <p className="small">Accepted points in last send: {runState.acceptedPoints}</p>
      {runState.lastError ? <div className="error-banner">{runState.lastError}</div> : null}
      <div style={{ display: 'flex', gap: '8px', marginTop: '10px' }}>
        <button type="button" onClick={onStop} disabled={runState.state !== 'running'}>
          Stop
        </button>
        <button type="button" onClick={onRetry} disabled={runState.state === 'running'}>
          Retry
        </button>
      </div>
    </section>
  )
}
