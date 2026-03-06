import React from 'react'

export function DetectionResultsTable({ results }: { results: any[] }) {
  const formatDate = (value: string | undefined) => {
    if (!value) return '-'
    const date = new Date(value)
    return Number.isNaN(date.getTime()) ? value : date.toLocaleString()
  }

  const formatFeatures = (value: unknown) => {
    if (!Array.isArray(value) || value.length === 0) return '-'
    return value.join(', ')
  }

  return (
    <section className="panel">
      <h3>Detection runs</h3>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Detector</th>
            <th>Status</th>
            <th>Window</th>
            <th>Threshold</th>
            <th>Features</th>
            <th>Anomaly</th>
          </tr>
        </thead>
        <tbody>
          {results.map((r) => (
            <tr key={r.id}>
              <td>{r.id}</td>
              <td>{r.detector_config_id ?? '-'}</td>
              <td>{r.status}</td>
              <td>
                {formatDate(r.window_start)} - {formatDate(r.window_end)}
              </td>
              <td>{r.summary?.threshold ?? '-'}</td>
              <td>{formatFeatures(r.summary?.features)}</td>
              <td>{typeof r.summary?.is_anomaly === 'boolean' ? String(r.summary.is_anomaly) : '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  )
}
