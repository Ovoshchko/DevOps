import React from 'react'

export function LatestAnomaliesWidget({ results }: { results: any[] }) {
  return (
    <section className="panel">
      <h3>Latest Anomalies</h3>
      <p className="small">Recent results: {results.length}</p>
      {results.length > 0 ? (
        <ul>
          {results.slice(0, 5).map((result) => (
            <li key={result.id}>
              {result.id} - score {result.anomaly_score} - anomaly {String(result.is_anomaly)}
            </li>
          ))}
        </ul>
      ) : (
        <p className="small">No anomaly results yet.</p>
      )}
    </section>
  )
}
