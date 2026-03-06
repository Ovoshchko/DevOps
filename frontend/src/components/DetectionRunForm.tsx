import React from 'react'

type Props = {
  detectors: any[]
  selectedDetectorId: string
  onChangeDetector: (detectorId: string) => void
  onRun: (payload: any) => Promise<void> | void
}

export function DetectionRunForm({ detectors, selectedDetectorId, onChangeDetector, onRun }: Props) {
  const hasDetectors = detectors.length > 0

  return (
    <div className="panel">
      <h3>Detection run</h3>
      <p className="small">Start anomaly detection for a selected detector and last one minute window.</p>
      <label>
        Detector
        <select
          value={selectedDetectorId}
          onChange={(event) => onChangeDetector(event.target.value)}
          disabled={!hasDetectors}
        >
          {hasDetectors ? null : <option value="">No detectors available</option>}
          {detectors.map((detector) => (
            <option key={detector.id} value={detector.id}>
              {detector.name} ({detector.status})
            </option>
          ))}
        </select>
      </label>
      <button
        className="primary"
        onClick={() =>
          onRun({
            detector_config_id: selectedDetectorId,
            window_start: new Date(Date.now() - 60000).toISOString(),
            window_end: new Date().toISOString(),
          })
        }
        type="button"
        disabled={!selectedDetectorId}
        style={{ marginTop: '12px' }}
      >
        Run detection
      </button>
    </div>
  )
}
