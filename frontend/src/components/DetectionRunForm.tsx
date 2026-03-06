import React from 'react'

export function DetectionRunForm({ onRun }: { onRun: (payload: any) => Promise<void> | void }) {
  return (
    <div className="panel">
      <h3>Detection run</h3>
      <p className="small">Start anomaly detection for the last one minute window.</p>
      <button
        className="primary"
        onClick={() =>
          onRun({
            detector_config_id: 'demo',
            window_start: new Date(Date.now() - 60000).toISOString(),
            window_end: new Date().toISOString(),
          })
        }
        type="button"
      >
        Run detection
      </button>
    </div>
  )
}
