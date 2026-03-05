import React from 'react'

export function DetectionRunForm({ onRun }: { onRun: (payload: any) => void }) {
  return (
    <button onClick={() => onRun({ detector_config_id: 'demo', window_start: new Date(Date.now() - 60000).toISOString(), window_end: new Date().toISOString() })}>
      Run detection
    </button>
  )
}
