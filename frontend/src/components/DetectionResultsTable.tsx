import React from 'react'

export function DetectionResultsTable({ results }: { results: any[] }) {
  return (
    <table>
      <thead><tr><th>ID</th><th>Score</th><th>Anomaly</th></tr></thead>
      <tbody>
        {results.map((r) => <tr key={r.id}><td>{r.id}</td><td>{r.anomaly_score}</td><td>{String(r.is_anomaly)}</td></tr>)}
      </tbody>
    </table>
  )
}
